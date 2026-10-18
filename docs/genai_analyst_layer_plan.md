# Phase 10 — GenAI Analyst Layer

## Purpose

Add a useful natural-language layer to the Phase 9 analyst dashboard. It may
explain deterministic portfolio summaries, answer bounded questions about the
currently scored portfolio, and help analysts navigate the existing evidence.
It must remain an interpretation layer: the model, probability scores, risk
bands, ranking, capacity rule, and local explanations remain deterministic
application outputs.

This phase does not add intervention recommendations, make credit decisions,
predict new outcomes, or claim causal or fairness conclusions. Phase 11 remains
the final deployment phase on the user's DigitalOcean Droplet.

## Current baseline and design constraint

Phase 9 uses FastAPI for scoring and decision logic with a custom
HTML/CSS/JavaScript dashboard. The current customer explanation endpoint
returns grouped model attributions and explicit limitations. There is no
database, user account system, or GenAI provider configured.

**Recommended boundary:** the browser requests an answer for the current
portfolio and question; the application validates the request, constructs a
compact context from deterministic metrics and approved explanation outputs,
and sends only that context to the selected language model. Raw customer rows,
customer IDs, and direct identifiers should not be sent to a hosted model.
The model's answer is labeled as generated commentary, checked against a
structured response contract, and presented with the metric names and values
that support it. Unsupported questions receive an honest limitation response.

The open-weight Hugging Face strategy and Kaggle as the user's training
environment are agreed. `Qwen/Qwen3-8B` is selected at a pinned revision and
Step 10.9 has a small, hand-authored synthetic dataset. The LoRA workflow,
artifact export, inference resource requirements, and activation policy
remain for later steps. The user's current DigitalOcean Droplet (1 vCPU, 1 GB
RAM, 25 GB disk) cannot serve the selected model; Phase 11 must resolve this.

## Proposed steps and strategies

### 10.1 Define analyst use cases, answer boundaries, and acceptance criteria

**Implement:** agree on the small set of analyst tasks GenAI should support,
such as summarizing the scored portfolio, explaining a displayed metric,
comparing two currently visible cohorts, and pointing out limitations. Define
which questions it must refuse or redirect, including outcome, causal,
fairness, credit eligibility, and intervention-effect claims.

**Options:**

| Option | Pros | Cons |
| --- | --- | --- |
| A. Generated portfolio narrative only | Lowest ambiguity; predictable and easy to evaluate; useful as a dashboard insight panel. | Does not let analysts ask follow-up questions. |
| B. Bounded question answering over approved dashboard context | More useful for interactive exploration while retaining a defined evidence scope. | Requires strong context construction, question refusal behavior, and evaluation. |
| C. Open-ended assistant with general knowledge and tools | Flexible and conversational. | Highest risk of unsupported financial claims, data leakage, and confident answers unrelated to the uploaded portfolio. |

**Recommendation:** start with B but constrain questions to current portfolio
metrics, definitions, queue results, and existing explanation outputs. Include
a generated narrative as the first interaction. Do not offer open-ended credit
or intervention advice.

**Deliverable:** agreed use cases, disallowed claims, refusal examples, and
acceptance criteria. User decision required before Step 10.2.

**Decision recorded:** Option B, bounded question answering over approved
dashboard context, with a generated portfolio brief and no saved conversation
history in the first version. Supported questions concern current portfolio
metrics and definitions, filtered cohort summaries, deterministic queue
behavior, existing grouped local explanations, and limitations. Questions
about actual outcomes, causes, fairness, credit decisions, or intervention
recommendations must be refused or redirected. See
[`phase_10_step_10_1_use_cases_and_boundaries.md`](phase_10_step_10_1_use_cases_and_boundaries.md).

### 10.2 Decide model and experimentation strategy · Complete

**Implement:** select the candidate model family and decide whether to fine-
tune or use prompting. Keep inference hosting and deployment-specific
resource decisions separate for Phase 11.

**Options:**

