# Phase 10 · Step 10.4: Server-side analyst context assembly

## Decision and scope

The user selected **Option B: recompute context on the server from the
validated portfolio and review capacity**. This keeps scores, queue results,
risk bands, and filtered aggregates tied to the same deterministic service
definitions used by the dashboard. It repeats scoring for a new request, but
avoids trusting browser-calculated values or adding persistence and run IDs.

This step creates an API endpoint that returns bounded evidence. It does not
send anything to an LLM, add a dashboard question panel, or select an inference
provider. The endpoint is the server-side seam that a later provider adapter
can consume after the small-cohort policy is decided in Step 10.7.

## Files changed

- `src/propensity_prediction/api/schemas.py` adds strict request and response
  models for analyst context.
- `src/propensity_prediction/api/analyst_context.py` rebuilds the portfolio
  summary, applies filters, and creates minimized evidence.
- `src/propensity_prediction/api/routes.py` exposes
  `POST /v1/analyst-context`.
- `src/propensity_prediction/api/main.py` makes schema-validation errors use
  API-wide wording rather than mentioning only the review queue.
- `docs/genai_analyst_layer_plan.md` and `README.md` record completion.

## 1. Define a strict request contract

`AnalystContextRequest` extends the existing `ReviewQueueRequest`, so it uses
the same validated customer input shape, portfolio row cap, and requested
review capacity. It adds:

| Field | Purpose | Boundary |
| --- | --- | --- |
| `filters` | Reapply current Explore filters on the server. | Only score bounds, fixed risk band, selected status, and allowlisted non-demographic feature filters. |
| `question` | The analyst's natural-language request for the later generation step. | Required, trimmed, nonblank, and at most 1,000 characters. It is not copied into the evidence response or used to override context rules. |
| `group_by` | Summarize groups visible in Explore. | A listed dashboard field only; no ID, `SEX`, `EDUCATION`, or `MARRIAGE`. |
| `explain_customer_id` | Explicitly request an existing local grouped explanation. | Used only to locate a row in the request; the ID is discarded before the response is built. |

`AnalystCohortFilters` uses strict types and rejects reversed probability or
feature bounds. Categorical status filtering (`PAY_0`, `PAY_2` through
`PAY_6`) accepts an integer category. Those fields reject numeric ranges.
Other allowlisted fields accept optional numeric lower and upper bounds.
Unknown fields are rejected by Pydantic because extra properties are
forbidden.

This is an allowlist rather than a blacklist: the API does not accept an
arbitrary field name and then try to remove sensitive names later.

## 2. Reuse the Phase 9 scoring and queue service

`AnalystContextService.build_context()` first calls
`ReviewQueueService.build_queue(request)`. That existing service validates
unique IDs, obtains scores from the model artifact, and runs the established
tie-aware capacity selection. The context builder does not implement a new
prediction or ranking rule.

The queue response is sorted by risk rank, whereas the submitted rows retain
their original order. The builder therefore creates an internal map keyed by
customer ID and uses it to attach scores and selection flags to the rows. This
join happens only inside the API process. The ID is never copied into an
evidence item or response record.

The service reuses `validation_risk_band_definition()` and
`assign_risk_bands()` so that current cohort bands use the fixed Phase 6
reference cut points. It also uses the queue response's portfolio summary and
capacity accounting instead of independently recalculating those metrics.

## 3. Apply active filters on the server

`_filter_cohort()` implements the Explore filter semantics on the scored
DataFrame:

1. Include probability minimum and maximum bounds, both inclusive.
2. If supplied, match the fixed risk band.
3. If supplied, match selected or not-selected queue status.
4. If a feature filter is supplied, match a repayment status category or
   apply the numeric feature bounds.

Customer-ID text search is intentionally absent from the request model. It
cannot be used to ask the language model about a named row through this
context contract. Filters are echoed in the response only as the allowlisted
filter configuration, so the analyst can tell what defines the cohort.

The active cohort response includes its row count, mean estimated probability
when nonempty, selected count, and risk-band counts. Every aggregate count or
probability carries unit, scope, definition, denominator, provenance, and
limitations metadata. An empty cohort has a count of zero and a `null` mean;
zero is not substituted for an unavailable mean.

## 4. Build the full evidence set

The response's `evidence` dictionary has stable keys and typed metric values.
It includes:

- Full-portfolio count, mean, 25th percentile, median, 75th percentile, and
  probability range.
- Counts and shares for the fixed reference risk bands.
- Requested capacity, selected count, unused capacity, and queue reason-code
  totals.
- Active-cohort counts and mean probability, plus active-cohort risk-band
  counts.

Each `EvidenceMetric` records `value`, `unit`, `scope`, `definition`,
`denominator`, `source`, and `limitations`. The top-level response records
the risk-band reference and method, and the deterministic tie-preserving
queue rule. This makes the meaning and provenance available alongside the
numbers instead of leaving the model to infer them.

If `group_by` is provided, `_group_summary()` produces the current dashboard
group view. Repayment status fields use encoded category groups. Other fields
use quartile boundaries computed over the full portfolio, matching the
dashboard's scope for its quartile cuts; the group shares and means are then
computed over the filtered cohort. The response says which field and grouping
method were used. It includes group count, cohort share, mean probability,
and selected count, with the filtered-cohort denominator, definition, source,
and limitations. It never returns group members or their IDs.

If `explain_customer_id` is provided, `_local_explanation()` finds that row in
the submitted request and calls the existing `ReviewQueueService` explanation
method. Only the estimate, reference probability, grouped contributions,
method, background size, and explanation limitations are copied into the
response. The identifier and raw feature values are omitted. If the requested
ID is absent, the API returns a client error instead of a fabricated
explanation.

## 5. Expose the API route and error behavior

`POST /v1/analyst-context` takes the typed request and returns the typed
`AnalystContextResponse`. Existing application handlers map failures as
follows:

- **422** — malformed request, unsupported field, or invalid filter bounds.
- **400** — duplicate customer IDs or a requested explanation ID not present
  in the submitted portfolio.
- **503** — model artifact unavailable.

The generic request-validation message now refers to the API contract, so it
also describes this new route correctly.

## Data boundary and remaining decision

The response has no customer-level identifier list, raw customer rows,
`DEFAULT`, or `SEX`/`EDUCATION`/`MARRIAGE` feature values. The optional local
explanation is the previously approved grouped numeric attribution only.
The context endpoint is not yet connected to a model provider. A numeric
small-cell suppression threshold has not been chosen, so Step 10.7 must
evaluate and settle that policy before live generated answers are enabled.
The dashboard does not call this endpoint yet; the interaction is added in
Step 10.6 after the grounded generation contract is settled.

No chat history is accepted or stored. No scoring, selection, probability, or
risk-band logic is changed by this step.

## Validation performed

Python syntax compilation succeeded for the modified API modules. Importing
the new request schema and route succeeded, and the route registry includes
the new endpoint. The automated test suite was not run in this step.

## Walkthrough summary

1. Extend the existing portfolio request with bounded filter and explanation
   options, backed by explicit field allowlists.
2. Reuse the established queue service to recompute scores and selection.
3. Join queue data to request rows internally by ID, then remove ID from the
   evidence output.
4. Apply Explore filters and calculate only approved aggregate summaries.
5. Attach definitions, denominator, source, scope, and limitations.
6. Return structured evidence over FastAPI, leaving generation and dashboard
   integration for later steps.
