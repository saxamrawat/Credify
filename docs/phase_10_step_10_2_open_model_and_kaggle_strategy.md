# Phase 10 · Step 10.2: Open model and Kaggle experimentation strategy

## Decision

Proceed with an **open-weight instruction model from Hugging Face** as the
candidate model family. First establish a prompted, untuned baseline. A
parameter-efficient fine-tune such as LoRA is an optional experiment in
Kaggle, to be attempted only if the baseline falls short on the Step 10.1
acceptance criteria. For such an experiment, use reviewed instruction/answer
examples that teach response format and boundaries; do not fine-tune on raw
customer rows or historical outcomes as a substitute for passing current
metrics as context.

This decision does not select a specific checkpoint, license, quantization,
Kaggle notebook configuration, inference server, or production runtime. Those
depend on evaluation and resource measurements. Live inference deployment
remains in Phase 11 on the user's DigitalOcean Droplet or another explicitly
chosen host.

## Updated direction: fine-tuning is now required in Phase 10

The initial decision treated Kaggle LoRA as optional after a prompted baseline.
The user later clarified that Phase 10 must include actual fine-tuning and
Kaggle code they can run. The plan now includes explicit steps to select a
checkpoint, curate reviewed synthetic examples, build the LoRA/QLoRA notebook,
export and load the tuned artifact, and compare it with the base model.

This does not change the data boundary: fine-tuning examples must not contain
raw customer rows, customer IDs, `DEFAULT`, demographics, or unreviewed
customer outcomes. The model learns response format and bounded behavior;
current portfolio facts continue to arrive as minimized runtime evidence.
The prompted baseline remains useful as a comparison arm, but fine-tuning is
no longer conditional on that baseline failing. See the revised
[Phase 10 plan](genai_analyst_layer_plan.md), Steps 10.8–10.12.

## Why this is feasible

Hugging Face's PEFT guidance recommends testing prompting first and then
considering adapter/layer tuning if prompting is insufficient. LoRA is one
parameter-efficient method that trains a smaller set of adapter parameters
while leaving base weights frozen. Kaggle documents free GPU access with a
weekly usage quota; its published guidance says the quota is 30 hours or
sometimes higher depending on resource demand, so it must be checked in the
account at experiment time.

Sources:

- [Hugging Face PEFT method overview](https://huggingface.co/docs/peft/en/methods/overview)
- [Hugging Face LoRA documentation](https://huggingface.co/docs/peft/en/package_reference/lora)
- [Kaggle efficient GPU usage](https://www.kaggle.com/docs/efficient-gpu-usage)

## Why not fine-tune directly on the credit table

The dashboard needs accurate answers about each newly uploaded portfolio.
Fine-tuning on the project's tabular training data would not give the model
the live portfolio metrics, their denominators, or the definitions used by
the dashboard. It could also encourage the model to reproduce stale facts or
memorize examples. Instead, deterministic application code will calculate the
current metrics, then pass only the minimized, approved context to the LLM.

The LoRA experiment will use curated, reviewed examples that demonstrate how
to answer from supplied context, cite evidence, keep estimates distinct from
observed values, and refuse unsupported claims. Evaluate that adapter against
the same held-out question set and the untuned baseline; recommend activation
only if it improves measured usefulness without unacceptable grounding or
safety regressions.

## Alternatives considered

| Strategy | Benefit | Cost/risk | Decision |
| --- | --- | --- | --- |
| Hosted LLM provider | Strong capability and minimal local inference compute. | External data processing, credentials, recurring usage cost, and provider retention terms need approval. | Not selected. |
| Open-weight model plus Kaggle LoRA fine-tuning | User can run training experiments; base model and adapter can be evaluated separately; avoids choosing a per-call hosted API. | Model license, Kaggle quota, artifact handling, and eventual inference hardware must be checked; Kaggle is not the serving host. | Selected and now required in the Phase 10 plan. |
| Mock-only integration | Safest for early API/UI work before selecting a model. | Does not exercise real generation quality. | Useful for tests, but not the sole Phase 10 model strategy. |

## Guardrails for the later training notebook

- Select a specific model only after reviewing its license, access terms,
  architecture compatibility, context length, memory footprint, and expected
  inference speed.
- Use a frozen base model and a small LoRA adapter experiment; compare it
  against the prompted baseline before any activation decision.
- Do not upload real customer portfolios or direct identifiers to Kaggle.
- Do not include `ID`, raw customer rows, `DEFAULT`, or demographic fields in
  the language-model fine-tuning examples.
- Build examples from synthetic or carefully reviewed scenario/metric pairs;
  keep portfolio facts as runtime context rather than training memory.
- Save the exact model revision, license, dataset-generation procedure,
  notebook environment, random seeds, training parameters, evaluation set,
  and adapter checksum so the experiment can be reproduced.
- Compare the adapter with the untuned prompted model. A training loss
  decrease alone is not evidence that answers are safer or more grounded.
- Treat Kaggle as temporary experimentation infrastructure. It does not host
  the dashboard inference endpoint; measure deployment requirements during
  evaluation and configure final serving in Phase 11.

## Step-by-step walkthrough

This step settled the open-weight model family and training-data boundaries.
It changed no application code and did not start a Kaggle run. Steps 10.8–10.12
now explicitly carry out checkpoint selection, dataset preparation, user-run
Kaggle fine-tuning, artifact integration, and model-backed evaluation. The
user will run the actual Kaggle training session; its artifacts and results
must be reviewed before the app uses the tuned model.
