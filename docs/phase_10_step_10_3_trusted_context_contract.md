# Phase 10 · Step 10.3: Trusted, minimized context contract

## Decision

The user selected **Option B: send deterministic aggregates and approved
grouped explanation outputs**. The language model receives evidence about
the current portfolio rather than customer-level input rows. Context values
must remain traceable to the deterministic Phase 9 calculations and carry the
scope, definitions, denominator, and limitations needed to interpret them.

This document defines the contract and exclusions. Step 10.4 will implement
server-side assembly and validation. This step adds no application code.

## Context payload sections

The proposed version 1 context is organized into these evidence sections:

| Section | Included evidence | Required interpretation metadata |
| --- | --- | --- |
| `portfolio` | Customer count and the available summary of predicted probabilities. | Scope = full uploaded portfolio; unit = probability; method and data source; count used for the summary. |
| `risk_bands` | Fixed-reference risk band labels, customer counts, portfolio shares, and the fixed reference definition. | Reference cohort and cut-point method; denominator = full portfolio count. These are descriptive bands, not interventions or outcome groups. |
| `review_queue` | Requested/target capacity, selected count, unused capacity, deterministic queue reason totals, and the documented tie policy. | Scope = scored portfolio; queue rule version; denominator for each share/count. Do not include customer rows. |
| `active_cohort` | Current filter description, matching count, and supported aggregate summaries for that cohort. | Scope = current filters; denominator = matching cohort; field and aggregation definition; `null`/unavailable behavior. It must not include individual members. |
| `feature_insights` | Existing uploaded-portfolio monthly repayment code/amount aggregates and the fixed Phase 6 model-importance reference, when relevant to the question. | Portfolio observation vs model-reference provenance; month/field definition; valid row count; evaluation cohort, metric, and method for model importance. Keep these evidence types distinct. |
| `local_explanation` | Only when the analyst explicitly asks about a selected customer's already computed grouped explanation: its model estimate, reference mean, and grouped contribution values. | Scope = one selected explanation; method, reference/background, group names, units, and local-explanation limitations. Do not attach the customer's ID or raw feature values. |

Each value sent to the model should be a typed evidence item with a stable
metric key, value, unit, scope, definition, denominator or sample count when
applicable, source/provenance, and limitation text. A value without enough
metadata to interpret it is omitted rather than guessed. Missing evidence is
represented as unavailable, never silently substituted with zero.

## Explicit exclusions

The model context must not contain:

- Raw customer rows, lists of customer IDs, or individual input values.
- `DEFAULT` or any actual outcome label.
- Demographic attributes (`SEX`, `EDUCATION`, `MARRIAGE`) or their supplied
  values. Existing grouped explanation outputs may be included only as the
  numeric model-attribution results approved above; do not expand a group
  back into its underlying feature values.
- CSV contents, upload file names, filesystem paths, authentication secrets,
  or unrelated environment/configuration values.
- Browser-generated metric values treated as authoritative without later
  server-side validation (Step 10.4 owns that implementation).
- Previous chat turns or persistent conversation history. Step 10.1 chose a
  stateless first version.

The user question itself is required to answer the request. Step 10.4 must
bound its length and treat it as untrusted user text, not as an instruction to
change the evidence allowlist or application rules.

## Illustrative contract shape

This is a conceptual payload, not an API schema or a sample of real customer
data:

```json
{
  "context_version": "1",
  "portfolio": {
    "customer_count": 120,
    "predicted_probability": {
      "mean": {
        "value": 0.28,
        "unit": "probability",
        "scope": "full_portfolio",
        "definition": "Arithmetic mean of model-estimated probabilities",
        "denominator": 120,
        "source": "deterministic_scoring_summary",
        "limitations": ["Model estimate; not an observed outcome"]
      }
    }
  },
  "review_queue": {
    "requested_capacity": 20,
    "selected_count": 18,
    "unused_capacity": 2,
    "selection_rule": "deterministic_risk_rank_with_equal_scores_kept_together"
  },
  "active_cohort": null,
  "feature_insights": null,
  "local_explanation": null
}
```

The illustrative values above only demonstrate structure. They must not be
used as defaults or as a real portfolio response.

## How this supports Step 10.1

The assistant can summarize the overall portfolio, explain a metric, compare
approved aggregates for the currently selected cohort, describe queue
capacity/tie behavior, and explain existing grouped attribution values when
the analyst explicitly asks about a customer detail. It cannot reconstruct a
customer record, identify someone, calculate a new prediction, change queue
selection, or answer questions requiring outcome or causal evidence that is
not present.

No numeric small-cell suppression threshold was selected in this step. The
context must preserve each relevant count/denominator so Step 10.7 can test
small-cohort behavior and make a reviewed suppression decision before a live
model receives such metrics.

## Step-by-step walkthrough

1. **Choose evidence sections:** use the same concepts the dashboard already
   shows, while marking full portfolio, filtered cohort, fixed model
   reference, and one-customer explanation as different scopes.
2. **Attach definitions and counts:** require source, meaning, unit, and
   denominator so generated sentences can preserve the actual metric context.
3. **Create a strict allowlist:** remove rows, identifiers, outcomes,
   demographics, filenames, and history before handing context to generation.
4. **Make unknowns explicit:** missing evidence remains unavailable so the
   model cannot interpret an absent field as zero or fill it from general
   knowledge.
5. **Defer computation details:** the data contract is now settled; Step 10.4
   will decide and implement how validated server code builds it from the
   current request.

## Validation boundary

This step is a written contract, so no software tests were required. During
Step 10.4, tests should prove that identifiers, raw records, outcome labels,
demographic values, file metadata, and prior conversation are absent; that
every included numeric metric has correct scope and denominator; and that
local explanation context appears only when explicitly requested.