| Option | Pros | Cons |
| --- | --- | --- |
| A. Hosted model provider behind a server-side adapter | Strong model capability; small local resource footprint; provider can be changed behind one interface. | Requires external network and credentials; has per-use cost; data processing and retention terms need explicit review. |
| B. Open-weight instruction model from Hugging Face, prompted first with optional Kaggle LoRA experiment | Keeps a portable model option; Kaggle can support bounded adapter experiments; current portfolio facts remain runtime context. | Exact checkpoint/license and inference resources remain to be evaluated; Kaggle has variable compute quotas and does not serve the application. |
| C. Keep a provider-neutral interface and use a local mock until a provider is approved | Allows the API, grounding, UI, and tests to be built without transmitting portfolio context. | Does not deliver live generated answers until a provider/host is chosen. |

**Decision recorded:** Option B, initially with a prompted baseline and an
optional LoRA experiment if evaluation justified it. The user has since
clarified that Phase 10 must include actual fine-tuning, with Kaggle training
code they can run. This updated direction supersedes treating LoRA as
optional: Steps 10.8–10.12 now cover checkpoint selection, training data,
Kaggle LoRA training, artifact integration, and model-backed evaluation.
Training examples must not contain raw customer rows or outcomes; deterministic
application evidence remains runtime context. The exact model, license, and
inference host remain open until those steps and the Phase 11 resource review.
See
[`phase_10_step_10_2_open_model_and_kaggle_strategy.md`](phase_10_step_10_2_open_model_and_kaggle_strategy.md).

**Deliverable:** model family and training strategy. The user confirmed an
open-weight Hugging Face approach and Kaggle as training compute. The exact
checkpoint is selected in Step 10.8.

### 10.3 Define a trusted, minimized context contract · Complete

**Implement:** create a typed server-side request and context model containing
only the evidence approved in Step 10.1. Context may include portfolio count,
score distribution summaries, reference risk-band counts, requested and
selected review capacity, filtered cohort denominators, and existing local
explanation group values. Include definitions, denominators, provenance, and
limitations beside every metric.

**Options:**

| Option | Pros | Cons |
| --- | --- | --- |
| A. Send raw customer rows to the model | Makes arbitrary per-row questions easier. | Unnecessary exposure of personal and sensitive data; greater prompt-injection surface; contradicts the proposed data-minimization boundary. |
| B. Send only deterministic aggregates and approved grouped explanation outputs | Minimizes exposure; makes evidence traceable; matches Phase 9's metric-first design. | Limits row-level questions and requires an explicit context schema. |
| C. Send a mix of aggregates plus selected, de-identified rows | Enables selected-customer questions with less direct identifying data. | Rare combinations can still identify individuals; consent and minimum-group rules are needed; more complex to validate. |

**Recommendation:** B. Keep customer-specific row inspection in the existing
deterministic explanation view. Build context on the server from validated
inputs and derived metrics, rather than trusting a browser-supplied answer
context. Do not include `ID`, raw rows, `DEFAULT`, or demographic fields in
model context by default.

**Deliverable:** typed context schema, definitions/provenance, allowed fields,
and an audit showing excluded inputs.

**Decision recorded:** Option B. Send deterministic aggregates and approved
grouped explanation outputs only. Every metric carries scope, definition,
denominator/sample count, source, and limitations. Exclude raw rows, IDs,
`DEFAULT`, demographic input values, file metadata, and chat history. A local
grouped explanation is included only on explicit customer-detail questions,
without ID or raw features. No small-cell suppression threshold was chosen;
Step 10.7 will evaluate this before live generation. See
[`phase_10_step_10_3_trusted_context_contract.md`](phase_10_step_10_3_trusted_context_contract.md).

### 10.4 Implement deterministic context assembly and API contract · Complete

**Implement:** add a service boundary that validates the user's question,
reconstructs or verifies current deterministic portfolio metrics, applies the
approved field policy, and builds compact evidence for the language model.
Keep scoring and queue construction in the existing deterministic services.

**Options:**

| Option | Pros | Cons |
| --- | --- | --- |
| A. Browser sends its already-rendered metrics to the answer endpoint | Minimal extra computation and a simple client request. | Browser context is mutable and its definitions can drift from the server's calculations. |
| B. Server recomputes context from a validated portfolio request and capacity | Stronger integrity and one authoritative metric definition; avoids trusting client-supplied summaries. | Repeats scoring/aggregation unless a run-state mechanism is added; request size and latency need attention. |
| C. Add server-side run storage and refer to a run ID | Avoids resending portfolio rows and supports repeat questions against stable results. | Introduces persistence, retention, deletion, authentication, and deployment responsibilities. |

