# Phase 10 · Step 10.1: Analyst use cases and answer boundaries

## Decision

The user selected **Option B: bounded question answering over approved
dashboard context**. The initial experience may provide a generated portfolio
brief and answer follow-up questions about evidence currently available from
the scored portfolio. It will not be an open-ended credit or intervention
assistant. Conversation history will not be persisted in the first version.

## Supported analyst tasks

The assistant may:

1. Summarize the current scored portfolio using the deterministic values shown
   in the dashboard.
2. Explain a dashboard metric, its definition, denominator, and data scope.
3. Compare cohorts selected in the current dashboard filters when the
   approved context contains their counts and summaries.
4. Explain review-capacity counts, queue selection and tie behavior using the
   deterministic queue result and documented rule.
5. Describe existing grouped local model attributions and their stated
   training-reference comparison, without framing them as causes.
6. Point out important limitations or identify when the available evidence
   cannot answer the question.

Answers must keep observed input patterns, estimated probabilities, queue
decisions, and generated prose distinct. They should name the metric and
denominator when making a quantitative comparison and avoid claims beyond the
current portfolio evidence.

## Out-of-scope requests

The assistant must decline or redirect requests to:

- Predict actual future default outcomes or certainty for an individual.
- Explain a score as a real-world cause or infer an intervention's effect.
- Recommend contacting, pricing, approving, rejecting, or otherwise acting on
  a customer.
- Make fairness, bias, legal-compliance, or adverse-action conclusions.
- Infer missing outcomes, including `DEFAULT`, or treat a model estimate as
  an observed outcome.
- Answer questions whose necessary metric or evidence is not in the current
  approved context.

For an unsupported question, return a concise limitation/refusal and, when
possible, identify which available dashboard metric can address a narrower
question. The language model must not score customers, alter rankings, change
capacity, or execute a decision.

## Data and interaction boundary

Questions refer only to the current portfolio and current dashboard context.
No conversation history is saved in the first version. The context sent to a
model must be explicitly assembled and approved in later steps; do not send
raw customer rows, customer IDs, `DEFAULT`, or demographic attributes by
default. The provider, hosting location, retention terms, and budget are not
selected by this step and remain open for Step 10.2.

## Acceptance criteria

- Each answer is grounded in a metric, definition, queue rule, or existing
  explanation included in the approved request context.
- Quantitative statements retain the supplied value, units, denominator, and
  scope; the assistant does not manufacture missing comparisons.
- The answer distinguishes model estimates from observed outcomes and
  generated interpretation.
- Unsupported causal, fairness, credit-decision, intervention, and
  individual-outcome requests are declined or redirected.
- The assistant cannot change deterministic model or decision outputs.
- The interface makes clear that generated commentary can be limited and
  should be checked against the displayed dashboard evidence.
- No chat history is persisted in the initial release.

## Step-by-step walkthrough

This is a product-scope and safety-definition step, so it changes no Python,
API, or frontend code. The decision narrows the original Phase 10 options:
it preserves the useful interaction from bounded Q&A while excluding the
unbounded general assistant. These boundaries will guide Step 10.2's provider
and privacy decision, Step 10.3's context allowlist, and later grounding and
evaluation tests. They do not authorize transmitting data to any model
provider.
