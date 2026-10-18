# Phase 10 · Step 10.6: Bounded dashboard insight experience

## Decision and purpose

The user selected **Option B: a portfolio brief plus a bounded question
input**. The dashboard now offers three starter prompts and one free-form
question per request. Only the latest answer is displayed; no conversation
history is kept. Generated commentary is optional and does not change scoring,
risk bands, queue selection, or any other deterministic dashboard result.

The panel is part of the Overview because the brief is about the scored
portfolio and its review capacity. It appears after an analysis has completed.
The existing Explore filters can scope the request. The application still
rebuilds the evidence on the server; the browser does not send its displayed
metrics as trusted facts.

## Files changed

- `src/propensity_prediction/dashboard/static/index.html` adds the optional
  insight panel, starter prompts, question form, and answer region.
- `src/propensity_prediction/dashboard/static/styles.css` styles the panel,
  evidence list, status messages, keyboard focus, and narrow-screen layout.
- `src/propensity_prediction/dashboard/static/app.js` retains the current
  uploaded predictor rows in memory, builds the request, calls the analyst
  answer endpoint, and renders claims and server citations.
- `docs/genai_analyst_layer_plan.md` records the completed decision and
  implementation.
- `README.md` updates the Phase 10 progress summary.

## 1. Place the panel in the existing workflow

The new `<section class="card analyst-card">` is inside the results section,
below the portfolio snapshot and its deterministic interpretation note. This
means it stays hidden until a file has been scored, shares the calm card
language of the existing dashboard, and is clearly separate from the charts
that show deterministic values.

The panel contains:

1. A short description of the evidence boundary and lack of saved history.
2. Three starter buttons: create a brief, explain risk bands, and explain
   queue capacity.
3. A labeled, required textarea capped at 1,000 characters.
4. A single Ask button and an answer region announced through `aria-live`.

Starter buttons populate the textarea and submit immediately. A custom
question uses the same request path. While a request is in flight, the submit
and prompt buttons are disabled. A later response replaces the previous
response; nothing is appended to a transcript or written to browser storage.

## 2. Keep the API request stateless and bounded

`renderOverview()` retains the validated CSV predictor rows in
`currentInputRows`, alongside the current deterministic result. When asked,
`askAnalyst()` posts to the same-origin `POST /v1/analyst-answer` route with:

- The validated input rows needed by the stateless server to reconstruct the
  current portfolio. These rows are sent to the application API, not directly
  to a model by the browser.
- The review capacity from the current scored result.
- Allowlisted Explore filters (probability bounds, risk band, review status,
  and an eligible feature/category or numeric range).
- The active group-by feature and the user's question.

The customer-ID search box is deliberately excluded from this request. The
Step 10.4/10.5 server path validates the input and constructs minimized
aggregate evidence; it does not treat any browser metric as authoritative.
The local model sees the question and that server-created evidence, not raw
rows or IDs. Each request is independent and recomputes context; the current
browser workflow does not persist a run or prompt history.

The chosen UI is the bounded question workflow, but it does not provide an
authorization boundary. Step 10.7 must evaluate privacy and small-cell policy,
and Phase 11 must address access control and deployment security before
production use.

## 3. Render answers as generated text with attached evidence

The dashboard distinguishes “Generated commentary” from its evidence list.
For each returned citation, it displays the server's metric key, value, unit,
scope, and definition. The disclaimer from the API is shown with the response.
Refusals use a plain explanation, including a separate message when the
server suppresses an answer under its small-cell gate.

All model claim text, citation values, and descriptions are inserted with
`textContent`, not HTML parsing. This prevents generated text from being
interpreted as markup. The frontend displays only claims and citations
returned by the server's structured response contract.

The API does not currently send a successful response unless both a local
model and a positive minimum-cell threshold are configured. When the endpoint
returns 503, the panel explains that generated insights are not enabled yet;
scoring and dashboard summaries continue to work. Other service errors and
network failures are shown inside the panel without replacing existing
portfolio results.

## 4. Follow the client code path

The relevant path in `app.js` is:

1. `renderOverview(result, inputRows)` saves the current request rows and
   renders the existing deterministic dashboard.
2. `buildAnalystFilters()` serializes only supported cohort filters. It omits
   the ID search term.
3. The form or starter-prompt listener calls `askAnalyst(question)`.
4. `askAnalyst()` sets the loading state, disables duplicate submissions,
   sends one request, and handles the API response or failure.
5. `renderAnalystAnswer()` replaces the answer region with either the
   structured claims and citations or a refusal message.
6. The `finally` block clears the busy state and re-enables the controls.

This path does not add new scoring logic. `currentResult` supplies the exact
capacity used by the last analysis, and the API recomputes its own metrics via
the existing deterministic service.

## Current limitation

The endpoint is gated until Step 10.7 decides the small-cell policy and a
local model checkpoint is selected and configured. Therefore, the panel is
implemented and handles the disabled state, but it is not yet expected to
produce live generated answers in the current configuration.

## Validation performed

The changed JavaScript passed a syntax check and `git diff --check` passed.
The automated test suite and browser interaction checks were not run in this
step.
