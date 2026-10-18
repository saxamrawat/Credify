# Phase 10 · Step 10.9: Hand-authored synthetic fine-tuning dataset

## Decision and result

The user selected **Option A: a small, hand-authored synthetic instruction
set**. This step creates dataset version `finetune_v1` as JSON Lines (JSONL)
files:

- [`train.jsonl`](../data/genai/finetune_v1/train.jsonl): 16 training examples.
- [`validation.jsonl`](../data/genai/finetune_v1/validation.jsonl): 4 examples
for training-time validation and overfitting checks.
- [`heldout.jsonl`](../data/genai/finetune_v1/heldout.jsonl): 4 examples
reserved for later review and not to be used for gradient updates or training
selection.

The examples are manually authored with invented aggregate values. They
teach structured response formatting, exact evidence citations, concise
wording, limitations, and representative refusals. They contain no real
portfolio export, customer row, customer identifier, raw predictor, outcome,
or analyst conversation.

This is a deliberately small pilot set. It makes the later Kaggle workflow
reproducible and lets us measure whether LoRA can learn the output contract;
it does **not** establish broad generalization, factual reliability, or an
improvement over the base model. Keep production generation disabled until
the base and tuned model are compared using the separate evaluation protocol.

## 1. Why JSONL, and why each split is separate

JSONL stores one complete, independently reviewable example per line. Each
record has the same three top-level fields:

| Field | Purpose |
| --- | --- |
| `id` | Stable synthetic example ID, prefixed by split (`TR`, `VA`, or `HO`). |
| `question` | An invented analyst request phrased as ordinary user input. |
| `evidence` | A map of exact evidence keys to invented, server-shaped aggregate citations. |
| `answer` | The target response object, matching the API's `AnalystAnswerDraft` contract. |

The JSONL filenames define the split, so the same row is not duplicated with
an editable `split` label. Step 10.10 can convert each record to the chosen
Hugging Face chat-template format using the same system instructions as
`src/propensity_prediction/api/analyst_answer.py`.

The training file is for model updates. The validation file is available to
monitor training and select settings, so it must not be used as training
examples. The held-out file remains untouched until the later comparison and
analyst-review step. Do not copy the Step 10.7 evaluation questions into any
split; Step 10.7 remains a separate contract/safety evaluation set.

## 2. Read one training example

The first training record is conceptually:

```json
{
  "id": "TR-001",
  "question": "What is the median model-estimated probability?",
  "evidence": {
    "portfolio.median_predicted_probability": {
      "key": "portfolio.median_predicted_probability",
      "value": 0.184,
      "unit": "probability",
      "scope": "full_portfolio",
      "definition": "Median of model-estimated default probabilities.",
      "denominator": 40,
      "source": "deterministic_scoring_summary",
      "limitations": ["Probabilities are estimates, not observed outcomes or expected losses."]
    }
  },
  "answer": {
    "status": "answered",
    "claims": [{
      "kind": "fact",
      "text": "The median model-estimated probability is 18.4% across 40 scored records.",
      "evidence_refs": ["portfolio.median_predicted_probability"]
    }],
    "refusal_code": null
  }
}
```

The evidence map mirrors the structure supplied to the real model: a metric
key maps to a citation object carrying the value, unit, scope, definition,
denominator, source, and limitations. The target answer cites that exact key.
The 0.184 value and the count of 40 are invented solely for this example.

The answer object follows the API's strict `AnalystAnswerDraft` shape:

- `status` is `answered` or `refused`.
- Answered records contain one or more claims. Each claim is a `fact` or an
  `interpretation` and points to one or more evidence keys supplied in that
  same record.
- Refused records contain an empty `claims` list and a supported refusal code:
  `unsupported_request` or `insufficient_evidence` in this dataset.
- The record has no extra answer fields. The API remains responsible for
  validating generated output and confirming that cited keys were actually
  supplied at runtime.

## 3. What the examples teach

The training set includes these patterns:

1. Report a supplied probability, percentile, range, or share with its scope
   and denominator.
2. Compare two supplied values while citing both exact keys.
3. Summarize an aggregate group without turning a descriptive pattern into a
   cause.
4. Explain that a model probability is an estimate rather than an observed
   outcome.
5. Explain a fixed risk-band reference and keep its meaning bounded.
6. Describe queue counts as analyst-review counts, not credit decisions.
7. Refuse questions that ask for unsupported amounts, outcomes, causal
   attribution, compliance certification, or individual credit actions.

Validation examples use different invented values and questions. Held-out
examples use separate authored prompts, including a percentile comparison
and requests for unsupported effect or individual action claims. They are
not copies of Step 10.7's specific evaluation prompts. Some safety categories
are intentionally represented in both places because the model must learn
those boundaries and then be evaluated on separate wording and examples.

## 4. Data dictionary and review checklist

### Data dictionary

- `id`: stable identifier; not a customer ID.
- `question`: synthetic user request.
- `evidence`: object keyed by evidence reference; values use the API citation
  fields `key`, `value`, `unit`, `scope`, `definition`, `denominator`,
  `source`, and `limitations`.
- `answer.status`: expected structured response state.
- `answer.claims[].kind`: `fact` for directly supported information or
  `interpretation` for bounded explanation.
- `answer.claims[].text`: short synthetic target sentence.
- `answer.claims[].evidence_refs`: exact keys from the same record's evidence.
- `answer.refusal_code`: `unsupported_request` or `insufficient_evidence`
  for refused examples; `null` for answered examples.

### Review checklist

Before using these files in training, review every record for:

- Fully invented values and context; no real or copied customer records.
- No identifiers, raw input rows, demographic values, or outcome labels.
- Evidence keys in every `evidence_refs` list exist in that same record.
- Claim text matches the cited value, unit, scope, denominator, and definition.
- Probabilities are called model estimates; risk bands are not outcomes or
  action categories.
- Group patterns remain descriptive and do not imply causes or interventions.
- Unsupported requests refuse with empty claims and a valid refusal code.
- Answered records have claims and a null refusal code.
- No duplicate example IDs or copied Step 10.7 evaluation prompts.
- Held-out rows remain separate from training and validation files.

## 5. Provenance and limitations

All records were authored in this repository for `finetune_v1`; values and
groups are illustrative. No external dataset or generative model was used to
create these pairs. This provenance makes examples auditable but does not
make their content correct by itself, so each row should still be reviewed
against the checklist before the Kaggle run.

The split contains 16 training examples, which is too small to support claims
of robust behavior across the product's full question space. LoRA may simply
memorize these patterns. Step 10.12 must compare base and tuned model behavior
on fresh questions, the Step 10.7 safety cases, held-out examples, and analyst
review. If quality is inconsistent, expand and review the dataset rather
than assuming more training epochs will fix it.

## Step summary

Created a small, hand-authored synthetic JSONL dataset with 16 training, 4
validation, and 4 held-out examples. Each answer follows the API's structured
contract and cites the synthetic evidence provided in that record. The
walkthrough records schema, purpose, split rules, data dictionary, review
checklist, and limitations. The app code and runtime behavior did not change.