**Recommendation:** B for an initial stateless implementation, sharing the
existing deterministic calculation functions. If repeated requests prove
costly, reassess C only after identity and retention requirements are defined.

**Deliverable:** request/response schema, context builder, validation and
size limits, stable metric definitions, and error behavior.

**Decision recorded:** Option B. `POST /v1/analyst-context` accepts the
validated current portfolio and capacity, plus allowlisted cohort filters,
optional group-by field, and an optional explicit customer identifier used
only to compute an existing grouped explanation. The server calls the same
queue/scoring service used by Phase 9, joins internal scores by ID, applies
the current deterministic risk bands, then returns typed aggregate evidence.
The response contains no ID or raw input rows. It includes metric scope,
definition, denominator, source, limitations, queue reason totals, active
cohort summaries, and optional group summaries/local explanation. Invalid
schema/filter requests return 422; invalid portfolio/explanation lookups
return 400; missing model returns 503. IDs and demographics are not valid
filter/group-by fields. Small-cell suppression is still unresolved and must
be reviewed in 10.7 before generated context is sent to a live model. This
step exposes evidence only; it does not call a language model or change the
dashboard. See
[`phase_10_step_10_4_server_context_assembly.md`](phase_10_step_10_4_server_context_assembly.md).

### 10.5 Add grounded generation, output validation, and failure handling · Complete

**Implement:** create a provider adapter that accepts the bounded question and
approved evidence, requests a concise answer, and returns a validated
structured result. Attach evidence references (metric key, value, denominator)
and distinguish evidence from generated interpretation. Handle timeouts,
provider errors, malformed output, refusal, and empty context without breaking
the dashboard.

**Options:**

| Option | Pros | Cons |
| --- | --- | --- |
| A. Plain text answer | Fastest integration; natural interaction. | Hard to validate factual support or render evidence consistently. |
| B. Structured answer with claims and evidence references | Easier to validate, display, audit, and test against deterministic values. | Requires schema design; some provider outputs may need repair or rejection. |
| C. Generate a full report with charts and narrative | Polished, exportable result. | Larger scope; duplicates dashboard content and increases unsupported-detail risk. |

**Recommendation:** B. Validate references against the context supplied in
that request; reject unknown metric keys. Never let the model invoke the
scoring model, change capacity, rank customers, or execute an action.

**Deliverable:** provider adapter interface, prompt/version, structured output
schema, evidence validation, refusal/error paths, and secure configuration.

**Decision recorded:** Option B. Add structured claims with a required claim
kind and one or more evidence keys. The API validates the JSON schema, rejects
unknown evidence keys, and attaches citations from the current server-built
context. A local Hugging Face Transformers adapter loads only a configured
local checkpoint, uses deterministic decoding, serializes generation, and
limits input/output tokens and generation time. The model and generation
remain disabled unless a local model path and a positive small-cell threshold
are configured; Step 10.7 must evaluate and choose that threshold before
activation. Malformed output, invalid references, timeouts, provider failures,
and unavailable configuration use stable error responses. See
[`phase_10_step_10_5_grounded_generation.md`](phase_10_step_10_5_grounded_generation.md).

### 10.6 Add a bounded GenAI experience to the dashboard

**Status: Complete.** The user selected Option B. The Overview now contains
an optional portfolio brief and bounded question panel with starter prompts,
one question per request, structured evidence display, accessible loading and
error states, and no saved history. It calls the stateless answer endpoint
with the current portfolio inputs and allowlisted Explore filters; the server
rebuilds the evidence. The endpoint's existing model and privacy-policy gate
is surfaced as a friendly unavailable state. See
[`phase_10_step_10_6_dashboard_experience.md`](phase_10_step_10_6_dashboard_experience.md).

**Implement:** add an optional, clearly labeled generated-insights panel with
starter questions, a question input, answer/evidence display, loading/error
states, and a way to distinguish deterministic dashboard values from generated
commentary. Preserve the dashboard's calm visual style and accessible keyboard
flow.

**Options:**

