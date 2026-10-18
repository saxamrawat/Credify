# Phase 10 · Step 10.11: Load the QLoRA adapter for local inference

## Decision and deliverable

The user selected **Option B: load the pinned base model and the PEFT adapter
together at runtime**. The API now reads a local base-model directory and the
Kaggle adapter directory, checks that the adapter metadata matches the pinned
Qwen3-8B revision, loads the base in 4-bit NF4, attaches the LoRA weights with
PEFT, and performs local-only generation. The API stays disabled unless the
existing minimum-cell policy is configured. No base checkpoint was downloaded
and no inference was run in this workspace.

The Kaggle output at `artifacts/genai/qwen3_8b_qlora_run/` contains the PEFT
adapter, `training_manifest.json`, and trainer checkpoints. The runtime uses
the `adapter/` subfolder and manifest. It does not load trainer checkpoints.

## 1. Why base plus adapter

QLoRA trains a small set of low-rank adapter weights while keeping the base
model quantized and frozen. The resulting `adapter_model.safetensors` stores
only those learned changes; it is not an entire language model. Loading it
requires both the exact base checkpoint and PEFT's adapter loader.

Merging would turn the adapter into another full-size model export, requiring
more memory and disk and duplicating the base. The user chose the approach
that keeps the adapter small. Option C, leaving the app on the untuned base,
was not selected because the project is explicitly doing fine-tuning.

## 2. Pin the local inference dependencies

The `genai-local` optional dependency group now matches the Kaggle run's
Transformers, Hugging Face Hub, PEFT, bitsandbytes, and Accelerate versions.
Install the local model dependencies only on a CUDA-capable machine intended
for inference:

```bash
pip install -e '.[genai-local]'
```

PyTorch is left at a minimum compatible version rather than pinning Kaggle's
CUDA-specific build, because the correct PyTorch wheel depends on the target
machine's CUDA runtime. bitsandbytes still requires a compatible GPU runtime.

## 3. Download the exact base revision separately

The adapter folder does not contain the base weights. Download the selected
revision to a local directory accessible to the API. This example uses
Hugging Face Hub's Python API and writes only to the path passed as
`local_dir`:

```bash
python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='Qwen/Qwen3-8B', revision='e8bbd8252970581ea5b08b6a5b3e668adaf3161a', local_dir='artifacts/genai/qwen3_8b_base')"
```

This may download many gigabytes; it was not run as part of this step. Keep
both model files and adapter files out of Git. The repository already ignores
`artifacts/genai/`. Do not upload the model to the current 1 vCPU / 1 GB
Droplet; Phase 11 must choose a machine that can hold and serve the model.

## 4. Configure two local paths

The old single `PROPENSITY_GENAI_MODEL_PATH` setting is replaced by two
settings:

```dotenv
PROPENSITY_GENAI_BASE_MODEL_PATH=/absolute/path/to/artifacts/genai/qwen3_8b_base
PROPENSITY_GENAI_ADAPTER_PATH=/absolute/path/to/artifacts/genai/qwen3_8b_qlora_run/adapter
```

The base directory must contain `config.json` and the safetensors checkpoint
files. The adapter directory must contain `adapter_config.json`,
`adapter_model.safetensors`, and the tokenizer/template files from Kaggle. Its
parent must contain `training_manifest.json`, as in the generated Kaggle
output. Keep `PROPENSITY_GENAI_MINIMUM_CELL_SIZE` unset until the separate
activation decision; without that policy, the application does not load the
model or generate answers.

## 5. Validate provenance before loading weights

`LocalHuggingFaceProvider.load()` checks the paths before importing the large
runtime packages. It reads the adjacent training manifest and adapter config
and verifies that both identify `Qwen/Qwen3-8B` at revision
`e8bbd8252970581ea5b08b6a5b3e668adaf3161a`. This prevents a mismatched
adapter from being silently combined with the selected base model. The API
uses local-only loading and does not contact Hugging Face during startup.

The check authenticates the declared provenance; it does not cryptographically
prove that the base files were downloaded from that revision. The operator
must use the pinned download command and retain the generated training
manifest with the adapter.

## 6. Load the quantized base model and attach PEFT

The provider refuses to load this QLoRA runtime without CUDA. It selects BF16
compute when the GPU supports it and FP16 otherwise. The Transformers loader
uses the same core quantization choices as training:

```python
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=compute_dtype,
)
base_model = AutoModelForCausalLM.from_pretrained(
    base_path,
    local_files_only=True,
    trust_remote_code=False,
    use_safetensors=True,
    quantization_config=quantization_config,
    device_map="auto",
)
model = PeftModel.from_pretrained(
    base_model,
    adapter_path,
    local_files_only=True,
    is_trainable=False,
)
```

`device_map="auto"` lets Accelerate place the quantized model on the available
devices. The model is switched to evaluation mode and generation remains
deterministic. No custom model code is enabled. Qwen's chat template is called
with `enable_thinking=False`, matching the training serialization; a fallback
handles tokenizers whose templates do not accept this Qwen-specific option.
This load pattern follows the official Hugging Face
[bitsandbytes quantization](https://huggingface.co/docs/transformers/quantization/bitsandbytes)
and [PEFT model loading](https://huggingface.co/docs/peft/package_reference/peft_model)
guidance.

## 7. Understand the files changed

- `src/propensity_prediction/api/local_llm.py` now accepts separate base and
  adapter paths; checks their required files and provenance; requires CUDA;
  loads NF4 with double quantization; attaches the PEFT adapter; and disables
  Qwen thinking mode when formatting messages.
- `src/propensity_prediction/api/main.py` reads the two new environment
  variables when it constructs the provider. It still calls `load()` only
  when the minimum-cell policy is configured.
- `pyproject.toml` pins the local inference stack to the versions recorded by
  the Kaggle run in the optional `genai-local` dependency group.
- `docs/genai_analyst_layer_plan.md` records the selected option and completion
  of Step 10.11. The earlier Step 10.5 walkthrough is updated to mark its
  single-checkpoint loader description as superseded.

## 8. Limits and next step

The artifact manifest records 16 training and 4 validation examples, a
training loss of about 2.407, and a final validation loss of about 0.819.
Validation is too small to support a quality claim. This step establishes a
reproducible loading path; it does not show that the tuned model is better,
safe, grounded, fast enough, or deployable.

The selected Qwen3-8B model cannot run on the current 1 GB Droplet. This code
has not been exercised against the base checkpoint or a CUDA inference
machine. Step 10.12 must compare the prompted base and tuned adapter on the
held-out evaluation set, review representative answers, and record latency
and resource use before any activation decision.

## Step summary

Connected the Kaggle QLoRA output to the local inference seam using the
base-plus-adapter approach selected by the user. The provider verifies the
adapter's declared base revision, loads the base in 4-bit NF4 on CUDA, and
attaches the adapter with PEFT. Generation remains behind the existing
small-cell policy gate. No model download or inference run was performed.
