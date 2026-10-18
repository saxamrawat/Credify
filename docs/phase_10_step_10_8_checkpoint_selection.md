# Phase 10 · Step 10.8: Hugging Face checkpoint selection

## Decision

The user selected the mid-sized checkpoint strategy and approved
**`Qwen/Qwen3-8B`** as the base model for the planned Kaggle LoRA fine-tuning
workflow and the local analyst-answer adapter.

The selected repository revision is
[`e8bbd8252970581ea5b08b6a5b3e668adaf3161a`](https://huggingface.co/Qwen/Qwen3-8B/tree/e8bbd8252970581ea5b08b6a5b3e668adaf3161a).
Pinning the revision makes later dataset/training instructions reproducible;
the Hugging Face `main` branch may change. The model card declares the
**Apache-2.0** license and documents Transformers use through
`AutoTokenizer` and `AutoModelForCausalLM`, consistent with the broad model
class used by the existing local adapter. See the
[Qwen3-8B model card](https://huggingface.co/Qwen/Qwen3-8B).

This step records a model choice. It does not download model files, start a
Kaggle session, or enable live generation in the dashboard.

## 1. Compare the shortlisted candidates

| Candidate | Advantages | Trade-offs for this project |
| --- | --- | --- |
| `Qwen/Qwen3-4B` | Apache-2.0; causal language model; lower storage and memory needs than 8B; Transformers support. | Smaller capability budget; still needs careful local resource planning and JSON-oriented generation settings. |
| **`Qwen/Qwen3-8B` (selected)** | Apache-2.0; causal language model; safetensors available; documented Transformers loader aligns with the existing adapter; mid-sized capability target for Kaggle LoRA. | Hugging Face repository artifacts are about 16.4 GB in BF16, before runtime memory and other files. The unquantized local loader can need substantially more working memory. Droplet capacity has not been confirmed. |
| `microsoft/Phi-4-mini-instruct` | MIT license; 4B parameter class and a compact alternative. | The model card's documented loading path uses custom model code (`trust_remote_code=True`), while this project's adapter explicitly disables remote code. Adopting it would require a separate compatibility and security decision. |

The selected 8B checkpoint is the best fit for the user's requested middle
ground: it retains an ordinary causal-language-model integration path and is
large enough to make a meaningful LoRA experiment, without selecting a much
larger family. The smaller Qwen3-4B remains a fallback if the user's measured
inference-host budget rules out the 8B model.

Sources: [Qwen3-8B model card](https://huggingface.co/Qwen/Qwen3-8B),
[Qwen3-4B model card](https://huggingface.co/Qwen/Qwen3-4B), and
[Phi-4-mini-instruct model card](https://huggingface.co/microsoft/Phi-4-mini-instruct).

## 2. Compatibility with this application's model adapter

The current local provider in `src/propensity_prediction/api/local_llm.py`
loads a local directory through `AutoTokenizer` and
`AutoModelForCausalLM`, with `local_files_only=True`,
`trust_remote_code=False`, and `use_safetensors=True`. The Qwen3-8B model card
documents that loader family, so it does not require relaxing the project's
remote-code restriction.

The current provider does not specify a lower-precision `torch_dtype`, load a
quantized model, or configure a Qwen-specific chat-template option. Therefore
this selection alone does not make the checkpoint deployable. Later work must
address loading precision/quantization and generation behavior explicitly,
then verify the answer contract against the model-backed evaluation set.

Qwen3 has a thinking mode. The Qwen model documentation describes how to
control thinking through the chat template. For this application's
structured-answer contract, Step 10.11 must use the documented non-thinking
configuration (or another tested extraction strategy) so hidden reasoning
text cannot be mistaken for the JSON response. See the
[Qwen3-8B usage guidance](https://huggingface.co/Qwen/Qwen3-8B).

## 3. Training and inference resource caveats

The model repository is approximately 16.4 GB of BF16 weight artifacts. This
is a download/storage figure, not a guarantee that 16.4 GB of RAM is enough
for inference: framework overhead, KV cache, context length, and concurrent
requests add memory. The current provider moves the model to available CUDA
or CPU and does not enable quantization. A small CPU-only Droplet may not be a
practical host for the unquantized model.

The user provided the planned DigitalOcean Droplet configuration:
**1 vCPU, 1 GB RAM, and 25 GB disk**. This is not sufficient to serve
Qwen3-8B. The model has 8.2 billion parameters and BF16 weights; even a
theoretical 4-bit representation of the parameters alone is about 4.1 GB
before quantization metadata, runtime memory, context/KV cache, or the API and
dashboard processes. The full BF16 checkpoint artifacts are about 16.4 GB,
which would also leave little room on a 25 GB disk for the operating system,
application, caches, and model export. The [Qwen3-8B model card](https://huggingface.co/Qwen/Qwen3-8B)
lists the parameter count and BF16 format.

Therefore, keep the chosen Qwen3-8B for the Kaggle fine-tuning experiment,
but mark serving it on the current Droplet as **not feasible**. Phase 11 must
include an explicit hosting decision before enabling inference. The
recommended path is to resize or replace the Droplet with a host sized after
measuring the chosen quantized inference/export format and the complete
application. Do not pick a specific RAM tier from parameter count alone.
Kaggle training feasibility does not imply that the same model will fit on
the production Droplet.

## 4. License and data boundary

The Qwen3-8B model card identifies the model license as Apache-2.0. Before
redistributing model weights or serving the application publicly, retain the
license and model attribution in the deployment artifact/package and review
the current license text for the intended use.

The fine-tuning set remains synthetic and hand-authored, as already agreed.
It must not contain raw customer rows, customer identifiers, `DEFAULT`,
demographic attributes, or unreviewed customer outcomes. The model is trained
to follow the analyst response format and boundaries; deterministic runtime
evidence continues to supply current portfolio facts.

## 5. Next step

Step 10.9 will prepare and review synthetic training examples, with a held-out
evaluation split that does not overlap Step 10.7 evaluation questions. Step
10.10 will then provide the user-run Kaggle LoRA workflow. Do not start those
steps until the user has reviewed the Step 10.9 implementation proposal and
chosen its dataset-generation option.

## Step summary

Selected `Qwen/Qwen3-8B` at a pinned repository revision under Apache-2.0 for
the mid-sized Kaggle fine-tuning path. Its loader family fits the existing
local Transformers abstraction without enabling remote code. Its BF16 weight
artifact size, the unquantized current provider, the Qwen thinking-mode
behavior, and the confirmed 1 vCPU / 1 GB RAM / 25 GB Droplet configuration
are recorded as integration constraints. The current Droplet cannot serve
this model; Phase 11 must size a different or resized host before activation.