| Option | Pros | Cons |
| --- | --- | --- |
| A. One-click generated portfolio brief | Simple, low friction, and easy to position as optional. | No analyst follow-up or cohort-specific query. |
| B. Portfolio brief plus bounded question input | Supports follow-up questions while using the same approved evidence scope. | More UI state, backend contract work, and abuse/refusal cases to handle. |
| C. Separate chat workspace with conversation history | Familiar conversational pattern; supports longer analysis sessions. | Adds history retention, privacy, deletion, and multi-turn grounding complexity. |

**Recommendation:** B, with one question per request and no persisted
conversation history in the first version. Add history only if the user
approves storage and retention behavior.

**Deliverable:** accessible generated-insights panel, interaction copy,
request states, evidence presentation, and non-GenAI fallback.

### 10.7 Evaluate grounding, privacy, safety, and analyst usefulness

**Status: Complete for this iteration; generation remains disabled.** The user
selected Option B for evaluation and chose to leave the minimum-cell threshold
unset until a model and representative portfolio can be reviewed. Versioned
synthetic-data checks now cover trusted evidence
references, server-recomputed filters, raw-input exclusion, prompt
construction, small-cell suppression boundaries, malformed output, and
provider/configuration failures. Fourteen targeted checks pass. The current
release recommendation is to keep generation disabled. Real-model analyst
review and selection of a threshold remain activation prerequisites once a
checkpoint and representative portfolio are available. See
[`phase_10_step_10_7_evaluation.md`](phase_10_step_10_7_evaluation.md).

**Implement:** create a versioned evaluation set covering supported metrics,
cohort comparisons, tie-boundary/unused-capacity explanations, local
explanation limitations, unsupported causal/fairness/outcome questions,
prompt injection in user text, empty and contradictory context, malformed
provider output, and service failure. Test that deterministic values remain
unchanged and evidence references match supplied context.

**Options:**

| Option | Pros | Cons |
| --- | --- | --- |
| A. Manual review of example answers | Fast and useful for interaction quality. | Hard to reproduce; easy to miss regressions. |
| B. Automated contract/grounding tests plus analyst review | Reproducible core checks with human assessment of usefulness and tone. | Requires maintained test cases and review effort after prompt/model changes. |
| C. Build a large benchmark and monitoring pipeline immediately | Broad coverage and production-style trend monitoring. | Premature before a provider, traffic pattern, and success criteria are known. |

**Recommendation:** B. Track grounded correctness, unsupported-claim rate,
refusal correctness, privacy-field exclusion, latency, and cost per request.
Treat fluent but unsupported answers as failures.

**Deliverable:** test/evaluation report, threat and privacy review, analyst
feedback, latency/cost measurements, and release recommendation.

### 10.8 Select the Hugging Face base checkpoint

**Implement:** compare a short list of instruction-tuned checkpoints for
license, model-card restrictions, supported language, context length,
quantization/LoRA support, Kaggle trainability, and compatibility with the
local Transformers inference adapter. Record the exact revision and license
before downloading or training.

**Options:**

| Option | Pros | Cons |
| --- | --- | --- |
| A. Small checkpoint chosen for modest local inference resources | Lower memory and faster experiments; more likely to fit a small deployment host. | May be less reliable at structured output and nuanced refusals. |
| B. Mid-sized instruction checkpoint with quantized LoRA training | Better capability while remaining a plausible Kaggle experiment. | Resource and license fit must be verified; inference may still exceed the future Droplet budget. |
| C. Largest available checkpoint and tune for best answer quality | Highest potential capability. | Kaggle quotas and Droplet inference may not support it; increases runtime and export complexity. |

**Decision recorded:** the user selected the mid-sized strategy and approved
`Qwen/Qwen3-8B` as the Phase 10 base checkpoint. The Step 10.8 walkthrough
records the revision, license, compatibility findings, and deployment caveats.
This selection does not authorize downloading or training the model in this
step; the user will run the later Kaggle training workflow.

**Deliverable:** selected checkpoint ID and revision, license review,
tokenizer details, quantization direction, context length, resource estimate,
and a remaining deployment hardware check. See
[Step 10.8: checkpoint selection](phase_10_step_10_8_checkpoint_selection.md).

### 10.9 Create a reviewed fine-tuning dataset · Complete

