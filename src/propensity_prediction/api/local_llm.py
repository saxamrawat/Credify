"""Optional, offline Hugging Face text-generation adapter."""

from __future__ import annotations

import json
import logging
import threading
import time
from pathlib import Path
from typing import Protocol

from propensity_prediction.api.errors import (
    AnalystModelUnavailable,
    AnalystProviderFailure,
    AnalystProviderTimeout,
)


logger = logging.getLogger(__name__)

EXPECTED_BASE_MODEL = "Qwen/Qwen3-8B"
EXPECTED_BASE_REVISION = "e8bbd8252970581ea5b08b6a5b3e668adaf3161a"


class StructuredGenerationProvider(Protocol):
    """Small seam between answer grounding and a concrete local model runtime."""

    @property
    def available(self) -> bool: ...

    def generate(self, messages: list[dict[str, str]]) -> str: ...


class LocalHuggingFaceProvider:
    """Load a local quantized base model with its local PEFT adapter."""

    MAX_INPUT_TOKENS = 8192
    MAX_NEW_TOKENS = 384
    MAX_GENERATION_SECONDS = 45

    def __init__(
        self,
        base_model_path: str | None,
        adapter_path: str | None,
    ) -> None:
        self.base_model_path = base_model_path
        self.adapter_path = adapter_path
        self._tokenizer = None
        self._model = None
        self._torch = None
        self._load_error: Exception | None = None
        self._generation_lock = threading.Lock()

    @property
    def available(self) -> bool:
        return self._model is not None and self._tokenizer is not None

    def load(self) -> bool:
        """Load only a local checkpoint; leave the API usable if unavailable."""
        if not self.base_model_path or not self.adapter_path:
            self._load_error = FileNotFoundError(
                "Both local base-model and adapter paths must be configured."
            )
            return False

        base_path = Path(self.base_model_path).expanduser().resolve()
        adapter_path = Path(self.adapter_path).expanduser().resolve()
        if not base_path.is_dir() or not (base_path / "config.json").is_file():
            self._load_error = FileNotFoundError(
                "The configured base-model path must contain a local config.json."
            )
            logger.warning("Local analyst base model is not available at the configured path.")
            return False
        if (
            not adapter_path.is_dir()
            or not (adapter_path / "adapter_config.json").is_file()
            or not (adapter_path / "adapter_model.safetensors").is_file()
        ):
            self._load_error = FileNotFoundError(
                "The configured adapter path must contain PEFT config and safetensors weights."
            )
            logger.warning("Local analyst adapter is not available at the configured path.")
            return False
        manifest_path = adapter_path.parent / "training_manifest.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            adapter_config = json.loads(
                (adapter_path / "adapter_config.json").read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            self._load_error = ValueError(
                "The adapter must include readable manifest and PEFT configuration files."
            )
            logger.warning("Local analyst adapter metadata is unavailable.")
            return False
        if (
            not isinstance(manifest, dict)
            or not isinstance(adapter_config, dict)
            or manifest.get("model_id") != EXPECTED_BASE_MODEL
            or manifest.get("model_revision") != EXPECTED_BASE_REVISION
            or adapter_config.get("base_model_name_or_path") != EXPECTED_BASE_MODEL
        ):
            self._load_error = ValueError(
                "The adapter manifest does not match the application's pinned base model."
            )
            logger.warning("Local analyst adapter does not match the pinned base model.")
            return False

        try:
            import torch
            from peft import PeftModel
            from transformers import (
                AutoModelForCausalLM,
                AutoTokenizer,
                BitsAndBytesConfig,
            )

            if not torch.cuda.is_available():
                raise RuntimeError(
                    "Qwen3-8B QLoRA inference requires a CUDA GPU; CPU loading is not supported."
                )

            compute_dtype = (
                torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
            )
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=compute_dtype,
            )

            self._tokenizer = AutoTokenizer.from_pretrained(
                base_path,
                local_files_only=True,
                trust_remote_code=False,
            )
            base_model = AutoModelForCausalLM.from_pretrained(
                base_path,
                local_files_only=True,
                trust_remote_code=False,
                use_safetensors=True,
                quantization_config=quantization_config,
                device_map="auto",
            )
            self._model = PeftModel.from_pretrained(
                base_model,
                adapter_path,
                local_files_only=True,
                is_trainable=False,
            )
            self._model.eval()
            self._torch = torch
            self._load_error = None
            logger.info("Loaded local quantized base model and PEFT adapter.")
            return True
        except Exception as exc:
            self._tokenizer = None
            self._model = None
            self._torch = None
            self._load_error = exc
            logger.exception("Could not load the configured local analyst model.")
            return False

    def generate(self, messages: list[dict[str, str]]) -> str:
        if not self.available:
            raise AnalystModelUnavailable(
                "No usable local language model is configured."
            ) from self._load_error

        started = time.monotonic()
        try:
            with self._generation_lock, self._torch.inference_mode():
                prompt = self._format_messages(messages)
                max_input_tokens = self._input_token_limit()
                model_inputs = self._tokenizer(
                    prompt,
                    return_tensors="pt",
                    truncation=True,
                    max_length=max_input_tokens,
                )
                model_device = next(self._model.parameters()).device
                model_inputs = {
                    name: tensor.to(model_device)
                    for name, tensor in model_inputs.items()
                }
                generated = self._model.generate(
                    **model_inputs,
                    max_new_tokens=self.MAX_NEW_TOKENS,
                    max_time=self.MAX_GENERATION_SECONDS,
                    do_sample=False,
                    pad_token_id=self._tokenizer.eos_token_id,
                )
                if time.monotonic() - started > self.MAX_GENERATION_SECONDS:
                    raise AnalystProviderTimeout(
                        "Local language-model generation exceeded its time budget."
                    )
                prompt_length = model_inputs["input_ids"].shape[1]
                return self._tokenizer.decode(
                    generated[0][prompt_length:], skip_special_tokens=True
                ).strip()
        except AnalystProviderTimeout:
            raise
        except Exception as exc:
            raise AnalystProviderFailure(
                "The local language model could not complete this request."
            ) from exc

    def _format_messages(self, messages: list[dict[str, str]]) -> str:
        if getattr(self._tokenizer, "chat_template", None):
            try:
                return self._tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                    enable_thinking=False,
                )
            except TypeError:
                # Other tokenizers may not expose Qwen's thinking toggle.
                return self._tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                )
        return "\n\n".join(
            f"{message['role'].upper()}: {message['content']}"
            for message in messages
        ) + "\n\nASSISTANT:"

    def _input_token_limit(self) -> int:
        configured_limit = getattr(self._model.config, "max_position_embeddings", None)
        if not isinstance(configured_limit, int) or configured_limit <= 0:
            return self.MAX_INPUT_TOKENS
        return min(configured_limit, self.MAX_INPUT_TOKENS)
