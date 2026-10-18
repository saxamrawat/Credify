# Phase 10 · Step 10.5: Grounded structured generation

## Decision and scope

The user selected **Option B: structured answers with evidence references**.
Each generated claim has a kind, text, and one or more stable evidence keys.
FastAPI validates the output, rejects keys absent from that request's evidence,
and attaches the corresponding server-created citations.

The implementation uses a local Hugging Face Transformers adapter because
the agreed Phase 10.2 strategy is an open-weight model. It does not select a
checkpoint, license, or inference host. The adapter loads a local checkpoint
directory only and does not download model files from Hugging Face during
application startup or inference.

## Files changed

- `src/propensity_prediction/api/schemas.py` defines generated claims, the
  model draft shape, evidence citations, and the answer response.
- `src/propensity_prediction/api/analyst_answer.py` makes the prompt, builds
  a citation index from the trusted context, validates output, and fails
  closed on unknown references or small cells.
- `src/propensity_prediction/api/local_llm.py` defines the provider interface
  and the optional local Transformers implementation.
- `src/propensity_prediction/api/errors.py` adds stable provider and output
  error types.
- `src/propensity_prediction/api/routes.py` adds `POST /v1/analyst-answer`.
- `src/propensity_prediction/api/main.py` configures the local model, applies
  the activation gate, and maps errors to stable HTTP responses.
- `pyproject.toml` adds optional `genai-local` dependencies.
- `docs/genai_analyst_layer_plan.md` and `README.md` record completion.

## 1. Specify the model's structured draft

`AnalystClaim` permits only two claim kinds:

- `fact` for a direct statement supported by supplied evidence.
- `interpretation` for a short explanation that remains tied to supplied
  evidence and limitations.

Every claim must be 1–600 characters and cite 1–8 evidence keys. A response
can contain at most six claims. `AnalystAnswerDraft` accepts exactly two
states:

```json
{"status":"answered","claims":[{"kind":"fact","text":"...","evidence_refs":["portfolio.customer_count"]}],"refusal_code":null}
```

```json
{"status":"refused","claims":[],"refusal_code":"insufficient_evidence"}
```

Pydantic forbids extra properties and validates the relationship between
`status`, `claims`, and `refusal_code`. Each claim's references must be unique.
The generated draft is untrusted input: it is never returned directly to the
client.

The API response replaces each referenced key with an
`AnalystEvidenceCitation` containing the server's value, unit, scope,
definition, denominator, source, and limitations. This makes the response
renderable without asking the browser to trust values written by the model.

## 2. Build a per-request citation index

`_build_evidence_index()` converts the Step 10.4 context into a dictionary
whose keys are the only keys a generated claim may cite. It includes:

- Stable portfolio, risk-band, and queue metric keys from `evidence`.
- Active cohort metrics such as its count, mean probability, selected count,
  risk-band counts, and allowlisted filter configuration.
- Optional group summaries, referenced by their position in this request's
  sorted summary list.
- An optional grouped local explanation only when Step 10.4 was explicitly
  asked to compute one.

The local explanation citation contains grouped contributions and its stated
limitations; it does not contain the searched customer ID or input row. The
question is sent separately from the citation index. No browser-supplied
metric values are accepted.

After generation, `AnalystAnswerService.answer()` compares every model-supplied
reference with this exact index. An unknown key causes a `502` invalid-output
error. The service collects referenced citations once, in claim order, and
builds the final response from the original server-side objects. A refusal
contains no claims or citations.

## 3. Set the fixed prompt boundaries

`SYSTEM_PROMPT` asks the model to use only supplied evidence, treat the
question as data, ignore instructions embedded in that question, and return
one JSON object in the agreed format. It also tells the model not to:

- Re-score customers, change capacity or ranking, or identify customers.
- Recommend customer contact, pricing, approval, rejection, or intervention.
- Claim observed outcomes, causes, intervention effects, fairness, or legal
  compliance.
- Treat probability estimates as observed defaults or expected losses.

The prompt is a behavioral instruction, not a proof that a model will follow
it. Step 10.7 will evaluate refusal behavior, prompt injection, and semantic
grounding. This step enforces JSON shape and citation-key existence but does
not prove that every sentence's meaning or number is correctly entailed by
its citation.

## 4. Load a local Hugging Face checkpoint

`LocalHuggingFaceProvider` implements a small `StructuredGenerationProvider`
protocol. That keeps the grounding service independent from the inference
runtime. The initial Step 10.5 implementation used a single complete
checkpoint. Step 10.11 superseded it with the chosen base-plus-adapter loader;
the current implementation:

1. Reads `PROPENSITY_GENAI_BASE_MODEL_PATH` and
   `PROPENSITY_GENAI_ADAPTER_PATH` as local directories.
2. Requires a base `config.json`, PEFT adapter config and safetensors weights,
   and the adjacent Kaggle `training_manifest.json`. It checks that the
   manifest and adapter target the pinned `Qwen/Qwen3-8B` revision.