**Implement:** define instruction/response examples for bounded dashboard
tasks, refusal cases, evidence citation format, and wording limitations.
Examples teach response style and contract-following; real portfolio metrics
still come from the live deterministic context. Keep a held-out set that is
not used for training.

**Options:**

| Option | Pros | Cons |
| --- | --- | --- |
| A. Hand-author a small synthetic instruction set | Transparent and easy to review; contains no customer records. | Narrow coverage and more manual authoring. |
| B. Generate synthetic evidence contexts from the approved schema, then review the pairs | Covers metric shapes, citations, refusals, and edge cases more broadly. | Synthetic examples can encode mistakes or repetitive language unless reviewed. |
| C. Train on real customer rows, outcomes, or historical portfolio exports | Could resemble operational data. | Conflicts with the agreed minimization boundary and can expose sensitive records; not recommended for this project. |

**Decision recorded:** Option A, a small hand-authored synthetic instruction
set. Every example is explicitly authored for the response contract and uses
invented aggregate evidence. The set excludes customer IDs, raw predictors,
`DEFAULT`, and unreviewed analyst conversations. It is an initial experiment,
not enough evidence to assume robust generalization or improved answer quality.

**Deliverable:** versioned train/validation/held-out datasets, a data
dictionary, review checklist, and provenance notes. Completed in
[Step 10.9 walkthrough](phase_10_step_10_9_synthetic_dataset.md). The training
and held-out examples use distinct authored questions and synthetic values;
the separate Step 10.7 evaluation set remains unchanged.

### 10.10 Build the Kaggle QLoRA training workflow · Complete

**Implement:** create a reproducible notebook and companion instructions the
user can run in Kaggle. It should load the chosen public Hugging Face
checkpoint, validate the dataset, apply LoRA/QLoRA settings appropriate to
the selected model and available accelerator, track training and validation
loss, save adapter/config/tokenizer artifacts, and emit a training manifest.
Kaggle is an experimentation environment, not the production inference host.

**Options:**

| Option | Pros | Cons |
| --- | --- | --- |
| A. Prompt-only baseline, no fine-tuning code | Lowest training complexity. | Does not meet the user's request to perform actual fine-tuning. |
| B. Parameter-efficient LoRA/QLoRA notebook | Lower training memory and faster experiments than full fine-tuning; produces a compact adapter. | Requires compatible quantization/runtime libraries and an additional adapter integration/export step. |
| C. Full fine-tuning | No adapter composition at inference; can update all model weights. | High compute/storage demand and likely poor fit for free Kaggle sessions and this project's small curated dataset. |

**Decision recorded:** Option B, QLoRA using the pinned Qwen3-8B checkpoint
loaded in 4-bit NF4 with double quantization and a trainable LoRA adapter.
The user will run the notebook in Kaggle and bring the resulting artifact and
manifest back; this workspace cannot access the user's Kaggle account or GPU
session.

**Deliverable:** runnable Kaggle notebook, setup guide, conservative memory
settings, data checks, smoke-run option, adapter output, and reproducibility
manifest. See [Step 10.10 walkthrough](phase_10_step_10_10_kaggle_qlora.md).
The workflow reads only the synthetic training and validation files and must
not upload private data or secrets.

### 10.11 Export and connect the tuned model to local inference · Complete

**Implement:** make the Kaggle adapter loadable by the local Transformers
provider. The adapter is not a standalone checkpoint, so the provider needs
the pinned base model plus the PEFT adapter. The user selected runtime loading
of base plus adapter.

**Options:**

| Option | Pros | Cons |
| --- | --- | --- |
| A. Merge LoRA weights into a full safetensors checkpoint | Fits the current loader and simplifies runtime packaging. | Export may need substantial memory/disk and duplicates base weights. |
| B. Extend the adapter to load base plus LoRA adapter | Keeps the adapter small and makes the tuned delta explicit. | Adds PEFT runtime dependency and more deployment configuration. |
| C. Keep the adapter as a Kaggle-only artifact and use the base model in the app | No inference-loader changes. | The application would not use the fine-tuned model, defeating the requested work. |

**Decision recorded:** Option B. Keep the compact adapter separate and load it
with the pinned base model using PEFT. The provider verifies the adapter
manifest against the selected model revision, loads 4-bit NF4 weights on CUDA,
and stays behind the existing policy gate. The current 1 GB Droplet cannot
serve this model; Phase 11 must plan suitable inference hardware. See the
[Step 10.11 walkthrough](phase_10_step_10_11_adapter_inference.md).

