# Phase 10 · Step 10.10: Kaggle QLoRA workflow

## Decision and deliverable

The user selected **Option B: QLoRA** for the selected
`Qwen/Qwen3-8B` checkpoint. The user-run notebook is
[`notebooks/genai_qwen3_8b_qlora.ipynb`](../notebooks/genai_qwen3_8b_qlora.ipynb).
It loads the pinned base revision in 4-bit NF4, attaches a LoRA adapter,
trains only assistant answer tokens on `finetune_v1`, checks validation loss,
and saves a PEFT adapter plus a training manifest.

The notebook is prepared for the user's Kaggle account; **it has not been run
here**. Kaggle GPU availability, quotas, internet settings, and the actual
training run belong to the user's account. Kaggle's current notebook docs
describe selecting a GPU in notebook settings and note that free GPU capacity
may queue or vary. Check the account's current quota before running. See
[Kaggle notebook setup](https://www.kaggle.com/docs/notebooks) and
[Kaggle efficient GPU usage](https://www.kaggle.com/docs/efficient-gpu-usage).

## 1. Prepare the private Kaggle input dataset

Create a Kaggle Dataset with only these two files from this repository:

- `data/genai/finetune_v1/train.jsonl`
- `data/genai/finetune_v1/validation.jsonl`

Keep the Kaggle Dataset private. Do **not** include
`data/genai/finetune_v1/heldout.jsonl`; the notebook neither reads nor trains
on it. Add the dataset to the Kaggle notebook as an input, then edit
`DATA_DIR` in the notebook configuration cell to its mounted directory under
`/kaggle/input/`.

In Notebook Settings, select a **GPU** accelerator and enable Internet for
the pinned Hugging Face model download and package installation. A CPU or TPU
run is not supported by this notebook. Current Kaggle free GPU types and
availability can vary; the notebook prints the detected GPU name and memory
and stops when CUDA is unavailable. A GPU with about 16 GB memory is the
intended initial run configuration; a smaller device may run out of memory.

## 2. Pin the libraries and model revision

The first code cell pins Transformers 5.20.1, `huggingface_hub` 1.31.0, PEFT
0.21.2, bitsandbytes 0.50.2, and Accelerate 1.15.0. The Hub pin matters:
current Transformers imports `httpx` through `huggingface_hub.utils`, which
requires the compatible Hub re-export. The Transformers version is above the
minimum named in the Qwen3 model card; all these package versions are
recorded in the manifest. See the [Qwen3-8B card](https://huggingface.co/Qwen/Qwen3-8B),
[Hugging Face Hub 1.31.0 release](https://github.com/huggingface/huggingface_hub/releases),
[Transformers releases](https://github.com/huggingface/transformers/releases),
[Transformers v5 migration guide](https://github.com/huggingface/transformers/blob/main/MIGRATION_GUIDE_V5.md),
[PEFT releases](https://github.com/huggingface/peft/releases),
[bitsandbytes releases](https://github.com/bitsandbytes-foundation/bitsandbytes/releases),
and [Accelerate releases](https://github.com/huggingface/accelerate/releases).

The configuration cell pins model ID `Qwen/Qwen3-8B` to revision
`e8bbd8252970581ea5b08b6a5b3e668adaf3161a`. It also sets maximum sequence
length 768, random seed 17, and the output directory. If Kaggle's package
installation asks for a kernel restart, restart first and then continue from
the import/configuration cell. Record any package or CUDA installation error
in the run notes; do not silently change library versions without recording
them.

## 3. Confirm the runtime and validate the input

The notebook prints Python, PyTorch, Transformers, PEFT, bitsandbytes, and
Accelerate versions plus the GPU name and memory. It fails early if CUDA is
unavailable. The memory warning below 12 GiB is a caution, not a guarantee
that a 12 GiB device will succeed. Reduce `MAX_LENGTH` if the GPU runs out of
memory; keep batch size at 1 and gradient checkpointing enabled.

The JSONL loader reads only `train.jsonl` and `validation.jsonl`. It checks
the record fields, duplicate IDs, answer state, claim type, and citation
references. This catches data-contract mistakes before allocating the model.
The notebook prints the example counts and explicitly reports that held-out
examples were not loaded.

## 4. Build the supervised chat examples

The preprocessing cell uses the same answer system rules as
`src/propensity_prediction/api/analyst_answer.py`. For each JSONL record it
serializes the question and evidence as the runtime's user-message JSON,
serializes the expected `answer` object as the assistant target, and applies
Qwen's chat template with `enable_thinking=False`.

The important distinction in the labels is:

```python
labels = [-100] * len(prompt_ids) + full_ids[len(prompt_ids):]
```

PyTorch's causal-language-model loss ignores label positions set to `-100`.
That masks the system instructions and evidence context from the loss, so the
adapter learns to produce the target assistant answer rather than copy the
question or context. Padding tokens are also masked. The code verifies that
the full chat tokenization begins with the prompt tokenization and refuses to
silently truncate an example above `MAX_LENGTH`.

The custom dataset and collator are small on purpose: the project has only 16
training and 4 validation records, so a general-purpose dataset pipeline
would add dependencies without improving this pilot.

## 5. Load QLoRA and train the adapter

The model-load cell configures 4-bit **NF4** quantization and double
quantization, selects BF16 compute where supported and FP16 otherwise, and
loads the pinned checkpoint with `trust_remote_code=False` and
`use_safetensors=True`. It calls `prepare_model_for_kbit_training`, then
attaches LoRA rank 8, alpha 16, dropout 0.05, and PEFT's `all-linear` target
selection. Hugging Face's
[PEFT quantization guide](https://huggingface.co/docs/peft/developer_guides/quantization)
documents 4-bit NF4 QLoRA, preparation for k-bit training, and targeting
linear layers.

The Trainer settings use one example per device batch, gradient accumulation
of four, gradient checkpointing, a paged 8-bit AdamW optimizer, a learning
rate of `1e-4`, a 5% warmup (`warmup_steps=0.05` in Transformers 5), and up
to three epochs. Transformers 5 replaced the older `warmup_ratio` argument
with the fractional `warmup_steps` setting. Validation runs at each epoch;
early-stopping watches validation loss. A two-step `SMOKE_TEST` mode checks the
pipeline without saving an adapter. Set `SMOKE_TEST=False` for the full
configured training run.

Since validation has only four examples, its loss can change sharply from one
example. Early stopping is a guardrail, not a robust model-selection score.
The training set is also small enough that the adapter may memorize it. Do
not interpret a lower training loss as proof that the model answers real
portfolio questions better.

## 6. Inspect and retrieve the output

After a full run, the save cell writes:

- `adapter/`: PEFT LoRA weights and adapter configuration in safetensors
  format, plus tokenizer files.
- `training_manifest.json`: model ID/revision, dataset version and hashes,
  package versions, GPU model/memory, quantization and LoRA settings,
  example counts, training/evaluation metrics, and elapsed time.
- `qwen3_8b_qlora_run.zip`: a convenient archive of the output directory.

Save a Kaggle notebook version with outputs enabled, then download the ZIP
from the notebook's output files and bring it back with the manifest. Do not
publish the adapter or Kaggle dataset publicly. The adapter is **not** a
standalone model checkpoint and is not loadable by the current application
provider by itself. Step 10.11 will decide whether to merge it with the base
or extend local loading to use PEFT.

## What this step validates—and what it does not

The notebook contains checks for input structure, output contract, exact
citations, split separation, and run provenance. This workspace did not run
the notebook because it requires a Kaggle GPU session and the user's Kaggle
account. A successful notebook run establishes that the user-run training
pipeline completed and emitted an artifact; it does not establish answer
quality, correct safety behavior, or feasibility on the current 1 vCPU / 1 GB
DigitalOcean Droplet.

The user must retain the Kaggle run result for Step 10.11 and Step 10.12. If
the environment cannot install the pinned packages or load the model, record
the exact error, package versions, and GPU details before adjusting the
workflow.

## Step summary

Added a user-run Kaggle notebook for pinned Qwen3-8B QLoRA training. It
validates the train/validation inputs, applies NF4 4-bit quantization with
LoRA, trains answer-only tokens with constrained memory settings, and saves
the adapter and manifest. The held-out set is not attached or loaded. No
training was run in this workspace.