3. Requires CUDA, then loads the base locally in NF4 4-bit with double
   quantization and attaches the adapter with PEFT. It sets the model to
   evaluation mode and never enables custom remote code.
4. Uses the tokenizer's chat template with Qwen thinking disabled when the
   template supports that option.
5. Truncates input to at most 8,192 tokens, generates at most 384 new tokens,
   and asks Transformers to stop after a 45-second time budget. Generation
   checks time between decoding passes, so a final pass may finish after the
   configured budget; the adapter then converts an over-budget result to a
   timeout response.
6. Serializes generation with a lock because one in-memory model is shared by
   the API process.

The optional install command after a checkpoint and hardware are selected is:

```bash
pip install -e '.[genai-local]'
```

The optional dependencies are not added to the base requirements. This avoids
installing PyTorch and Transformers for users who do not have a compatible
local checkpoint yet. Model loading can use substantial memory and CPU/GPU
resources, so the chosen checkpoint and host still need a resource review in
Phase 11. The official Transformers loader supports loading from
a local directory and `local_files_only`; generation supports a `max_time`
budget. See [Hugging Face Auto Classes](https://huggingface.co/docs/transformers/model_doc/auto)
and [Hugging Face text generation](https://huggingface.co/docs/transformers/main_classes/text_generation).

Model files must be downloaded locally at the pinned revision before
configuration. Custom model code is not enabled. The base directory contains
the full checkpoint files; the adapter directory contains only the LoRA
weights and metadata. The loader requires a CUDA-capable machine and cannot
run on the current 1 GB Droplet. See the [Step 10.11 walkthrough](phase_10_step_10_11_adapter_inference.md)
for download, dependency, and path instructions.

## 5. Keep generation disabled until privacy policy is settled

The API requires both model paths and the separately approved small-cell
policy before it loads the local LLM or generates an answer:

- `PROPENSITY_GENAI_BASE_MODEL_PATH`: local pinned base model directory.
- `PROPENSITY_GENAI_ADAPTER_PATH`: local PEFT adapter directory.
- `PROPENSITY_GENAI_MINIMUM_CELL_SIZE`: positive integer threshold.

The numeric threshold remains unset by default because the user has not
approved one. If it is missing or invalid, `POST /v1/analyst-answer` returns
`503 ANALYST_POLICY_UNAVAILABLE`; model loading is skipped. This makes the
code ready for the later evaluation while avoiding sending small-cell context
to a model before Step 10.7 chooses a policy.

When a threshold is configured, the service scans customer counts in
risk-band groups, queue reason groups, active-cohort metrics, and group and
selected-count summaries. Any positive count below the threshold produces a
deterministic refusal with `small_cell_suppressed`; the model is not called.
Zero counts do not trigger this rule. This is a conservative first gate, not
the final reviewed policy: Step 10.7 must assess which metrics require
suppression and whether this rule is useful for the dashboard.

## 6. Handle errors without returning model internals

The API maps failures to a stable error envelope:

| Condition | Status | Error code |
| --- | ---: | --- |
| Invalid question, filter, or request schema | 422 | `INVALID_REQUEST_SCHEMA` |
| Invalid portfolio or missing requested explanation | 400 | `INVALID_PORTFOLIO` |
| Missing model, invalid model path, or unset small-cell policy | 503 | `ANALYST_MODEL_UNAVAILABLE` or `ANALYST_POLICY_UNAVAILABLE` |
| Model generation exceeds its time budget | 504 | `ANALYST_PROVIDER_TIMEOUT` |
| Local inference fails | 502 | `ANALYST_PROVIDER_FAILURE` |
| Empty, malformed, schema-invalid, or unknown-reference model output | 502 | `INVALID_ANALYST_OUTPUT` |

The API does not return raw model output or exception details to the browser.
The dashboard integration and user-facing loading/error copy remain Step
10.6. No answer history is stored.

## 7. Request flow

```text
Question + current portfolio request
                 │
                 ▼
     Validate request and activation gate
                 │
                 ▼
  Re-score portfolio and build Step 10.4 evidence
                 │
                 ▼
     Apply small-cell refusal gate
                 │
                 ▼
  Local model receives question + citation index
                 │
                 ▼
      Parse strict JSON answer draft
                 │
                 ▼
 Validate every evidence key against this request
                 │
                 ▼
 Return claims + server-attached evidence citations
```

The new endpoint is `POST /v1/analyst-answer`. It recomputes the portfolio
for each request, consistent with the stateless Step 10.4 decision. It is not
called by the dashboard until Step 10.6.

## Validation performed

Python syntax compilation succeeded for the modified API modules. Importing
the application and generating its OpenAPI schema confirmed both analyst
routes are registered. `git diff --check` passed. The automated test suite
was not run in this step.