**Deliverable:** local base-plus-adapter loading path, provenance checks,
dependency pins, and configuration instructions. Generation remains disabled
until Step 10.12 passes and the activation policy is approved.

### 10.12 Compare base and fine-tuned models and complete analyst review

**Implement:** run the Step 10.7 evaluation set against both the prompted
base checkpoint and the fine-tuned checkpoint. Compare structured validity,
correct citations, numerical fidelity, refusal behavior, prompt-injection
resistance, latency, and resource use. Have the analyst review representative
answers with the Step 10.7 rubric. Measure suppression rates on an approved,
representative portfolio before deciding whether to configure a minimum-cell
threshold.

**Options:**

| Option | Pros | Cons |
| --- | --- | --- |
| A. Select the fine-tuned model if it is more fluent | Simple, visible quality improvement. | Fluency alone does not establish grounding or safety. |
| B. Require the fine-tuned model to pass every critical contract and safety case and improve analyst usefulness | Matches the project's evidence-first requirements. | May result in keeping the base model or disabling GenAI if tuning regresses. |
| C. Choose whichever model is faster | Directly optimizes response time. | Can select a fast model with unsupported claims or poor refusals. |

**Recommendation:** B. Treat factual or citation regressions, disclosure,
and unsafe answers as release failures even if prose quality improves. The
user must approve any minimum-cell threshold after seeing actual suppression
impact; otherwise leave it unset and generation disabled.

**Decision recorded:** the user selected Option B. A post-training evaluation
set and Kaggle comparison notebook are prepared. The tuned model must pass
critical contract and safety checks and improve analyst usefulness. Kaggle
execution, paired answer review, and the release recommendation are still
pending. See the [Step 10.12 walkthrough](phase_10_step_10_12_model_evaluation.md)
and [comparison notebook](../notebooks/genai_model_comparison_phase10_step10_12.ipynb).

**Deliverable:** base-versus-tuned evaluation report, completed analyst
scorecards, suppression analysis, latency/resource notes, and an explicit
recommendation to use the tuned model, retain the base model, or keep
generation disabled.

### 10.13 Integrate, document, and prepare the final deployment phase

**Implement:** document the supported questions, provider setup, prompt and
context versions, data flow, limitations, configuration, fallback behavior,
operational cost controls, and steps that must be completed during Phase 11.
Run the complete project suite and an analyst walkthrough before closing Phase
10. Do not deploy production during this phase.

**Options:**

| Option | Pros | Cons |
| --- | --- | --- |
| A. Ship the integration as experimental behind a disabled feature flag | Lets the rest of the app be validated without activating generation. | Requires clear flag behavior and can leave the feature unavailable to analysts. |
| B. Enable for all users once implementation is complete | Simplest experience. | No user/auth boundary exists yet; inappropriate before privacy, provider, and evaluation gates are approved. |
| C. Complete implementation and evaluation, then leave activation/provider configuration for Phase 11 | Keeps code and deployment readiness separate; aligns with deployment being the final phase. | GenAI will not be live in the deployed application until Phase 11 setup is finished. |

**Recommendation:** C, unless the user approves a controlled experimental
activation after evaluation. Phase 11 will configure the production host,
secrets, network policy, monitoring, and final live-provider checks.

**Deliverable:** Phase 10 guide, full validation evidence, explicit go/no-go
record, and Phase 11 deployment checklist updates.

## Phase boundaries

- Phase 9 is complete and remains the deterministic source of scores, bands,
  queue outcomes, metrics, and local explanations.
- Phase 10 adds only a bounded natural-language interpretation layer.
- Phase 11 is the final deployment phase on the user's DigitalOcean Droplet.

## Working process

The user wants one step at a time. Before each Phase 10 step, present the
proposed implementation, viable options, pros and cons, and recommendation;
answer questions and wait for the user's choice. Implement that step only
after the choice is settled, then create a detailed step walkthrough and give
a concise summary before moving to the next step. The recommendations in this
plan are proposals, not advance approval. In particular, no model provider,
external data processing, paid service, or production activation is approved
by this document.
