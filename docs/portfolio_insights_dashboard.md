# Phase 9 — Portfolio Insights Dashboard Documentation

This combined document preserves the complete Phase 9 plan and every step document in order. Each source document is included in full below.

## Contents

1. [Phase 9 — Portfolio Insights Dashboard](#phase-9-plan)
2. [Phase 9.1 — Analyst Questions and Dashboard Success Criteria](#step-9-1)
3. [Phase 9.2 — Frontend Architecture Decision](#step-9-2)
4. [Phase 9.3 — Information Architecture and View Flow](#step-9-3)
5. [Phase 9.4 — Insight Calculation Contract](#step-9-4)
6. [Phase 9.5 — Build the Portfolio Overview](#step-9-5)
7. [Phase 9.6 — Risk Distribution and Cohort Exploration](#step-9-6)
8. [Phase 9.7 — Explain Review Capacity and Queue Construction](#step-9-7)
9. [Phase 9.8 — Compare Selected and Not Selected Customers](#step-9-8)
10. [Phase 9.9 — Feature and Repayment-Pattern Insights](#step-9-9)
11. [Phase 9 · Step 9.10: Customer drilldown and local explanation](#step-9-10)
12. [Phase 9 · Step 9.11: Segment policy and responsible-use safeguards](#step-9-11)
13. [Phase 9 · Step 9.12: Analyst exports](#step-9-12)
14. [Phase 9 · Step 9.13: Accessibility and responsive polish](#step-9-13)
15. [Phase 9 · Step 9.14: Integration, validation, and closeout](#step-9-14)

---

<a id="phase-9-plan"></a>
## Phase 9 Plan

# Phase 9 — Portfolio Insights Dashboard

## Purpose

Phase 8 established a working FastAPI scoring service and a basic Streamlit
upload-and-results page. Phase 9 will turn that first version into a polished
analyst workspace with multiple views, interactive visual analysis, useful
portfolio summaries, and customer-level drilldown.

The dashboard must help an analyst understand **who is in the uploaded
portfolio, how the model ranked them, how review capacity affects the queue,
and what patterns are visible in the data**. The insights in this phase are
computed from the supplied customer records, model scores, and existing
explainability methods. They are descriptive; they do not establish causes,
intervention effectiveness, or future savings.

This phase is deliberately non-GenAI. Every number, chart, filter, and
explanation should be reproducible from the data and model outputs. Phase 10
can add natural-language interaction after the dashboard's information
architecture and trusted calculations are settled. Deployment to the user's
cloud Droplet remains the final project phase, Phase 11.

## Working rules and current completion authorization

The phase was initially executed one approved step at a time, with detailed
walkthrough documents and concise implementation summaries. For remaining
steps 9.10–9.14, the user explicitly authorized completing the whole remainder
in one pass using the agent's recommendations. The selections recorded below
are the recommendations applied to this authorized completion.

## Proposed steps

### 9.1 Define analyst questions and dashboard success criteria · Complete

**Purpose:** Decide what an analyst should learn or do in each dashboard
view. Translate “lots of insights” into an ordered set of decisions and
questions, rather than a collection of unrelated charts.

**Candidate questions:**

- What is the size and overall predicted-risk profile of this portfolio?
- How are predicted probabilities distributed, and how many customers fall
  into each clearly defined risk band?
- How much review capacity was requested, how much was used, and who entered
  the queue?
- How do selected customers differ descriptively from those not selected?
- Which input patterns and model-supported drivers are associated with high
  scores in this particular portfolio?
- What should an analyst inspect next, and what limitations apply?

**Options:** Keep the current narrow scoring task and add only charts directly
supporting it; broaden the product to a full portfolio-analysis workspace;
or define an executive overview plus a deeper analyst exploration area. The
recommended starting point is the third option: a compact overview, with
separate drilldown views for detailed analysis. This keeps the first screen
readable while making room for the requested breadth.

**Deliverable:** agreed analyst personas, questions, key metrics, out-of-scope
claims, and acceptance criteria for the phase.

**Decision recorded:** Option C, a concise portfolio overview with deeper
exploration views. The detailed decision and success criteria are in
[Step 9.1](portfolio_insights_dashboard.md#step-9-1).

### 9.2 Choose the frontend architecture · Complete

The existing API remains the scoring and decision boundary. The main choice
is how much of the dashboard presentation layer to replace or extend.

| Option | Advantages | Costs and risks | When it fits |
| --- | --- | --- | --- |
| A. Expand Streamlit | Reuses the current application and Python skills; fastest path to filters, pages, and charts; fewest new tools. | Less control over fine-grained layout and interaction; complex visual workflows may feel constrained. | Choose if rapid delivery and Python-only maintenance matter most. |
| B. Build a custom React + TypeScript frontend over FastAPI | Strong control over layout, navigation, responsive behavior, visual polish, and client-side interactions; keeps the existing API reusable. | Adds a frontend toolchain, JavaScript/TypeScript code, dependency management, and a separate development workflow. | Recommended if the agreed design requires a cohesive, highly interactive analyst product. |
| C. Migrate gradually while retaining Streamlit as a fallback | Allows comparison and lower-risk transition; existing dashboard remains usable while custom views are built. | Temporarily maintains two clients and duplicates some interaction work. | Choose if a custom frontend is desired but migration risk should be staged. |

**Decision recorded:** custom HTML, CSS, and JavaScript frontend over the
existing FastAPI service. Streamlit will be replaced, with no parallel
fallback dashboard. The user wants the interface to feel stylish and easy on
the eyes. See
[Step 9.2](portfolio_insights_dashboard.md#step-9-2).

The main tradeoff is that vanilla JavaScript keeps the frontend stack light,
but requires disciplined modules and state management as views and
interactions grow. A charting library remains possible; it will be discussed
when the chart and design choices are made.
No API or frontend migration is pre-approved by this plan.

**Deliverable:** selected frontend approach, charting approach, repository
layout, local development workflow, and API responsibilities.

### 9.3 Design the information architecture and visual system · Complete

**Purpose:** Define navigation, page hierarchy, reusable components, and a
coherent visual language before building a large dashboard.

**Candidate views:**

1. **Portfolio overview:** essential counts, score profile, and capacity
   summary.
2. **Portfolio exploration:** searchable/filterable customers, risk bands,
   distributions, and segment comparisons.
3. **Review queue:** selected customers, queue reasons, capacity use, ties,
   and downloads.
4. **Customer detail:** one customer's score, input profile, and supported
   explanation.
5. **Model and data notes:** model version, input coverage, definitions,
   validation warnings, and interpretation limits.

**Options:** one long page with sections; a multi-page dashboard; or a
single-page overview with tabs/drawers for details. Recommend multi-view
navigation if Step 9.1 confirms all of the above questions, with the overview
as the default landing page. A long scroll page is simpler but can bury
important insights.

**Deliverable:** agreed page map, low-fidelity wireframes, component inventory,
responsive behavior, color and typography rules, and accessibility targets.

**Navigation direction selected:** sidebar navigation with separate views.
The analyst flow, intent for each view, and state-preservation rules are
recorded in
[Step 9.3](portfolio_insights_dashboard.md#step-9-3).
The user selected a calm light theme with an explicit easy-on-the-eyes
requirement. Text and chart contrast must remain strong; risk colors will be
restrained and paired with labels. Exact design tokens remain for wireframing.

### 9.4 Establish insight definitions and calculation contracts · Complete

**Purpose:** Specify exact definitions before drawing charts so the UI does
not imply more than the calculations establish.

Define, at minimum:

- probability display and rounding rules;
- whether risk bands are fixed business thresholds, quantiles, or analyst
  selected, and how band edges are labeled;
- population denominators for every percentage;
- queue selection counts, unused capacity, and tie handling;
- selected-versus-not-selected comparison rules;
- missing-value and invalid-file behavior;
- minimum group sizes for segment views;
- treatment of duplicate identifiers and filtered populations.

**Options:** compute derived summaries in the frontend, add deterministic
summary operations to the API, or put reusable analytics functions in the
Python package and expose selected results through the API. Recommend keeping
shared business definitions in tested Python service/package logic and
returning clear data contracts, while leaving presentation-only formatting
to the frontend. The final boundary depends on the Step 9.2 architecture.

**Deliverable:** metric glossary, definitions, example payloads, and a record
of which calculations belong to the API, shared Python logic, or browser.

**Decision recorded:** reuse the fixed Phase 6 validation-derived risk bands
and calculate score summaries in the FastAPI service. The packaged model
reproduces the reference cut points. The response schema, formulas, and
interpretation limits are documented in
[Step 9.4](portfolio_insights_dashboard.md#step-9-4).

### 9.5 Build the portfolio overview · Complete

**Purpose:** Let analysts understand a scoring run at a glance before
exploring individual records.

**Candidate content:** portfolio size; average and median predicted risk;
score distribution; counts and percentages by documented risk band; requested
review capacity; selected count; unused capacity; and a short explanation of
how the queue was formed. Show model and run metadata where available.

**Options:** KPI cards plus a distribution chart; an overview table plus
charts; or a narrative-like page assembled from deterministic labels and
metrics. Recommend a small number of prominent metrics with distribution and
capacity visuals beneath them. Avoid a wall of cards and avoid converting
probability directly into expected loss or prevented defaults.

**Deliverable:** implemented overview with clear units, accessible labels,
empty/error/loading states, and links into detailed views.

**Decision recorded:** Option A, a compact overview with KPI cards, a fixed
risk-band distribution, and a review-capacity summary. The custom frontend is
served by FastAPI and uses the API as its source for scores, bands, and queue
calculations. The full walkthrough and code listings are in
[Step 9.5](portfolio_insights_dashboard.md#step-9-5).

### 9.6 Add risk distribution and cohort exploration · Complete

**Purpose:** Show how the portfolio's model scores and input patterns vary,
and let analysts investigate meaningful groups.

**Candidate interactions:** filter by score range, risk band, review status,
and supported categorical or numeric fields; compare group counts and score
distributions; search by customer ID; reset filters; and see filtered versus
full-portfolio denominators.

**Options:** client-side filtering after one complete response, server-side
filter/query endpoints, or a hybrid with bounded initial data and server-side
pagination. With the current 30,000-row ceiling, client-side exploration may
work, but actual browser responsiveness must be measured. Recommend starting
with the simplest architecture that supports 30,000 rows smoothly, then add
server-side pagination if profiling shows it is needed.

**Deliverable:** interactive exploration view with explicit filter state,
population denominators, and performance behavior measured at the cap.

**Decision recorded:** Option A, filter the complete scored portfolio in the
browser. The view includes score range, fixed risk band, review status, ID
search, input-field filters, group summaries, and paged customer rows. Group
shares use the filtered cohort; numeric comparison quartiles use the full
portfolio as stable boundaries. The detailed walkthrough is in
[Step 9.6](portfolio_insights_dashboard.md#step-9-6).

### 9.7 Explain review capacity and queue construction · Complete

**Purpose:** Make the decision logic visible, especially for analysts who
need to understand why the queue has its particular size.

Show requested review count, target count, actual selected count, unused
capacity, the ranking rule, and the policy for equal scores at the capacity
boundary. Add a cumulative ranked-risk or capacity curve if it can be defined
without implying causal impact. Support review-count changes and make clear
when results refresh.

**Options:** preserve API queue results as the only source of truth; duplicate
queue logic in the client; or have the API return additional deterministic
explanations about the queue. Recommend the API/shared decision engine remain
authoritative and add explanatory response fields only when the user approves
the contract change. Do not reimplement tie-handling in the browser.

**Deliverable:** capacity-focused view and API contract update, if needed,
with tests against the existing deterministic decision engine.

**Decision recorded:** Option A, explain the current API response. The view
shows requested and capped target counts, selected and unused capacity,
per-customer reason-code totals, and the API-ranked selected queue. It states
the descending-score and whole-tie-group policy, and clarifies that updated
capacity applies after the analyst runs the analysis again. No API contract
change or browser-side queue calculation was needed. The detailed walkthrough
is in [Step 9.7](portfolio_insights_dashboard.md#step-9-7).

### 9.8 Compare selected and non-selected customers descriptively · Complete

**Purpose:** Help analysts see the characteristics of customers the current
capacity rule selects, while keeping comparisons descriptive.

Candidate comparisons include score distributions, repayment-status
patterns, credit limits, recent bill and payment values, and selected
categories. Use medians, quantiles, counts, and distributions as appropriate;
make sample size and missingness visible. Label the groups based on the
current review policy, not as “good” and “bad” customers.

**Options:** unadjusted side-by-side summaries; normalized effect-size style
comparisons; or only score-based differences. Recommend simple side-by-side
descriptive statistics first, then consider standardized comparisons if
analysts can interpret them. These views do not estimate intervention impact
or explain why selection causes an outcome.

**Deliverable:** comparison view with definitions, denominators, small-sample
handling, and caveats close to the charts.

**Decision recorded:** Option A, side-by-side descriptive summaries. The
Review queue view now compares customers selected by the current capacity rule
with those not selected. Each group shows its count and share of the full
uploaded portfolio, then median, 25th–75th percentile range, full range, and
available/missing record counts for predicted risk, credit limit, age, and
per-customer averages across the six bill and payment fields. These profiles
are independent of Explore portfolio filters. Small groups remain visible
with exact counts and an interpretation note; no group is labeled good or bad,
and no standardized or causal claim is made. The calculations are in the
browser using fields already present in the scored customer records; the API
contract and queue logic did not change. See the complete
[Step 9.8](portfolio_insights_dashboard.md#step-9-8)
walkthrough.

### 9.9 Add feature and repayment-pattern insights · Complete

**Purpose:** Give analysts a way to inspect input patterns connected to
portfolio risk without overstating model or data evidence.

Possible visuals include observed bill/payment amounts across the available
monthly fields, repayment-status distributions, credit-limit distributions,
and model-supported global feature importance. Check the data dictionary
before labeling any field as a particular month or deriving a trend. Keep
historical repayment fields distinct from future behavior.

**Options:** use only descriptive distributions; combine descriptive
distributions with global model explanations; or add local explanations for
individuals in this step. Recommend portfolio-level descriptive analysis
plus clearly labeled global model drivers here, reserving customer-level
explanation UX for Step 9.10. Feature importance is not a causal driver.

**Deliverable:** feature-pattern view with verified field definitions and
labels distinguishing “observed in data” from “used by model.”

**Decision recorded:** Option B, descriptive portfolio patterns plus the
existing global permutation-importance reference. A new Feature insights view
shows repayment-status code distributions by month and monthly bill/payment
summaries for the uploaded portfolio, separately from the model's top ten
validation features. Month labels follow the project's data dictionary;
repayment codes remain uninterpreted input values. Model importance reports
the Phase 6 validation Average Precision change and standard deviation across
ten shuffles, with its cohort and method stated. These fixed model-reference
values are not recomputed for an upload; the dashboard configuration now
supplies the reviewed Phase 6 snapshot. The view distinguishes observed data
from model behavior and explains that importance is not causation or an
individual explanation. Complete code and the walkthrough are in
[Step 9.9](portfolio_insights_dashboard.md#step-9-9).

### 9.10 Build customer drilldown and supported explanations · Complete

**Purpose:** Let an analyst inspect one row behind an aggregate or queue
entry and understand the model-supported explanation available in the
project.

Use the existing Phase 6 explainability methods and display their defined
outputs faithfully. Include the score, rank, queue status/reason, relevant
input values, explanation scope, and model limitations. Clarify that an
explanation describes the model's behavior for this record; it does not
establish a causal reason for default.

**Options:** show only the existing grouped local explanation; show the
explanation with a fuller input profile; or add a simplified analyst summary
generated from deterministic explanation fields. Recommend the first two
options, and keep any natural-language generation for Phase 10.

**Deliverable:** customer detail view with traceable input/output mapping and
explanation caveats.

### 9.11 Review segment comparisons and responsible-use safeguards · Complete

**Purpose:** Evaluate whether aggregate views are understandable and avoid
using sensitive or sparse groups carelessly.

Decide whether demographic categories should appear in operational filters,
in a restricted diagnostic view, or not at all. If subgroup comparisons are
included, show counts and uncertainty context, suppress or warn on small
groups, and do not label differences as bias or fairness conclusions without
an agreed evaluation methodology. This step is an analytical safeguard, not
a legal-compliance certification.

**Options:** exclude sensitive attributes from dashboard analysis; provide
descriptive subgroup diagnostics; or implement a formal fairness evaluation
with defined metrics and review. Recommend discussing the project objective
and evidence before selecting; a raw score comparison alone is not a
fairness assessment.

**Deliverable:** approved segment-display policy, safeguards, and concise
interpretation notes.

### 9.12 Add export, saved views, and analyst workflow refinements · Complete

**Purpose:** Make insights usable in a real analyst review process.

Potential features include filtered CSV export, full-ranking export,
selected-queue export, saved filter presets, and clear run metadata. Preserve
the prediction-time input/output separation and avoid exporting historical
`DEFAULT` unless a later, explicitly approved evaluation workflow requires
it.

**Options:** exports only; exports plus browser-local saved views; or shared
server-side saved workspaces requiring persistence/authentication. Recommend
exports first; defer shared saved views until user identity, privacy, and
storage requirements are decided.

**Deliverable:** approved exports and workflow controls with clear scope and
no accidental leakage of unsupported fields.

### 9.13 Visual polish, accessibility, and responsive behavior · Complete

**Purpose:** Make the dashboard coherent and comfortable for extended analyst
use across common screen sizes.

Refine typography, spacing, contrast, chart legends, keyboard navigation,
screen-reader labels, table density, loading skeletons, empty states, errors,
and responsive layouts. Use color as an aid rather than the only way to
convey risk. Keep terminology consistent across charts, tables, downloads,
and decision documentation.

**Options:** adopt a component library with project-specific styling; build a
small custom component system; or use framework defaults with light styling.
Choose based on the Step 9.2 frontend. Recommend a restrained design system
with reusable patterns rather than one-off styling per page.

**Deliverable:** reviewed, accessible visual system applied consistently to
all agreed views.

### 9.14 Integrate, validate, and document the dashboard · Complete

**Purpose:** Verify the full analyst journey and ensure insight definitions
remain consistent from API to chart and export.

Validation should cover representative portfolios, empty and malformed
inputs, filters and denominators, ties at capacity, all exports, customer
drilldown, API failures, slow responses, and the 30,000-row maximum. Review
chart calculations against independent examples; test keyboard and responsive
behavior; profile dashboard rendering and API response sizes; and rerun the
existing scoring and decision suite after any contract changes. Include a
manual analyst walkthrough in addition to automated checks.

**Options:** verify a narrow feature set before each merge; run a full
end-to-end test suite at the end; or combine continuous focused checks with
an end-of-phase walkthrough. Recommend the combined approach to catch errors
early and still inspect the actual experience.

**Deliverable:** detailed implementation walkthroughs for each step, final
dashboard guide, verified automated checks, measured 30,000-row experience,
and a Phase 9 closeout documenting what the charts establish and what they
do not.

## Phase boundaries and sequence

- **Phase 8 complete:** scoring API and simple Streamlit dashboard remain a
  functional baseline.
- **Phase 9:** build the analyst insights experience. No GenAI-generated
  summaries or decisions are required to complete it.
- **Phase 10:** plan and implement a GenAI layer against stable dashboard
  metrics, explanation outputs, and analyst workflows.
- **Phase 11, final:** deploy the agreed application to the user's cloud
  Droplet, including security, operations, configuration, and capacity
  review.

Each step will be discussed and approved individually under the user's
step-by-step process. This plan selects no frontend framework, visual
threshold, API extension, or subgroup policy in advance.

---

<a id="step-9-1"></a>
## Step 9.1

# Phase 9.1 — Analyst Questions and Dashboard Success Criteria

## Decision

The user chose **Option C: an executive-style portfolio overview with deeper
analyst exploration views**. The dashboard should be easy to scan first, then
let analysts investigate the portfolio, review queue, and individual customer
records in more detail.

This is a product-scope decision. It does not select a frontend framework,
final metrics, risk-band thresholds, chart types, or API changes. Those remain
for later Phase 9 steps.

## Intended user and workflow

The primary user is an analyst reviewing an uploaded customer portfolio to
understand its predicted-risk profile and inspect the queue produced under an
explicit review capacity. The workflow begins with a validated portfolio and
ends with the analyst able to inspect the overview, explore relevant groups,
understand the capacity-based queue, and drill into a customer record.

The dashboard supports human review. It does not approve or reject credit,
select or execute an intervention, or claim that an intervention changes
customer outcomes.

## Questions the dashboard should answer

### Portfolio overview

- How many customer records were scored?
- What does the portfolio's predicted-risk distribution look like?
- How many records fall into each agreed risk band, once the band definitions
  are chosen in Step 9.4?
- What review capacity was requested, how many records were selected, and
  was any capacity unused because of the queue's tie-handling rule?

### Portfolio exploration

- How does the score distribution vary across analyst-selected filters or
  portfolio segments?
- What observed customer and repayment-input patterns appear in groups of
  interest?
- What is the denominator and sample size behind each displayed comparison?

### Queue and customer review

- Which records were selected under the current review capacity, and what
  deterministic queue reason applies?
- How does a selected customer's score and input profile compare with the
  overall portfolio?
- What model-supported explanation is available for an individual record,
  and what does that explanation not establish?

Metric formulas, supported filters, minimum segment sizes, risk bands, and
explanation wording are deliberately deferred to their relevant steps.

## Chosen information structure

The initial information architecture will have a concise overview and deeper
views. Candidate views are:

1. **Portfolio overview** — portfolio size, score profile, and review-capacity
   summary.
2. **Portfolio exploration** — filters, distributions, and descriptive
   comparisons across groups.
3. **Review queue** — selected records, ranking, capacity accounting, and
   queue explanations.
4. **Customer detail** — one record's score, rank/status, inputs, and
   supported local explanation.
5. **Model and data notes** — model identity, input definitions, validation
   notes, and interpretation limits.

These are candidate view responsibilities, not a final navigation or
wireframe. Step 9.3 will decide the page map and layout after the frontend
approach is discussed.

## Success criteria

The dashboard will be successful when an analyst can:

- understand the portfolio's size and broad predicted-risk profile from the
  landing view;
- determine how the supplied review capacity affected the queue, including
  ties and unused capacity;
- move from a portfolio-level observation to a filtered group or customer
  record without losing context;
- distinguish observed portfolio patterns from model explanations and from
  causal claims;
- identify the sample size, denominator, and metric definition for displayed
  comparisons;
- interpret charts and tables without relying on color alone; and
- export or inspect the relevant records through the workflows approved in
  later steps.

Quantitative performance, accessibility, export, and 30,000-row acceptance
criteria will be specified in the implementation and validation steps. This
decision does not invent thresholds for them.

## Alternatives considered

### A. Focus only on scoring and the review queue

This would be the quickest expansion of the current page and would keep the
scope tightly tied to the Phase 8 workflow. It would provide less portfolio
exploration than the user wants from the dashboard.

### B. Build a broad portfolio-analysis workspace all at once

This would cover the most analyses immediately. It carries a higher risk of
crowding the interface, increasing implementation complexity, and presenting
descriptive patterns without enough context.

### C. Overview plus deeper exploration — selected

This provides a readable entry point and room for detailed analysis. It
requires an agreed information hierarchy and takes more work than a small set
of charts, but best matches the user's goal of a visually rich dashboard with
many useful insights.

## What remains open

- Streamlit, custom React + TypeScript, or gradual migration (Step 9.2).
- Navigation, page map, wireframes, and design system (Step 9.3).
- Metric formulas, risk-band policy, denominator conventions, and calculation
  boundaries (Step 9.4).
- Specific charts, filters, subgroup safeguards, and exports (Steps 9.5–9.12).
- Accessibility and performance thresholds (Steps 9.13–9.14).

## Code changes

This step changes the product definition and documentation only. It adds no
application code because the analyst questions and success criteria need to
guide the upcoming architecture and design decisions before implementation.

---

<a id="step-9-2"></a>
## Step 9.2

# Phase 9.2 — Frontend Architecture Decision

## Decision

The user chose a custom frontend using **HTML, CSS, and JavaScript**, replacing
the current Streamlit presentation layer. The custom frontend will call the
existing FastAPI service, which remains responsible for model scoring and
deterministic review-queue logic. Streamlit will not be retained as a second
dashboard or fallback once the custom interface is implemented.

The visual requirement is a **stylish, eye-soothing analyst experience**.
The detailed visual system, navigation, charts, and page layout are for Step
9.3 and later; they are not selected by this architecture decision.

## What this means

- Keep FastAPI and its scoring/API contracts as the presentation-independent
  service boundary.
- Replace Streamlit as the dashboard UI with custom web pages and browser-side
  interactions written in HTML, CSS, and JavaScript.
- Organize JavaScript into focused modules for API calls, state, filters,
  rendering, and page behavior instead of growing one large script.
- Keep all model predictions and queue decisions in the existing Python API;
  browser code presents returned results and may perform only agreed
  presentation-level interactions.
- Select a charting approach and exact asset-serving/development workflow
  when those details are needed by the design and implementation steps.
- Do not maintain two live dashboard implementations after migration.

## Alternatives considered

### A. Continue expanding Streamlit

This would reuse the current UI and Python skills with less setup. It offers
less control over fine-grained layout and interactions for the broad,
polished analyst experience requested.

### B. Use React and TypeScript over FastAPI

This offers a structured component model and strong support for complex
client-side interactions. It adds a JavaScript framework, TypeScript, and a
larger frontend toolchain.

### C. Custom HTML/CSS/JavaScript over FastAPI — selected adaptation

The original gradual-migration option proposed keeping Streamlit as a
fallback. The user chose the custom frontend part but explicitly declined the
parallel Streamlit fallback. This gives full visual control and avoids
maintaining duplicate dashboards, while keeping the frontend stack lighter
than React.

## Tradeoff and implementation advice

Plain JavaScript is sufficient for a custom dashboard and can deliver the
requested visual quality. As the dashboard grows to include multiple views,
filters, tables, and charts, manually managed state and DOM updates can become
hard to maintain. To reduce that risk, keep modules small, define clear
frontend data/state boundaries, and add a framework only if implementation
shows that the vanilla approach is becoming difficult to reason about.

This is a practical tradeoff, not a reason to reject the user's choice. A
focused charting library may still be considered later; “HTML, CSS, and
JavaScript” does not require hand-drawing every visualization.

## Not decided here

- Navigation and page layout (Step 9.3).
- Color palette, typography, spacing, and component styling (Step 9.3).
- Chart library and individual visual encodings (Steps 9.3 and 9.5 onward).
- Exact static asset serving and local development workflow.
- Whether any additional API responses are needed for the agreed views.

These details will be discussed before implementation of the relevant step.

## Code changes

This step records the architecture choice and does not yet add or remove
application code. Streamlit remains in the current application until the
custom frontend is implemented in later Phase 9 steps; it is not planned as a
parallel or permanent fallback.

---

<a id="step-9-3"></a>
## Step 9.3

# Phase 9.3 — Information Architecture and View Flow

## Status

The user selected **sidebar navigation with separate views** and clarified
that the views must have a clear purpose and flow into one another. The
navigation and view-flow direction below records that decision. The visual
theme and detailed wireframes remain open, so Step 9.3 is not complete yet.

## Design principle

Every view should answer a distinct analyst question and offer a clear next
action. The analyst should keep the same uploaded portfolio and scoring
context while moving between views. Customer detail is a contextual drilldown,
not a disconnected destination.

## Proposed analyst journey

```text
Start analysis
      ↓
Portfolio overview → Explore portfolio → Customer detail
      ↓                    ↓                    ↓
Review queue ─────────────┴────────────── Return to source context
      ↓
Model and data notes (available from every view)
```

The exact visual navigation treatment will be shown in the wireframes. The
intentional sequence is:

1. **Start Analysis** — upload the prediction-time CSV, validate it, set the
   review capacity, and run scoring. The analyst knows what portfolio is
   being analyzed and which capacity rule is applied.
2. **Portfolio Overview** — first results view. Answer “What does this
   portfolio look like, and what did the review-capacity rule produce?”
   Surface the population and score summary, agreed risk bands, and capacity
   accounting. Link to exploration and queue details.
3. **Explore Portfolio** — investigate descriptive patterns and segments.
   Filters change the rows being inspected and the displayed denominators;
   they do not silently redefine or rescore the full-portfolio review queue.
   Selecting a row opens its customer detail.
4. **Review Queue** — inspect customers selected by the API's deterministic
   review logic under the submitted full-portfolio capacity. Explain ranking,
   selection reasons, tie behavior, and unused capacity. Selecting a row
   opens its customer detail.
5. **Customer Detail** — inspect one customer's score, rank, queue status,
   input profile, and the existing model-supported explanation. Provide a
   direct return to the source view with its filters/search position intact.
6. **Model and Data Notes** — explain model identity, input meanings,
   validation, metric definitions, and interpretation limits. This is
   reference material, not a competing analysis workflow, and remains
   available from every view.

## View intent and transition table

| View | Main user question | Primary action | Entry and exit path |
| --- | --- | --- | --- |
| Start Analysis | What data and capacity am I asking the service to score? | Validate upload, choose capacity, run analysis | Entry point; successful scoring opens Overview |
| Portfolio Overview | What is the overall risk profile and queue result? | Choose Explore Portfolio or Review Queue | Default after a successful run |
| Explore Portfolio | Which groups or records should I inspect? | Filter, compare descriptive patterns, open a customer | From Overview; customer drilldown returns to the same filtered state |
| Review Queue | Who was selected and how did capacity affect selection? | Review selected rows and queue details; open a customer | From Overview; customer drilldown returns to the queue context |
| Customer Detail | What does the model and source data show for this record? | Inspect inputs and supported explanation | Opened from Explore or Queue; back returns to originating view and state |
| Model and Data Notes | How should I interpret the data, model, and metrics? | Read definitions and limitations | Reachable from all views; return to the same prior view |

## Context and state rules

- One active analysis supplies the portfolio and scoring outputs across all
  views. The dashboard must identify that active analysis clearly.
- Review capacity applies to the full submitted portfolio. Exploration
  filters are descriptive and must not cause a different queue unless the
  analyst explicitly starts a new analysis under a separately agreed
  workflow.
- Counts and percentages in a filtered view must identify whether they refer
  to the full portfolio or the filtered subset.
- Customer detail retains the source view, filters, search, and scroll or
  selection context when returning.
- Starting a new analysis replaces the active view context. Persistence,
  multiple saved analyses, and shared workspaces are not included unless
  approved in a later step.
- API failure or invalid input should preserve enough context for the analyst
  to correct the issue without losing their work.

## What remains to choose

## Visual theme decision

The user selected **Option A: a calm light theme**, with the additional
requirement that the interface be easy on the eyes. “Calm” means restrained
colors, clear visual hierarchy, and comfortable spacing; it must not mean
faint text or weak chart contrast.

The visual direction is warm neutral surfaces, readable dark text, and
restrained teal/blue accents. Risk and status colors should be used sparingly,
paired with text or icons, and remain distinguishable in tables and charts.
Avoid glaring white backgrounds and highly saturated decorative colors.
Specific color tokens, typography, and component styling remain for the
wireframe/design-system work.

### Other theme options considered

### A. Calm light theme — recommended

Warm off-white surfaces, dark slate text, restrained teal/blue accents, and
limited warm risk colors with labels and icons. This supports long analyst
sessions and a clear information hierarchy. Contrast still needs to meet
accessibility requirements.

### B. Dark theme

Deep neutral surfaces with muted highlights can feel focused and polished.
It can be tiring or reduce readability for dense tables and long sessions if
contrast and text weight are not tuned carefully.

### C. Light and dark themes

Gives analysts a personal choice, but doubles visual-system and accessibility
validation work. It is appropriate if user preference is a firm requirement;
otherwise it adds scope without improving the core analysis flow.

The exact palette, typography, spacing, chart colors, and wireframes will be
specified in the design-system work. The detailed chart library remains a
later implementation decision.

## Step completion

The sidebar structure, distinct purpose for each view, analyst journey,
context-preservation rules, and calm light visual direction are now agreed.
Detailed wireframes and exact design tokens will be produced alongside the
relevant implementation work; no frontend code was needed to settle this
design step.

## Code changes

This is a design and navigation decision; no application code is changed in
this step. The document records the flow constraints that the custom frontend
must follow.

---

<a id="step-9-4"></a>
## Step 9.4

# Phase 9.4 — Insight Calculation Contract

## Decision

The user chose **Option B**:

1. Reuse the fixed validation-derived risk bands documented in Phase 6.
2. Calculate portfolio summary metrics in the FastAPI service and include
   them in its review-queue response.

This keeps score summaries consistent between uploaded portfolios and makes
the API the single source for score, queue, capacity, and band calculations.
The browser will format and visualize these values; it will not independently
recompute the definitions.

## Compatibility check

Phase 6 defines four equal-frequency bands from validation probabilities of
the selected HistGradientBoosting model. The packaged model was scored on the
same validation partition as a compatibility check. It reproduced the exact
documented interior cut points:

| Band | Probability interval |
| --- | --- |
| Lower | `(-∞, 0.08940226956400625]` |
| Moderate | `(0.08940226956400625, 0.1444458140540088]` |
| Elevated | `(0.1444458140540088, 0.26307539734969276]` |
| Highest | `(0.26307539734969276, +∞)` |

The validation cohort contained 4,500 customers. These are descriptive
reference-cohort cut points, not business or action thresholds. They do not
change continuous-score ranking, review capacity, or queue membership. Tied
probabilities stay together because the intervals use the existing Phase 6
assignment rule.

If the model, feature set, or validation reference changes, the cut points
must be rechecked and versioned with that model before the dashboard uses
them.

## Summary definitions

The existing `POST /v1/review-queue` response now adds `portfolio_summary`.
The established `population_count`, `capacity`, and full `customers` list
remain in place.

### Probability summary

For all scored rows in the submitted portfolio, the API returns:

- `minimum` and `maximum` predicted default probabilities;
- `percentile_25` and `percentile_75`, using pandas' linear interpolation;
- `median`; and
- `mean`.

These are summaries of model estimates, not observed default rates, expected
loss, or intervention outcomes. The API returns numeric precision; the
frontend decides display formatting without changing the values.

### Risk-band counts and shares

The API returns all four fixed bands, including bands with zero customers.
For each band:

- `customer_count` is the number of submitted customers assigned to it;
- `portfolio_share` is `customer_count / population_count` for the complete
  submitted portfolio;
- `lower_bound_exclusive` is the inclusive interval's lower cut point under
  `p > lower`; it is `null` for the first open-ended band;
- `upper_bound_inclusive` is the upper cut point under `p <= upper`; it is
  `null` for the final open-ended band.

The four shares sum to 1.0, subject to floating-point representation.
Percentages shown by the browser must name the full portfolio as denominator.
Portfolio filters will not recompute these canonical bands or change the
full-population denominator; filtered-view denominators will be explicitly
defined when the exploration view is implemented.

### Method and reference labels

`risk_band_method` is `fixed_validation_cohort_quantiles`.
`risk_band_reference` says the bands were derived from Phase 6 validation
probabilities for the locked HistGradientBoosting engineered-feature model.
The frontend should expose this interpretation alongside the band chart or
in a clearly reachable explanation.

## API response shape

The new response section is:

```json
{
  "portfolio_summary": {
    "probability_summary": {
      "minimum": 0.2,
      "percentile_25": 0.35,
      "median": 0.5,
      "mean": 0.5333333333333333,
      "percentile_75": 0.7,
      "maximum": 0.9
    },
    "risk_band_method": "fixed_validation_cohort_quantiles",
    "risk_band_reference": "Phase 6 validation probabilities from the locked HistGradientBoosting engineered-feature model",
    "risk_bands": [
      {
        "label": "Lower",
        "customer_count": 0,
        "portfolio_share": 0.0,
        "lower_bound_exclusive": null,
        "upper_bound_inclusive": 0.08940226956400625
      }
    ]
  }
}
```

The API response model validates this summary before returning it. There is
no new endpoint and no database. The API service computes summaries from the
same probabilities it uses to build the queue.

## Implementation walkthrough

### Fixed Phase 6 definition

`src/propensity_prediction/explainability/risk_segmentation.py` now exposes
the verified cut points and a reusable fixed definition:

```python
VALIDATION_RISK_BAND_CUT_POINTS = (
    0.08940226956400625,
    0.1444458140540088,
    0.26307539734969276,
)
VALIDATION_RISK_BAND_LABELS = ("Lower", "Moderate", "Elevated", "Highest")


def validation_risk_band_definition() -> RiskBandDefinition:
    return RiskBandDefinition(
        edges=(-np.inf, *VALIDATION_RISK_BAND_CUT_POINTS, np.inf),
        labels=VALIDATION_RISK_BAND_LABELS,
        requested_bands=DEFAULT_N_BANDS,
    )
```

The existing `fit_risk_bands()` remains the analysis function that derives
bands from a reference cohort. The new helper applies the already agreed
Phase 6 definition to inference-time probabilities without fitting new
cut points on each uploaded portfolio.

### Response models

`src/propensity_prediction/api/schemas.py` defines strict response structures:

```python
class ProbabilitySummary(BaseModel):
    minimum: float = Field(ge=0, le=1)
    percentile_25: float = Field(ge=0, le=1)
    median: float = Field(ge=0, le=1)
    mean: float = Field(ge=0, le=1)
    percentile_75: float = Field(ge=0, le=1)
    maximum: float = Field(ge=0, le=1)


class RiskBandSummary(BaseModel):
    label: str
    customer_count: int = Field(ge=0)
    portfolio_share: float = Field(ge=0, le=1)
    lower_bound_exclusive: float | None = Field(default=None, ge=0, le=1)
    upper_bound_inclusive: float | None = Field(default=None, ge=0, le=1)


class PortfolioSummary(BaseModel):
    probability_summary: ProbabilitySummary
    risk_band_method: Literal["fixed_validation_cohort_quantiles"]
    risk_band_reference: str
    risk_bands: list[RiskBandSummary]
```

`ReviewQueueResponse` includes this as `portfolio_summary` alongside the
existing population, capacity, and customer results.

### Service calculation

`ReviewQueueService.build_queue()` scores each customer once, builds the
existing deterministic queue, then uses those same probabilities for the
summary:

```python
risk_band_definition = validation_risk_band_definition()
assigned_bands = assign_risk_bands(probabilities, risk_band_definition)
probability_series = pd.Series(probabilities, dtype=float)

probability_summary = {
    "minimum": float(probability_series.min()),
    "percentile_25": float(probability_series.quantile(0.25)),
    "median": float(probability_series.median()),
    "mean": float(probability_series.mean()),
    "percentile_75": float(probability_series.quantile(0.75)),
    "maximum": float(probability_series.max()),
}
```

It walks the fixed label order to return a stable four-item array, counts each
band, calculates each full-portfolio share, and represents open-ended
intervals with `null` bounds. It does not use actual `DEFAULT` outcomes.

## Validation

The API and risk-segmentation tests check that:

- the packaged inference model reproduces the documented validation cut
  points (compatibility check performed during implementation);
- summary statistics match known scores;
- all four labels are returned with correct counts and shares;
- the response passes `ReviewQueueResponse` validation; and
- the existing queue ordering and tie behavior are unchanged.

Focused checks:

```bash
venv/bin/python -m pytest tests/test_api_review_queue.py tests/test_risk_segmentation.py
```

Result: **23 passed**.

## Not included in this step

Selected-versus-not-selected comparisons, filtered-view aggregations,
histograms, segment minimum sizes, and customer-specific explanation display
remain for their later steps. The new response contract establishes the
portfolio-wide score and risk-band summaries those views can build on.

---

<a id="step-9-5"></a>
## Step 9.5

# Phase 9.5 — Build the Portfolio Overview

## Decision and scope

The user chose **Option A**: a compact overview with a small set of KPI cards, fixed risk-band distribution, and review-capacity summary. The page is the first landing view in the custom HTML/CSS/JavaScript dashboard. It uploads a prediction-time CSV, validates it in the browser against rules exposed by FastAPI, requests scores from the existing review-queue endpoint, and displays deterministic API output.

The overview deliberately avoids expected-loss estimates, causal conclusions, and action thresholds. The next views remain visibly marked as upcoming.

**Visual correction:** the risk-band fill elements now use `display: block`, allowing their API-derived percentage widths to render. Inline spans ignore the intended bar height/width presentation, which caused the empty tracks in the first browser view.

## What changed and why

1. **FastAPI serves the dashboard.** Static HTML/CSS/JavaScript is mounted at `/`; the API remains the model and decision boundary. Static files are included in the Python package so an installed build can serve the same interface.
2. **The browser reads canonical upload requirements.** `GET /v1/dashboard-config` returns the 30,000-row cap and the `CustomerInput` fields, preventing the UI from defining a second column contract.
3. **CSV validation gives early, row-specific feedback.** The browser handles quoted CSV fields, validates exact headers, numeric domains, missing values, unique IDs, the row cap, and rejects `DEFAULT` because it is an outcome, not a prediction-time input. FastAPI validates the submitted structured request again.
4. **Scoring uses the established endpoint.** The browser sends parsed customer rows and review capacity to `POST /v1/review-queue`. It does not score or rank records itself.
5. **The overview renders four KPIs, four API-defined risk bands, and a capacity graphic.** Counts, shares, score summaries, and queue outcomes come from the API response. Browser code formats and visualizes these values only.
6. **The visual system is calm and responsive.** Semantic sections, keyboard focus styling, status announcements, reduced-motion behavior, responsive layout, and accessible labels support use across screen sizes.

## Reading the page

- **Customers scored** and **mean predicted risk** describe the whole uploaded portfolio. The mean is a model estimate, not an observed default rate.
- **Selected for review** and **unused capacity** describe the tie-aware queue response. A tie at the selection boundary can leave capacity unused.
- **Predicted risk bands** are fixed from the Phase 6 validation cohort. They describe relative reference-cohort position and do not set action thresholds or change queue selection.
- **Review capacity** shows selected divided by the API's target count. If the target is zero, the display is undefined (`—`) rather than dividing by zero.
- The interpretation note says these are model estimates and descriptive patterns, not outcomes, expected losses, or evidence that interventions change outcomes.

## Detailed code walkthrough

### 1. Page structure (`index.html`)

The page has a persistent sidebar, top bar, title and purpose statement, upload/capacity form, results section, interpretation note, and empty state. The results section starts hidden so an analyst sees a clear next action. Sidebar entries for exploration and queue views are placeholders until those steps are implemented. The form uses native controls and labels; status and validation messages have live-region semantics.

### 2. Styling (`styles.css`)

CSS custom properties define the warm neutral canvas, white surfaces, readable ink, muted teal accent, restrained band colors, borders, radii, and shadow. Layout uses grid and flexbox; breakpoints collapse the sidebar and cards on narrow screens. `:focus-visible` keeps keyboard navigation visible, and a reduced-motion media query removes nonessential animation. Risk bands also carry text labels and counts, so color is not the only encoding.

### 3. Browser logic (`app.js`)

- `parseCsv` is a small state-machine parser supporting quoted fields, escaped quotes, commas inside quotes, CRLF/LF line endings, and a UTF-8 BOM. Malformed quoting produces a direct error.
- `validateCsvRows` checks duplicate headers, exact canonical headers from the config endpoint, at least one record, row cap, per-row field count, blank cells, numeric type/range rules, and unique IDs. The outcome column `DEFAULT` is explicitly rejected.
- `loadDashboardConfig` reads the API's row cap and required columns and uses them for validation and the upload hint.
- `checkService` uses `/health` and indicates whether the model is loaded.
- Form submission validates the file and review capacity, posts the structured request, handles API errors, then calls the rendering functions. The button is disabled during the request and restored in `finally`, including on failure.
- `renderMetricCards`, `renderRiskBands`, and `renderCapacity` format response values and build DOM nodes. Risk fills are clamped to 0–100%; capacity utilization is clamped and guarded for a zero target. Queue tie behavior is explained using the API's returned capacity fields.
- `renderOverview` reveals results and hides the empty state only after successful scoring.

### 4. API and packaging

`DashboardConfigResponse` describes the canonical browser configuration. The route derives required columns directly from `CustomerInput.model_fields` and imports the shared maximum row count. FastAPI mounts packaged static assets at `/` after registering API routes. `dashboard/__init__.py` exposes the static directory path; package-data includes HTML, CSS, and JS files.

## Complete code for this step

The following listings are the complete contents of the files created or modified for Step 9.5. Some files also contain earlier API functionality; they are included whole so the implementation can be followed without omitted sections.


### `src/propensity_prediction/dashboard/static/index.html`

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#f4f7f4" />
    <meta
      name="description"
      content="Understand a scored customer portfolio and its review capacity."
    />
    <title>Portfolio overview | Credit risk review</title>
    <link rel="stylesheet" href="/styles.css" />
    <script src="/app.js" defer></script>
  </head>
  <body>
    <div class="app-shell">
      <aside class="sidebar" aria-label="Dashboard navigation">
        <a class="brand" href="/" aria-label="Portfolio review home">
          <span class="brand-mark" aria-hidden="true">P</span>
          <span class="brand-copy">
            <strong>Portfolio</strong>
            <span>Risk review</span>
          </span>
        </a>

        <p class="nav-label">WORKSPACE</p>
        <nav class="primary-nav" aria-label="Primary">
          <a class="nav-link is-active" href="#overview" aria-current="page">
            <span class="nav-icon" aria-hidden="true">▦</span>
            <span>Overview</span>
          </a>
          <span class="nav-link is-disabled" aria-disabled="true">
            <span class="nav-icon" aria-hidden="true">⌕</span>
            <span>Explore portfolio</span>
            <span class="nav-soon">NEXT</span>
          </span>
          <span class="nav-link is-disabled" aria-disabled="true">
            <span class="nav-icon" aria-hidden="true">≡</span>
            <span>Review queue</span>
            <span class="nav-soon">NEXT</span>
          </span>
        </nav>

        <div class="sidebar-bottom">
          <div class="sidebar-note">
            <span class="note-icon" aria-hidden="true">i</span>
            <p>Predicted risk helps prioritize review. It is not an outcome or an action recommendation.</p>
          </div>
          <span class="service-status" id="service-status" role="status">
            <span class="status-dot" aria-hidden="true"></span>
            Checking scoring service
          </span>
        </div>
      </aside>

      <main class="main-content" id="overview">
        <header class="topbar">
          <div class="breadcrumb">Workspace <span aria-hidden="true">/</span> Overview</div>
          <div class="topbar-actions">
            <button class="text-button" id="health-check" type="button">Check service</button>
            <span class="avatar" aria-hidden="true">AR</span>
          </div>
        </header>

        <section class="page-heading" aria-labelledby="page-title">
          <div>
            <p class="eyebrow">PORTFOLIO INSIGHTS</p>
            <h1 id="page-title">Portfolio overview</h1>
            <p class="page-description">A clear view of predicted risk and review capacity for your customer portfolio.</p>
          </div>
          <div class="analysis-meta" id="analysis-meta" hidden>
            <span class="meta-dot" aria-hidden="true"></span>
            <span id="analysis-meta-text">Analysis complete</span>
          </div>
        </section>

        <section class="analysis-panel" aria-labelledby="analysis-title">
          <div class="analysis-panel-copy">
            <span class="step-badge">NEW ANALYSIS</span>
            <h2 id="analysis-title">Start with a customer portfolio</h2>
            <p>Upload a prediction-time CSV, set your review capacity, and score the full portfolio.</p>
          </div>
          <form id="analysis-form" class="analysis-form">
            <label class="file-drop" for="portfolio-file">
              <span class="upload-icon" aria-hidden="true">↑</span>
              <span class="file-drop-copy">
                <strong id="file-name">Choose a CSV file</strong>
                <span id="file-hint">ID and all 23 predictors · up to 30,000 customers</span>
              </span>
              <span class="browse-button">Browse files</span>
            </label>
            <input id="portfolio-file" class="visually-hidden" type="file" accept=".csv,text/csv" />
            <div class="form-actions">
              <label class="capacity-field" for="review-capacity">
                <span>Review capacity</span>
                <span class="capacity-input-wrap">
                  <input id="review-capacity" type="number" min="0" step="1" value="10" inputmode="numeric" />
                  <span>customers</span>
                </span>
              </label>
              <button class="primary-button" id="run-analysis" type="submit">
                <span>Run analysis</span><span aria-hidden="true">→</span>
              </button>
            </div>
            <p class="form-message" id="form-message" role="alert" hidden></p>
          </form>
        </section>

        <section class="results-section" id="results-section" aria-labelledby="results-title" hidden>
          <div class="section-heading">
            <div>
              <p class="eyebrow">AT A GLANCE</p>
              <h2 id="results-title">Portfolio snapshot</h2>
              <p class="section-description">Summary of model estimates for the full uploaded portfolio.</p>
            </div>
            <span class="portfolio-count" id="portfolio-count"></span>
          </div>

          <div class="metric-grid" id="metric-grid" aria-label="Portfolio summary metrics"></div>

          <div class="insight-grid">
            <article class="card band-card" aria-labelledby="bands-title">
              <div class="card-heading">
                <div>
                  <h3 id="bands-title">Predicted risk bands</h3>
                  <p>How customers are distributed across the fixed reference bands.</p>
                </div>
                <span class="chart-mark" aria-hidden="true">▥</span>
              </div>
              <div class="band-list" id="risk-band-chart" role="list"></div>
              <details class="chart-note">
                <summary>How to read these bands</summary>
                <p id="risk-band-reference"></p>
                <p>These bands describe relative predicted risk. They are not action thresholds and do not change queue selection.</p>
              </details>
            </article>

            <article class="card capacity-card" aria-labelledby="capacity-title">
              <div class="card-heading">
                <div>
                  <h3 id="capacity-title">Review capacity</h3>
                  <p>How the requested capacity translated into the queue.</p>
                </div>
                <span class="chart-mark capacity-mark" aria-hidden="true">◎</span>
              </div>
              <div class="capacity-visual">
                <div class="capacity-ring" id="capacity-ring" aria-label="Capacity utilization">
                  <div class="ring-center">
                    <strong id="capacity-percent">0%</strong>
                    <span>of target selected</span>
                  </div>
                </div>
                <div class="capacity-legend" id="capacity-legend"></div>
              </div>
              <div class="capacity-footnote" id="capacity-footnote"></div>
            </article>
          </div>

          <div class="interpretation-note">
            <span class="note-icon" aria-hidden="true">i</span>
            <p><strong>Interpretation:</strong> Predicted probabilities summarize model estimates, not observed outcomes or expected losses. Portfolio patterns are descriptive and do not show that an intervention will change outcomes.</p>
          </div>
        </section>

        <section class="empty-state" id="empty-state" aria-labelledby="empty-title">
          <div class="empty-illustration" aria-hidden="true">
            <span class="illustration-card card-one"></span>
            <span class="illustration-card card-two"></span>
            <span class="illustration-chart"><i></i><i></i><i></i><i></i></span>
          </div>
          <h2 id="empty-title">Your portfolio overview will appear here</h2>
          <p>Upload a customer file above to see the portfolio summary and review-capacity breakdown.</p>
        </section>

        <footer class="page-footer">
          <span>Credit risk review · Analyst workspace</span>
          <span>Model estimates support review prioritization only</span>
        </footer>
      </main>
    </div>
  </body>
</html>

```

### `src/propensity_prediction/dashboard/static/styles.css`

```css
:root {
  color-scheme: light;
  --canvas: #f4f7f4;
  --surface: #ffffff;
  --surface-muted: #f8faf8;
  --ink: #263a36;
  --ink-strong: #1a302b;
  --ink-muted: #62746f;
  --ink-soft: #7c8b86;
  --line: #e1e9e4;
  --line-strong: #d1ded7;
  --teal: #287c70;
  --teal-dark: #1f685e;
  --teal-soft: #e6f1ed;
  --blue: #6487a2;
  --blue-soft: #eaf0f5;
  --amber: #aa7740;
  --amber-soft: #f5eee3;
  --rose: #a45f62;
  --rose-soft: #f5e9e8;
  --shadow: 0 10px 30px rgb(36 63 53 / 5%);
  --radius: 18px;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
}

* { box-sizing: border-box; }

body {
  min-width: 320px;
  min-height: 100vh;
  margin: 0;
  background: var(--canvas);
  color: var(--ink);
  font-size: 14px;
  line-height: 1.55;
}

button, input { font: inherit; }
button { color: inherit; }
a { color: inherit; }
[hidden] { display: none !important; }

:focus-visible {
  outline: 3px solid #75a99d;
  outline-offset: 3px;
}

.app-shell { min-height: 100vh; }

.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 5;
  display: flex;
  width: 248px;
  flex-direction: column;
  padding: 26px 18px 20px;
  border-right: 1px solid var(--line);
  background: #fbfcfa;
}

.brand {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 2px 8px 28px;
  text-decoration: none;
}

.brand-mark {
  display: grid;
  width: 39px;
  height: 39px;
  place-items: center;
  border-radius: 13px;
  background: var(--teal-dark);
  color: #fff;
  font-family: "Manrope", sans-serif;
  font-size: 19px;
  font-weight: 800;
}

.brand-copy { display: grid; line-height: 1.25; }
.brand-copy strong { color: var(--ink-strong); font-size: 15px; font-weight: 700; }
.brand-copy span { margin-top: 3px; color: var(--ink-muted); font-size: 11px; }

.nav-label, .eyebrow {
  color: var(--ink-soft);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .12em;
}

.nav-label { margin: 0 10px 10px; }
.primary-nav { display: grid; gap: 5px; }

.nav-link {
  display: flex;
  min-height: 44px;
  align-items: center;
  gap: 11px;
  padding: 0 11px;
  border-radius: 10px;
  color: #566963;
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
}

.nav-link.is-active {
  background: var(--teal-soft);
  color: #245f55;
  font-weight: 700;
}

.nav-icon {
  display: inline-grid;
  width: 22px;
  place-items: center;
  color: currentColor;
  font-size: 18px;
  line-height: 1;
}

.nav-link.is-disabled { color: #77857f; cursor: not-allowed; }
.nav-soon {
  margin-left: auto;
  color: #77857f;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: .08em;
}

.sidebar-bottom { display: grid; gap: 17px; margin-top: auto; }
.sidebar-note, .interpretation-note {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  border: 1px solid #dfe9e3;
  background: #f1f6f2;
  color: #475d55;
}

.sidebar-note { padding: 12px 11px; border-radius: 12px; }
.sidebar-note p, .interpretation-note p { margin: 0; font-size: 11px; line-height: 1.55; }
.note-icon {
  display: inline-grid;
  width: 18px;
  height: 18px;
  flex: 0 0 auto;
  place-items: center;
  border: 1px solid #9bb5a9;
  border-radius: 50%;
  color: #3f6d5d;
  font-size: 11px;
  font-weight: 700;
}

.service-status { display: flex; align-items: center; gap: 8px; padding: 0 7px; color: var(--ink-muted); font-size: 11px; }
.status-dot, .meta-dot { width: 8px; height: 8px; border-radius: 50%; background: #b3c0b9; }
.service-status.is-ready .status-dot { background: #38876d; box-shadow: 0 0 0 3px #e2f0e8; }
.service-status.is-error .status-dot { background: #a45f62; box-shadow: 0 0 0 3px #f5e9e8; }

.main-content { max-width: 1540px; min-height: 100vh; margin-left: 248px; padding: 0 44px 24px; }
.topbar { display: flex; height: 72px; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--line); }
.breadcrumb { color: var(--ink-muted); font-size: 12px; }
.breadcrumb span { margin: 0 7px; color: #9aa8a2; }
.topbar-actions { display: flex; align-items: center; gap: 16px; }
.text-button { padding: 6px 2px; border: 0; background: transparent; color: #4c665e; cursor: pointer; font-size: 12px; font-weight: 600; }
.text-button:hover { color: var(--teal-dark); }
.avatar { display: grid; width: 31px; height: 31px; place-items: center; border: 1px solid #dce5df; border-radius: 50%; background: #e9f0eb; color: #426257; font-size: 10px; font-weight: 700; }

.page-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; padding: 31px 0 22px; }
.page-heading .eyebrow, .section-heading .eyebrow { margin: 0 0 6px; }
h1, h2, h3, p { margin-top: 0; }
h1, h2, h3 { color: var(--ink-strong); font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
h1 { margin-bottom: 6px; font-size: clamp(24px, 2.4vw, 32px); font-weight: 700; letter-spacing: -.04em; line-height: 1.2; }
.page-description { margin: 0; color: var(--ink-muted); font-size: 13px; }
.analysis-meta { display: inline-flex; align-items: center; gap: 8px; padding: 7px 11px; border: 1px solid var(--line); border-radius: 99px; background: var(--surface); color: #50665e; font-size: 11px; white-space: nowrap; }
.analysis-meta .meta-dot { background: #3c8a6f; }

.analysis-panel {
  display: grid;
  grid-template-columns: minmax(220px, .78fr) minmax(380px, 1.45fr);
  gap: 28px;
  padding: 22px 24px;
  border: 1px solid #dce7e0;
  border-radius: var(--radius);
  background: linear-gradient(116deg, #edf4ef, #f9fbf8 65%);
  box-shadow: var(--shadow);
}

.analysis-panel-copy { align-self: center; }
.step-badge { display: inline-block; margin-bottom: 9px; color: #4e7d6e; font-size: 9px; font-weight: 700; letter-spacing: .13em; }
.analysis-panel h2 { margin: 0 0 6px; font-size: 17px; letter-spacing: -.025em; }
.analysis-panel-copy p { max-width: 330px; margin: 0; color: var(--ink-muted); font-size: 12px; line-height: 1.6; }
.analysis-form { display: grid; align-content: center; gap: 12px; }
.file-drop { display: flex; min-height: 70px; align-items: center; gap: 12px; padding: 10px 12px; border: 1px dashed #aabeb2; border-radius: 12px; background: rgb(255 255 255 / 76%); cursor: pointer; }
.file-drop:hover, .file-drop:focus-within { border-color: var(--teal); background: #fff; }
.upload-icon { display: grid; width: 38px; height: 38px; flex: 0 0 auto; place-items: center; border-radius: 11px; background: #e7f1eb; color: #3d7461; font-size: 22px; font-weight: 500; }
.file-drop-copy { display: grid; min-width: 0; gap: 3px; }
.file-drop-copy strong { overflow: hidden; color: var(--ink-strong); font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.file-drop-copy span { color: var(--ink-muted); font-size: 10px; }
.browse-button { margin-left: auto; padding: 7px 10px; border: 1px solid var(--line-strong); border-radius: 8px; background: #fff; color: #395b50; font-size: 10px; font-weight: 700; white-space: nowrap; }
.visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; clip-path: inset(50%); }
.form-actions { display: flex; align-items: flex-end; justify-content: space-between; gap: 14px; }
.capacity-field { display: grid; gap: 5px; color: #536760; font-size: 10px; font-weight: 600; }
.capacity-input-wrap { display: flex; height: 36px; align-items: center; gap: 8px; padding: 0 9px; border: 1px solid var(--line-strong); border-radius: 8px; background: #fff; color: var(--ink-muted); font-size: 10px; }
.capacity-input-wrap input { width: 78px; border: 0; outline: none; background: transparent; color: var(--ink-strong); font-size: 12px; font-weight: 600; }
.capacity-input-wrap input:focus-visible { outline: 2px solid #75a99d; outline-offset: 2px; }
.primary-button { display: inline-flex; min-height: 37px; align-items: center; justify-content: center; gap: 15px; padding: 0 15px; border: 1px solid var(--teal-dark); border-radius: 8px; background: var(--teal-dark); color: #fff; cursor: pointer; font-size: 11px; font-weight: 700; transition: background .15s ease, transform .15s ease; }
.primary-button:hover { transform: translateY(-1px); background: #19584f; }
.primary-button:disabled { cursor: wait; opacity: .72; transform: none; }
.form-message { margin: 0; color: #8b4448; font-size: 11px; line-height: 1.5; }
.form-message.is-success { color: #34735d; }

.results-section { padding-top: 31px; }
.section-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 18px; margin-bottom: 15px; }
.section-heading h2 { margin: 0 0 5px; font-size: 19px; letter-spacing: -.03em; }
.section-description { margin: 0; color: var(--ink-muted); font-size: 11px; }
.portfolio-count { padding: 6px 10px; border: 1px solid var(--line); border-radius: 99px; background: #fff; color: #587069; font-size: 10px; font-weight: 600; white-space: nowrap; }
.metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 13px; margin-bottom: 15px; }
.metric-card { min-height: 112px; padding: 16px 17px; border: 1px solid var(--line); border-radius: 14px; background: var(--surface); box-shadow: 0 5px 16px rgb(36 63 53 / 3%); }
.metric-card-top { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.metric-label { color: var(--ink-muted); font-size: 10px; font-weight: 600; }
.metric-icon { display: grid; width: 27px; height: 27px; place-items: center; border-radius: 9px; background: var(--teal-soft); color: #397366; font-size: 13px; }
.metric-card:nth-child(2) .metric-icon { background: var(--blue-soft); color: #597b96; }
.metric-card:nth-child(3) .metric-icon { background: var(--amber-soft); color: #8d6639; }
.metric-card:nth-child(4) .metric-icon { background: var(--rose-soft); color: #92575a; }
.metric-value { display: block; margin-top: 9px; color: var(--ink-strong); font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; font-size: 25px; font-weight: 700; letter-spacing: -.04em; line-height: 1.15; }
.metric-help { display: block; margin-top: 5px; color: var(--ink-soft); font-size: 9px; }

.insight-grid { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(300px, .85fr); gap: 15px; }
.card { min-width: 0; padding: 19px 20px 17px; border: 1px solid var(--line); border-radius: 15px; background: var(--surface); box-shadow: 0 5px 16px rgb(36 63 53 / 3%); }
.card-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 15px; margin-bottom: 18px; }
.card-heading h3 { margin: 0 0 4px; font-size: 14px; letter-spacing: -.02em; }
.card-heading p { margin: 0; color: var(--ink-muted); font-size: 10px; }
.chart-mark { display: grid; width: 30px; height: 30px; flex: 0 0 auto; place-items: center; border-radius: 9px; background: #edf4ef; color: #547c69; font-size: 17px; }
.capacity-mark { background: #edf1f5; color: #617b91; }
.band-list { display: grid; gap: 14px; }
.band-row { display: grid; grid-template-columns: 77px minmax(70px, 1fr) 58px; align-items: center; gap: 12px; }
.band-label { color: #4b6058; font-size: 10px; font-weight: 600; }
.band-track { height: 10px; overflow: hidden; border-radius: 99px; background: #edf1ee; }
.band-fill { display: block; height: 100%; min-width: 0; border-radius: inherit; transition: width .45s ease; }
.band-row[data-band="Lower"] .band-fill { background: #76a994; }
.band-row[data-band="Moderate"] .band-fill { background: #7894a8; }
.band-row[data-band="Elevated"] .band-fill { background: #c49a61; }
.band-row[data-band="Highest"] .band-fill { background: #b97778; }
.band-value { color: #3f554c; font-size: 10px; font-variant-numeric: tabular-nums; text-align: right; }
.band-value strong { color: var(--ink-strong); font-weight: 700; }
.band-value span { color: var(--ink-soft); }
.chart-note { margin-top: 17px; padding-top: 12px; border-top: 1px solid #edf1ee; color: var(--ink-muted); }
.chart-note summary { width: fit-content; color: #466e61; cursor: pointer; font-size: 10px; font-weight: 600; }
.chart-note p { max-width: 640px; margin: 9px 0 0; font-size: 10px; line-height: 1.6; }

.capacity-visual { display: flex; min-height: 150px; align-items: center; justify-content: center; gap: clamp(18px, 4vw, 47px); }
.capacity-ring { display: grid; width: 142px; height: 142px; flex: 0 0 auto; place-items: center; border-radius: 50%; background: conic-gradient(#438675 0deg, #438675 0deg, #e8efeb 0deg 360deg); }
.ring-center { display: grid; width: 110px; height: 110px; align-content: center; justify-items: center; border-radius: 50%; background: #fff; }
.ring-center strong { color: var(--ink-strong); font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; font-size: 24px; letter-spacing: -.04em; }
.ring-center span { color: var(--ink-muted); font-size: 9px; }
.capacity-legend { display: grid; gap: 13px; }
.legend-item { display: grid; grid-template-columns: 9px auto; align-items: start; gap: 8px; color: var(--ink-muted); font-size: 10px; }
.legend-dot { width: 8px; height: 8px; margin-top: 4px; border-radius: 50%; background: #438675; }
.legend-item:nth-child(2) .legend-dot { background: #9bb9aa; }
.legend-item:nth-child(3) .legend-dot { background: #d5ded8; }
.legend-copy { display: grid; gap: 1px; }
.legend-copy strong { color: #42574f; font-size: 11px; font-weight: 700; }
.legend-copy span { color: var(--ink-soft); font-size: 9px; }
.capacity-footnote { min-height: 28px; margin-top: 9px; padding-top: 10px; border-top: 1px solid #edf1ee; color: var(--ink-muted); font-size: 9px; line-height: 1.5; }

.interpretation-note { align-items: flex-start; margin-top: 15px; padding: 11px 13px; border-radius: 11px; }
.interpretation-note p { font-size: 10px; }
.interpretation-note strong { color: #38584d; }

.empty-state { display: grid; justify-items: center; padding: 34px 20px 30px; color: var(--ink-muted); text-align: center; }
.empty-illustration { position: relative; width: 126px; height: 91px; margin-bottom: 13px; }
.illustration-card { position: absolute; width: 80px; height: 56px; border: 1px solid #dce7e0; border-radius: 10px; background: #fff; box-shadow: var(--shadow); }
.card-one { top: 7px; left: 16px; transform: rotate(-8deg); }
.card-two { top: 5px; left: 35px; transform: rotate(7deg); }
.illustration-chart { position: absolute; right: 9px; bottom: 8px; display: flex; width: 57px; height: 41px; align-items: flex-end; gap: 5px; padding: 6px; border: 1px solid #dce7e0; border-radius: 9px; background: #f8fbf8; }
.illustration-chart i { flex: 1; border-radius: 3px 3px 1px 1px; background: #8bb7a4; }
.illustration-chart i:nth-child(1) { height: 36%; }
.illustration-chart i:nth-child(2) { height: 58%; background: #9bb1bb; }
.illustration-chart i:nth-child(3) { height: 45%; background: #cfb082; }
.illustration-chart i:nth-child(4) { height: 78%; background: #c18787; }
.empty-state h2 { margin: 0 0 5px; font-size: 15px; letter-spacing: -.02em; }
.empty-state p { max-width: 410px; margin: 0; color: var(--ink-muted); font-size: 11px; }
.page-footer { display: flex; justify-content: space-between; gap: 15px; margin-top: 12px; padding: 14px 0 3px; border-top: 1px solid var(--line); color: var(--ink-soft); font-size: 9px; }

@media (max-width: 1120px) {
  .main-content { padding-right: 28px; padding-left: 28px; }
  .sidebar { width: 220px; }
  .main-content { margin-left: 220px; }
  .analysis-panel { grid-template-columns: 1fr; gap: 16px; }
  .analysis-panel-copy p { max-width: 520px; }
}

@media (max-width: 820px) {
  .sidebar { position: static; width: auto; height: auto; padding: 13px 18px; border-right: 0; border-bottom: 1px solid var(--line); }
  .brand { padding: 0; }
  .nav-label, .sidebar-bottom { display: none; }
  .primary-nav { display: flex; overflow-x: auto; gap: 4px; margin-top: 13px; }
  .nav-link { min-height: 38px; flex: 0 0 auto; padding: 0 10px; font-size: 11px; }
  .nav-icon { width: 16px; font-size: 15px; }
  .nav-soon { display: none; }
  .main-content { margin-left: 0; padding: 0 20px 20px; }
  .topbar { height: 55px; }
  .insight-grid { grid-template-columns: 1fr; }
}

@media (max-width: 560px) {
  .main-content { padding-right: 14px; padding-left: 14px; }
  .page-heading { align-items: flex-start; flex-direction: column; gap: 10px; padding: 23px 0 17px; }
  .analysis-panel { padding: 17px 14px; }
  .file-drop { gap: 9px; }
  .browse-button { padding: 7px; font-size: 9px; }
  .file-drop-copy span { max-width: 180px; font-size: 9px; }
  .form-actions { align-items: stretch; flex-direction: column; }
  .capacity-field { align-items: flex-start; }
  .primary-button { width: 100%; }
  .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; }
  .metric-card { min-height: 104px; padding: 13px; }
  .metric-value { font-size: 22px; }
  .card { padding: 16px 14px; }
  .band-row { grid-template-columns: 68px minmax(45px, 1fr) 52px; gap: 8px; }
  .capacity-visual { gap: 17px; }
  .capacity-ring { width: 120px; height: 120px; }
  .ring-center { width: 94px; height: 94px; }
  .ring-center strong { font-size: 21px; }
  .section-heading { align-items: flex-start; flex-direction: column; }
  .page-footer { flex-direction: column; gap: 4px; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; }
}

```

### `src/propensity_prediction/dashboard/static/app.js`

```javascript
"use strict";

const INTEGER_FIELDS = new Set([
  "ID", "SEX", "EDUCATION", "MARRIAGE",
  "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
]);
const NON_NEGATIVE_FIELDS = new Set([
  "LIMIT_BAL", "PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6",
]);
const INTEGER_RANGES = {
  SEX: [1, 2],
  EDUCATION: [0, 4],
  MARRIAGE: [0, 3],
};

const elements = {
  form: document.querySelector("#analysis-form"),
  file: document.querySelector("#portfolio-file"),
  fileName: document.querySelector("#file-name"),
  fileHint: document.querySelector("#file-hint"),
  capacity: document.querySelector("#review-capacity"),
  runButton: document.querySelector("#run-analysis"),
  formMessage: document.querySelector("#form-message"),
  status: document.querySelector("#service-status"),
  healthCheck: document.querySelector("#health-check"),
  emptyState: document.querySelector("#empty-state"),
  results: document.querySelector("#results-section"),
  metrics: document.querySelector("#metric-grid"),
  riskBands: document.querySelector("#risk-band-chart"),
  riskReference: document.querySelector("#risk-band-reference"),
  capacityRing: document.querySelector("#capacity-ring"),
  capacityPercent: document.querySelector("#capacity-percent"),
  capacityLegend: document.querySelector("#capacity-legend"),
  capacityFootnote: document.querySelector("#capacity-footnote"),
  portfolioCount: document.querySelector("#portfolio-count"),
  analysisMeta: document.querySelector("#analysis-meta"),
  analysisMetaText: document.querySelector("#analysis-meta-text"),
};

let dashboardConfig = null;
let selectedFile = null;

const percentFormatter = new Intl.NumberFormat(undefined, {
  style: "percent",
  maximumFractionDigits: 1,
});
const numberFormatter = new Intl.NumberFormat(undefined, {
  maximumFractionDigits: 0,
});

function showMessage(message, kind = "error") {
  elements.formMessage.textContent = message;
  elements.formMessage.hidden = false;
  elements.formMessage.classList.toggle("is-success", kind === "success");
}

function clearMessage() {
  elements.formMessage.textContent = "";
  elements.formMessage.hidden = true;
  elements.formMessage.classList.remove("is-success");
}

function setServiceStatus(ready, message) {
  elements.status.classList.toggle("is-ready", ready);
  elements.status.classList.toggle("is-error", !ready);
  elements.status.lastChild.textContent = ` ${message}`;
}

function parseCsv(text) {
  const source = text.replace(/^\uFEFF/, "");
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;
  let afterQuote = false;

  for (let index = 0; index < source.length; index += 1) {
    const character = source[index];
    const next = source[index + 1];

    if (inQuotes) {
      if (character === '"' && next === '"') {
        field += '"';
        index += 1;
      } else if (character === '"') {
        inQuotes = false;
        afterQuote = true;
      } else {
        field += character;
      }
      continue;
    }

    if (afterQuote) {
      if (character === ",") {
        row.push(field);
        field = "";
        afterQuote = false;
      } else if (character === "\n" || character === "\r") {
        row.push(field);
        appendCsvRow(rows, row);
        row = [];
        field = "";
        afterQuote = false;
        if (character === "\r" && next === "\n") index += 1;
      } else if (character === " " || character === "\t") {
        // Ignore whitespace between a closing quote and its delimiter.
      } else {
        throw new Error("The CSV has invalid characters after a quoted value.");
      }
      continue;
    }

    if (character === '"') {
      if (field.length > 0) {
        throw new Error("The CSV contains a quote inside an unquoted value.");
      }
      inQuotes = true;
    } else if (character === ",") {
      row.push(field);
      field = "";
    } else if (character === "\n" || character === "\r") {
      row.push(field);
      appendCsvRow(rows, row);
      row = [];
      field = "";
      if (character === "\r" && next === "\n") index += 1;
    } else {
      field += character;
    }
  }

  if (inQuotes) throw new Error("The CSV contains an unclosed quoted value.");
  if (field.length > 0 || row.length > 0 || afterQuote) {
    row.push(field);
    appendCsvRow(rows, row);
  }
  return rows;
}

function appendCsvRow(rows, row) {
  if (row.length === 1 && row[0] === "") return;
  rows.push(row);
}

function parseNumeric(value, column, csvRowNumber) {
  const trimmed = value.trim();
  const decimalPattern = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/;
  if (!decimalPattern.test(trimmed)) {
    throw new Error(`${column} must contain numeric values. Check CSV row ${csvRowNumber}.`);
  }
  const number = Number(trimmed);
  if (!Number.isFinite(number)) {
    throw new Error(`${column} must contain finite numeric values. Check CSV row ${csvRowNumber}.`);
  }
  if (INTEGER_FIELDS.has(column) && !Number.isInteger(number)) {
    throw new Error(`${column} must contain integer values. Check CSV row ${csvRowNumber}.`);
  }
  if (column === "ID" && !Number.isSafeInteger(number)) {
    throw new Error(`ID must be a safely representable integer. Check CSV row ${csvRowNumber}.`);
  }
  if (NON_NEGATIVE_FIELDS.has(column) && number < 0) {
    throw new Error(`${column} must be non-negative. Check CSV row ${csvRowNumber}.`);
  }
  if (Object.hasOwn(INTEGER_RANGES, column)) {
    const [minimum, maximum] = INTEGER_RANGES[column];
    if (number < minimum || number > maximum) {
      throw new Error(`${column} must use values from ${minimum} through ${maximum}. Check CSV row ${csvRowNumber}.`);
    }
  }
  return number;
}

function validateCsvRows(rows) {
  if (!rows.length) throw new Error("The CSV is empty.");
  const [headers, ...dataRows] = rows;
  if (!headers.length || headers.every((header) => header === "")) {
    throw new Error("The CSV must include a header row.");
  }
  if (new Set(headers).size !== headers.length) {
    throw new Error("The CSV contains duplicate column names.");
  }
  if (headers.includes("DEFAULT")) {
    throw new Error("DEFAULT is a historical outcome, not an input for prediction. Upload a prediction-time file without this column.");
  }

  const required = dashboardConfig.required_columns;
  const missing = required.filter((column) => !headers.includes(column));
  const extra = headers.filter((column) => !required.includes(column));
  if (missing.length || extra.length) {
    const problems = [];
    if (missing.length) problems.push(`Missing required columns: ${missing.join(", ")}.`);
    if (extra.length) problems.push(`Unrecognized columns: ${extra.join(", ")}.`);
    throw new Error(problems.join(" "));
  }
  if (!dataRows.length) throw new Error("The CSV must contain at least one customer row.");
  if (dataRows.length > dashboardConfig.max_customer_rows) {
    throw new Error(`The CSV contains ${numberFormatter.format(dataRows.length)} customer rows; the maximum is ${numberFormatter.format(dashboardConfig.max_customer_rows)}. Split the portfolio into smaller files.`);
  }

  const seenIds = new Set();
  return dataRows.map((values, rowIndex) => {
    const csvRowNumber = rowIndex + 2;
    if (values.length !== headers.length) {
      throw new Error(`CSV row ${csvRowNumber} has ${values.length} values; expected ${headers.length}.`);
    }
    const sourceRow = Object.fromEntries(headers.map((header, index) => [header, values[index]]));
    const customer = {};
    for (const column of required) {
      const value = sourceRow[column];
      if (value === undefined || value.trim() === "") {
        throw new Error(`${column} cannot be blank. Check CSV row ${csvRowNumber}.`);
      }
      customer[column] = parseNumeric(value, column, csvRowNumber);
    }
    if (seenIds.has(customer.ID)) {
      throw new Error(`ID values must be unique. Duplicate ID ${customer.ID} appears in CSV row ${csvRowNumber}.`);
    }
    seenIds.add(customer.ID);
    return customer;
  });
}

function formatCount(value) {
  return numberFormatter.format(value);
}

function formatPercent(value) {
  return percentFormatter.format(value);
}

function renderMetricCards(result) {
  const capacity = result.capacity;
  const summary = result.portfolio_summary.probability_summary;
  const metrics = [
    { label: "Customers scored", value: formatCount(result.population_count), help: "Full uploaded portfolio", icon: "▦" },
    { label: "Mean predicted risk", value: formatPercent(summary.mean), help: "Average model estimate", icon: "⌁" },
    { label: "Selected for review", value: formatCount(capacity.selected_count), help: "Under the supplied capacity", icon: "✓" },
    { label: "Unused capacity", value: formatCount(capacity.unused_capacity), help: "After tie-aware selection", icon: "↗" },
  ];

  elements.metrics.replaceChildren(...metrics.map((metric) => {
    const card = document.createElement("article");
    card.className = "metric-card";
    card.innerHTML = `
      <div class="metric-card-top">
        <span class="metric-label">${metric.label}</span>
        <span class="metric-icon" aria-hidden="true">${metric.icon}</span>
      </div>
      <strong class="metric-value">${metric.value}</strong>
      <span class="metric-help">${metric.help}</span>
    `;
    return card;
  }));
}

function renderRiskBands(summary) {
  const bands = summary.risk_bands;
  elements.riskBands.replaceChildren(...bands.map((band) => {
    const row = document.createElement("div");
    row.className = "band-row";
    row.dataset.band = band.label;
    row.setAttribute("role", "listitem");

    const label = document.createElement("span");
    label.className = "band-label";
    label.textContent = band.label;

    const track = document.createElement("span");
    track.className = "band-track";
    track.setAttribute("aria-hidden", "true");
    const fill = document.createElement("span");
    fill.className = "band-fill";
    fill.style.width = `${Math.max(0, Math.min(1, band.portfolio_share)) * 100}%`;
    track.append(fill);

    const value = document.createElement("span");
    value.className = "band-value";
    value.innerHTML = `<strong>${formatCount(band.customer_count)}</strong> <span>· ${formatPercent(band.portfolio_share)}</span>`;
    row.append(label, track, value);
    return row;
  }));
  elements.riskReference.textContent = `${summary.risk_band_reference}. The fixed validation-cohort method is descriptive; these bands are not action thresholds.`;
}

function renderCapacity(result) {
  const capacity = result.capacity;
  const denominator = capacity.target_review_count;
  const utilization = denominator > 0 ? capacity.selected_count / denominator : 0;
  const safeUtilization = Math.max(0, Math.min(1, utilization));
  const percentage = denominator > 0 ? Math.round(safeUtilization * 100) : null;
  const degrees = safeUtilization * 360;

  elements.capacityRing.style.background = `conic-gradient(#438675 0deg ${degrees}deg, #e8efeb ${degrees}deg 360deg)`;
  elements.capacityPercent.textContent = percentage === null ? "—" : `${percentage}%`;

  const items = [
    { label: "Requested", count: capacity.requested_review_count, note: "Analyst capacity" },
    { label: "Selected", count: capacity.selected_count, note: "Entered the queue" },
    { label: "Unused", count: capacity.unused_capacity, note: "Tie-aware remainder" },
  ];
  elements.capacityLegend.replaceChildren(...items.map((item) => {
    const entry = document.createElement("div");
    entry.className = "legend-item";
    const dot = document.createElement("span");
    dot.className = "legend-dot";
    dot.setAttribute("aria-hidden", "true");
    const copy = document.createElement("span");
    copy.className = "legend-copy";
    const strong = document.createElement("strong");
    strong.textContent = `${item.label}: ${formatCount(item.count)}`;
    const note = document.createElement("span");
    note.textContent = item.note;
    copy.append(strong, note);
    entry.append(dot, copy);
    return entry;
  }));

  if (denominator === 0) {
    elements.capacityFootnote.textContent = "No review capacity was requested; no customers were selected.";
  } else if (capacity.unused_capacity > 0) {
    elements.capacityFootnote.textContent = "Some capacity remained unused because the queue keeps equal-score customers together at the selection boundary.";
  } else {
    elements.capacityFootnote.textContent = "The requested target was filled. Equal-score groups are kept together at the selection boundary.";
  }
}

function renderOverview(result) {
  renderMetricCards(result);
  renderRiskBands(result.portfolio_summary);
  renderCapacity(result);
  elements.portfolioCount.textContent = `${formatCount(result.population_count)} customers`;
  elements.analysisMetaText.textContent = `Scored ${new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}`;
  elements.analysisMeta.hidden = false;
  elements.results.hidden = false;
  elements.emptyState.hidden = true;
  elements.results.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function readSelectedFile() {
  if (!selectedFile) throw new Error("Choose a CSV file before running the analysis.");
  const text = await selectedFile.text();
  return validateCsvRows(parseCsv(text));
}

async function loadDashboardConfig() {
  const response = await fetch("/v1/dashboard-config");
  if (!response.ok) throw new Error("The dashboard configuration could not be loaded.");
  dashboardConfig = await response.json();
  elements.fileHint.textContent = `ID and all 23 predictors · up to ${formatCount(dashboardConfig.max_customer_rows)} customers`;
  elements.capacity.max = String(dashboardConfig.max_customer_rows);
}

async function checkService() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("The scoring service is unavailable.");
    const health = await response.json();
    if (!health.model_loaded) throw new Error("The API is running, but the model is not loaded.");
    setServiceStatus(true, "Scoring service ready");
  } catch (error) {
    setServiceStatus(false, error.message || "Scoring service unavailable");
  }
}

elements.file.addEventListener("change", () => {
  selectedFile = elements.file.files?.[0] ?? null;
  clearMessage();
  if (selectedFile) {
    elements.fileName.textContent = selectedFile.name;
    elements.fileHint.textContent = `${(selectedFile.size / 1024).toFixed(0)} KB · ready to validate`;
    elements.fileName.title = selectedFile.name;
  } else {
    elements.fileName.textContent = "Choose a CSV file";
  }
});

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearMessage();
  elements.runButton.disabled = true;
  elements.runButton.querySelector("span:first-child").textContent = "Scoring portfolio…";

  try {
    if (!dashboardConfig) await loadDashboardConfig();
    const customers = await readSelectedFile();
    if (elements.capacity.value.trim() === "") {
      throw new Error("Enter a review capacity.");
    }
    const capacity = Number(elements.capacity.value);
    if (!Number.isSafeInteger(capacity) || capacity < 0) {
      throw new Error("Review capacity must be a non-negative whole number.");
    }

    const response = await fetch("/v1/review-queue", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ customers, max_review_count: capacity }),
    });
    const payload = await response.json();
    if (!response.ok) {
      const details = payload?.error?.details?.filter(Boolean).join(" ");
      throw new Error(details || payload?.error?.message || "The scoring request failed.");
    }

    renderOverview(payload);
    setServiceStatus(true, "Scoring service ready");
    showMessage(`Analysis complete for ${formatCount(payload.population_count)} customers.`, "success");
  } catch (error) {
    showMessage(error.message || "The portfolio could not be scored.");
  } finally {
    elements.runButton.disabled = false;
    elements.runButton.querySelector("span:first-child").textContent = "Run analysis";
  }
});

elements.healthCheck.addEventListener("click", checkService);

loadDashboardConfig()
  .then(checkService)
  .catch((error) => setServiceStatus(false, error.message));

```

### `src/propensity_prediction/api/routes.py`

```python
"""HTTP routes for readiness and review-queue requests."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from propensity_prediction.api.schemas import (
    APIErrorResponse,
    CustomerInput,
    DashboardConfigResponse,
    HealthResponse,
    ReviewQueueRequest,
    ReviewQueueResponse,
)
from propensity_prediction.api.service import ReviewQueueService
from propensity_prediction.limits import MAX_CUSTOMER_ROWS


router = APIRouter()


def get_review_queue_service(request: Request) -> ReviewQueueService:
    return request.app.state.review_queue_service


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    repository = request.app.state.model_repository
    return HealthResponse(
        status="ok" if repository.is_loaded else "degraded",
        model_loaded=repository.is_loaded,
    )


@router.get("/v1/dashboard-config", response_model=DashboardConfigResponse)
def dashboard_config() -> DashboardConfigResponse:
    """Expose upload rules so the browser uses the API's schema and row cap."""
    return DashboardConfigResponse(
        max_customer_rows=MAX_CUSTOMER_ROWS,
        required_columns=list(CustomerInput.model_fields),
    )


@router.post(
    "/v1/review-queue",
    response_model=ReviewQueueResponse,
    responses={
        400: {"model": APIErrorResponse},
        422: {"model": APIErrorResponse},
        503: {"model": APIErrorResponse},
    },
)
def create_review_queue(
    payload: ReviewQueueRequest,
    service: ReviewQueueService = Depends(get_review_queue_service),
) -> dict:
    return service.build_queue(payload)

```

### `src/propensity_prediction/api/schemas.py`

```python
"""Pydantic request and response models for the public API contract."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt

from propensity_prediction.limits import MAX_CUSTOMER_ROWS


class CustomerInput(BaseModel):
    """One customer row: identifier plus the 23 canonical predictors."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        allow_inf_nan=False,
    )

    ID: StrictInt
    LIMIT_BAL: Annotated[float, Field(ge=0)]
    AGE: float
    BILL_AMT1: float
    BILL_AMT2: float
    BILL_AMT3: float
    BILL_AMT4: float
    BILL_AMT5: float
    BILL_AMT6: float
    PAY_AMT1: Annotated[float, Field(ge=0)]
    PAY_AMT2: Annotated[float, Field(ge=0)]
    PAY_AMT3: Annotated[float, Field(ge=0)]
    PAY_AMT4: Annotated[float, Field(ge=0)]
    PAY_AMT5: Annotated[float, Field(ge=0)]
    PAY_AMT6: Annotated[float, Field(ge=0)]
    SEX: Annotated[StrictInt, Field(ge=1, le=2)]
    EDUCATION: Annotated[StrictInt, Field(ge=0, le=4)]
    MARRIAGE: Annotated[StrictInt, Field(ge=0, le=3)]
    PAY_0: StrictInt
    PAY_2: StrictInt
    PAY_3: StrictInt
    PAY_4: StrictInt
    PAY_5: StrictInt
    PAY_6: StrictInt


class ReviewQueueRequest(BaseModel):
    """Batch request to score a portfolio and apply a review-count limit."""

    model_config = ConfigDict(extra="forbid", strict=True)

    customers: Annotated[
        list[CustomerInput], Field(min_length=1, max_length=MAX_CUSTOMER_ROWS)
    ]
    max_review_count: Annotated[StrictInt, Field(ge=0)]


class CapacitySummary(BaseModel):
    requested_review_count: int
    target_review_count: int
    selected_count: int
    unused_capacity: int


class CustomerQueueItem(BaseModel):
    customer_id: int
    predicted_default_probability: float = Field(ge=0, le=1)
    risk_rank: int = Field(ge=1)
    selected_for_review: bool
    reason_code: str
    reason: str


class ProbabilitySummary(BaseModel):
    minimum: float = Field(ge=0, le=1)
    percentile_25: float = Field(ge=0, le=1)
    median: float = Field(ge=0, le=1)
    mean: float = Field(ge=0, le=1)
    percentile_75: float = Field(ge=0, le=1)
    maximum: float = Field(ge=0, le=1)


class RiskBandSummary(BaseModel):
    label: str
    customer_count: int = Field(ge=0)
    portfolio_share: float = Field(ge=0, le=1)
    lower_bound_exclusive: float | None = Field(default=None, ge=0, le=1)
    upper_bound_inclusive: float | None = Field(default=None, ge=0, le=1)


class PortfolioSummary(BaseModel):
    probability_summary: ProbabilitySummary
    risk_band_method: Literal["fixed_validation_cohort_quantiles"]
    risk_band_reference: str
    risk_bands: list[RiskBandSummary]


class ReviewQueueResponse(BaseModel):
    population_count: int
    capacity: CapacitySummary
    portfolio_summary: PortfolioSummary
    customers: list[CustomerQueueItem]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


class DashboardConfigResponse(BaseModel):
    max_customer_rows: int = Field(ge=1)
    required_columns: list[str]


class APIErrorBody(BaseModel):
    code: str
    message: str
    details: list[str]


class APIErrorResponse(BaseModel):
    error: APIErrorBody

```

### `src/propensity_prediction/api/main.py`

```python
"""FastAPI application factory and stable error response handlers."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from propensity_prediction.api.errors import (
    InvalidPortfolioError,
    ModelArtifactUnavailable,
)
from propensity_prediction.api.repository import ModelArtifactRepository
from propensity_prediction.api.routes import router
from propensity_prediction.api.service import ReviewQueueService
from propensity_prediction.dashboard import STATIC_ASSETS_DIRECTORY
from propensity_prediction.models.artifact import DEFAULT_MODEL_ARTIFACT_PATH


logger = logging.getLogger(__name__)


def _error_response(code: str, message: str, details: list[str]) -> dict:
    return {"error": {"code": code, "message": message, "details": details}}


def create_app(
    artifact_path: str | Path = DEFAULT_MODEL_ARTIFACT_PATH,
) -> FastAPI:
    repository = ModelArtifactRepository(artifact_path)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        repository.load()
        app.state.model_repository = repository
        app.state.review_queue_service = ReviewQueueService(repository)
        yield

    app = FastAPI(
        title="Credit Risk Review Prioritization API",
        version="1.0.0",
        description=(
            "Scores supplied customer predictors and constructs a deterministic "
            "capacity-limited analyst review queue. It does not recommend or "
            "execute customer interventions."
        ),
        lifespan=lifespan,
    )
    app.include_router(router)
    app.mount(
        "/",
        StaticFiles(directory=STATIC_ASSETS_DIRECTORY, html=True),
        name="dashboard",
    )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        details = [
            ".".join(str(part) for part in error["loc"] if part != "body")
            + f": {error['msg']}"
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=_error_response(
                "INVALID_REQUEST_SCHEMA",
                "The request does not match the review-queue contract.",
                details,
            ),
        )

    @app.exception_handler(InvalidPortfolioError)
    async def invalid_portfolio_handler(
        request: Request,
        exc: InvalidPortfolioError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content=_error_response(
                "INVALID_PORTFOLIO",
                str(exc),
                [],
            ),
        )

    @app.exception_handler(ModelArtifactUnavailable)
    async def model_unavailable_handler(
        request: Request,
        exc: ModelArtifactUnavailable,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content=_error_response(
                "MODEL_UNAVAILABLE",
                str(exc),
                [],
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        code = "MODEL_UNAVAILABLE" if exc.status_code == 503 else "HTTP_ERROR"
        message = str(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_response(code, message, []),
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.error(
            "Unhandled API error",
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        return JSONResponse(
            status_code=500,
            content=_error_response(
                "INTERNAL_SERVER_ERROR",
                "The API could not complete this request.",
                [],
            ),
        )

    return app


app = create_app()

```

### `src/propensity_prediction/dashboard/__init__.py`

```python
"""Analyst dashboard helpers and packaged static web assets."""

from pathlib import Path


STATIC_ASSETS_DIRECTORY = Path(__file__).resolve().parent / "static"

```

### `tests/test_dashboard_web_app.py`

```python
from __future__ import annotations

from propensity_prediction.api.routes import dashboard_config
from propensity_prediction.data.schema import get_feature_columns
from propensity_prediction.dashboard import STATIC_ASSETS_DIRECTORY


def test_dashboard_config_uses_api_schema_and_row_limit() -> None:
    config = dashboard_config()

    assert config.max_customer_rows == 30_000
    assert config.required_columns[0] == "ID"
    assert len(config.required_columns) == 24
    assert config.required_columns[1:] == get_feature_columns()


def test_custom_dashboard_static_assets_are_packaged() -> None:
    page = (STATIC_ASSETS_DIRECTORY / "index.html").read_text()
    styles = (STATIC_ASSETS_DIRECTORY / "styles.css").read_text()
    script = (STATIC_ASSETS_DIRECTORY / "app.js").read_text()

    assert "Portfolio overview" in page
    assert "--canvas" in styles
    assert "validateCsvRows" in script

```

## Verification

- Focused tests: `venv/bin/python -m pytest tests/test_dashboard_web_app.py tests/test_api_review_queue.py tests/test_risk_segmentation.py`.
- Browser workflow: uploaded the provided 10-customer synthetic CSV, set capacity to 4, and confirmed successful scoring, overview metrics, risk-band counts, and capacity display.
- `git diff --check` checks whitespace and patch formatting.

## Files and responsibilities

| File | Responsibility |
| --- | --- |
| `dashboard/static/index.html` | Semantic overview layout and upload flow |
| `dashboard/static/styles.css` | Light visual system, responsive behavior, and accessibility states |
| `dashboard/static/app.js` | CSV parsing/validation, API calls, and response rendering |
| `api/routes.py` | Dashboard configuration endpoint |
| `api/schemas.py` | Typed configuration response |
| `api/main.py` | Serves packaged frontend assets |
| `dashboard/__init__.py` | Locates static assets |
| `pyproject.toml` | Packages static assets in distributions |
| `tests/test_dashboard_web_app.py` | Checks config contract and packaged frontend assets |

### `pyproject.toml` package-data change

The existing packaging configuration now includes the static frontend files when the Python package is built:

```toml
[tool.setuptools.package-data]
propensity_prediction = ["dashboard/static/*.html", "dashboard/static/*.css", "dashboard/static/*.js"]
```

---

<a id="step-9-6"></a>
## Step 9.6

# Phase 9.6 — Risk Distribution and Cohort Exploration

## Decision

The user chose **Option A: client-side exploration**. After FastAPI scores a portfolio once, the browser retains the submitted predictor rows and joins them to the returned scored rows by customer ID. Filters and comparisons operate on this in-memory copy. The API remains authoritative for predictions, risk-band assignments, rank, and review selection; the browser does not reproduce model or queue logic.

## What the analyst can do

- Search customer IDs by substring.
- Set minimum and maximum predicted-risk values.
- Filter on one of the fixed Phase 6 reference risk bands.
- Show all customers, those selected for review, or those not selected.
- Filter on one model input field. Encoded category fields filter by exact supplied code; other numeric fields filter by inclusive minimum/maximum.
- Compare the filtered cohort by any one of the 23 input fields.
- Inspect a fixed ten-bin predicted-risk distribution and a paginated, risk-ranked customer table.
- Reset all filters to their starting values.

The screen always states `matching customers of full portfolio`. Group shares and score-bin percentages use the **filtered cohort** as their denominator. Numeric feature quartiles use the **full portfolio** to keep their group boundaries stable while other filters change. Category values are shown as codes from the input; the UI does not infer meanings for codes.

## Step-by-step code walkthrough

### 1. Navigation and view structure (`index.html`)

The sidebar's Overview and Explore portfolio links are now actionable. The API upload form remains shared, while overview results and the exploration section are distinct views. The exploration view contains:

1. An explicit filtered/full-population count.
2. A filter card for ID, predicted-risk range, fixed risk band, review status, and input-field values.
3. A 10-bin score distribution.
4. A group-comparison table with count, share, mean predicted risk, and review-selected count.
5. A risk-rank ordered customer table with 50 rows per page.

The view includes descriptive-use language beside the results: group differences do not show causal effects or establish fairness conclusions.

### 2. Browser state and joins (`app.js`)

`currentPortfolio` is assembled by matching each API result's `customer_id` to the original input row's `ID`, then combining those properties with the API score, rank, selection, and queue reason fields. This lets the browser filter input characteristics without expanding the response schema or storing data server-side. The state exists only in the current page session and is replaced by a new scoring run.

### 3. Filter controls

`initializeExploreFields` derives available feature names from the dashboard configuration returned by the API. `renderFeatureValueControl` distinguishes encoded categorical inputs from continuous numeric predictors. Categorical choices use exact observed values. Continuous controls use inclusive ranges initialized to that field's current full-population minimum and maximum.

`applyExploreFilters` applies every active condition to each in-memory record. Risk bands are matched against the cut points returned in `portfolio_summary`; review membership comes directly from `selected_for_review`; score ordering/ranking comes directly from `risk_rank`. When minimum risk exceeds maximum risk, it gives a clear message instead of presenting a stale value as a valid cohort. The reset action restores all default controls and the full set.

### 4. Distribution and group comparisons

`renderScoreDistribution` bins each filtered score into one of ten fixed intervals: 0–10%, 10–20%, …, 90–100%. Counts and shares are derived from the filtered cohort. Bar widths represent those shares, with text values beside them.

`renderGroupSummary` groups filtered rows by the chosen input. Encoded categorical values remain separate groups. Numeric fields use quartile cut points calculated from the full portfolio, and these boundaries are cached per field so a filter change does not repeatedly sort the full population. Each group reports its count, its share of filtered rows, mean predicted probability, and selected count. These are descriptive summaries; the selected-count column is not a treatment-effect estimate.

### 5. Customer table and navigation

`renderCustomerTable` shows at most 50 matching rows per page, ordered as returned by the API's risk rank. It never creates 30,000 table rows in the DOM at once. Previous/Next controls and visible range labels communicate pagination. Empty cohorts show explicit no-match messages in both tables. `setActiveView` switches navigation state and reveals the requested view only after a portfolio has been scored.

### 6. Visual and responsive design (`styles.css`)

The exploration view reuses the light-theme palette and card hierarchy from Step 9.5. Inputs, tables, distribution tracks, empty states, and pagination use the same spacing and focus treatment. The filter layout collapses from four columns to two, and the comparison cards stack on narrower screens; tables remain horizontally scrollable when necessary.

## Performance profile at the 30,000-row cap

A local browser run used the real scoring API and a generated 30,000-row CSV made by repeating the provided 10-row synthetic sample with unique IDs. On this machine, changing the fixed risk-band filtering completed in **81 ms**; switching to a numeric `LIMIT_BAL` group completed in **56 ms**; selecting a numeric `AGE` field filter completed in **66 ms**; searching for one customer ID completed in **59 ms**. The page displayed 15,000 of 30,000 customers after choosing the Highest band, and ID search narrowed the view to one row; Reset restored all 30,000. These measurements include the browser control interaction and synchronous rendering on the current development machine, not a universal performance guarantee. Because the feature values were repeated from a small sample, the timing does not represent every real portfolio's data variety.

Filtering and binning scan the in-memory portfolio. Numeric quartile boundaries are sorted and cached once per field for the scoring run; the customer table renders at most 50 rows per page. Step 9.14 still includes a broader cap-level profile and end-to-end validation. If measured latency is unacceptable in the deployment environment, the user can consider server-side pagination in a later approved step.

## API and privacy boundary

No API endpoint or response field was added for this step. The existing scoring response already returns every customer score and decision field. Input records remain in browser memory for filtering and are not persisted. The browser cannot change the API's selected queue membership by filtering a view.

## Complete code listings

The following are the full current contents of the frontend files changed for Step 9.6. The HTML, CSS, and JavaScript also contain the previously completed overview UI so the integrated dashboard can be read as a whole.


### `src/propensity_prediction/dashboard/static/index.html`

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#f4f7f4" />
    <meta
      name="description"
      content="Understand a scored customer portfolio and its review capacity."
    />
    <title>Portfolio overview | Credit risk review</title>
    <link rel="stylesheet" href="/styles.css" />
    <script src="/app.js" defer></script>
  </head>
  <body>
    <div class="app-shell">
      <aside class="sidebar" aria-label="Dashboard navigation">
        <a class="brand" href="/" aria-label="Portfolio review home">
          <span class="brand-mark" aria-hidden="true">P</span>
          <span class="brand-copy">
            <strong>Portfolio</strong>
            <span>Risk review</span>
          </span>
        </a>

        <p class="nav-label">WORKSPACE</p>
        <nav class="primary-nav" aria-label="Primary">
          <a class="nav-link is-active" href="#overview" data-view="overview" aria-current="page">
            <span class="nav-icon" aria-hidden="true">▦</span>
            <span>Overview</span>
          </a>
          <a class="nav-link" href="#explore" data-view="explore">
            <span class="nav-icon" aria-hidden="true">⌕</span>
            <span>Explore portfolio</span>
          </a>
          <span class="nav-link is-disabled" aria-disabled="true">
            <span class="nav-icon" aria-hidden="true">≡</span>
            <span>Review queue</span>
            <span class="nav-soon">NEXT</span>
          </span>
        </nav>

        <div class="sidebar-bottom">
          <div class="sidebar-note">
            <span class="note-icon" aria-hidden="true">i</span>
            <p>Predicted risk helps prioritize review. It is not an outcome or an action recommendation.</p>
          </div>
          <span class="service-status" id="service-status" role="status">
            <span class="status-dot" aria-hidden="true"></span>
            Checking scoring service
          </span>
        </div>
      </aside>

      <main class="main-content" id="overview">
        <header class="topbar">
          <div class="breadcrumb">Workspace <span aria-hidden="true">/</span> Overview</div>
          <div class="topbar-actions">
            <button class="text-button" id="health-check" type="button">Check service</button>
            <span class="avatar" aria-hidden="true">AR</span>
          </div>
        </header>

        <section class="page-heading" aria-labelledby="page-title">
          <div>
            <p class="eyebrow">PORTFOLIO INSIGHTS</p>
            <h1 id="page-title">Portfolio overview</h1>
            <p class="page-description">A clear view of predicted risk and review capacity for your customer portfolio.</p>
          </div>
          <div class="analysis-meta" id="analysis-meta" hidden>
            <span class="meta-dot" aria-hidden="true"></span>
            <span id="analysis-meta-text">Analysis complete</span>
          </div>
        </section>

        <section class="analysis-panel" aria-labelledby="analysis-title">
          <div class="analysis-panel-copy">
            <span class="step-badge">NEW ANALYSIS</span>
            <h2 id="analysis-title">Start with a customer portfolio</h2>
            <p>Upload a prediction-time CSV, set your review capacity, and score the full portfolio.</p>
          </div>
          <form id="analysis-form" class="analysis-form">
            <label class="file-drop" for="portfolio-file">
              <span class="upload-icon" aria-hidden="true">↑</span>
              <span class="file-drop-copy">
                <strong id="file-name">Choose a CSV file</strong>
                <span id="file-hint">ID and all 23 predictors · up to 30,000 customers</span>
              </span>
              <span class="browse-button">Browse files</span>
            </label>
            <input id="portfolio-file" class="visually-hidden" type="file" accept=".csv,text/csv" />
            <div class="form-actions">
              <label class="capacity-field" for="review-capacity">
                <span>Review capacity</span>
                <span class="capacity-input-wrap">
                  <input id="review-capacity" type="number" min="0" step="1" value="10" inputmode="numeric" />
                  <span>customers</span>
                </span>
              </label>
              <button class="primary-button" id="run-analysis" type="submit">
                <span>Run analysis</span><span aria-hidden="true">→</span>
              </button>
            </div>
            <p class="form-message" id="form-message" role="alert" hidden></p>
          </form>
        </section>

        <section class="results-section" id="results-section" aria-labelledby="results-title" hidden>
          <div class="section-heading">
            <div>
              <p class="eyebrow">AT A GLANCE</p>
              <h2 id="results-title">Portfolio snapshot</h2>
              <p class="section-description">Summary of model estimates for the full uploaded portfolio.</p>
            </div>
            <span class="portfolio-count" id="portfolio-count"></span>
          </div>

          <div class="metric-grid" id="metric-grid" aria-label="Portfolio summary metrics"></div>

          <div class="insight-grid">
            <article class="card band-card" aria-labelledby="bands-title">
              <div class="card-heading">
                <div>
                  <h3 id="bands-title">Predicted risk bands</h3>
                  <p>How customers are distributed across the fixed reference bands.</p>
                </div>
                <span class="chart-mark" aria-hidden="true">▥</span>
              </div>
              <div class="band-list" id="risk-band-chart" role="list"></div>
              <details class="chart-note">
                <summary>How to read these bands</summary>
                <p id="risk-band-reference"></p>
                <p>These bands describe relative predicted risk. They are not action thresholds and do not change queue selection.</p>
              </details>
            </article>

            <article class="card capacity-card" aria-labelledby="capacity-title">
              <div class="card-heading">
                <div>
                  <h3 id="capacity-title">Review capacity</h3>
                  <p>How the requested capacity translated into the queue.</p>
                </div>
                <span class="chart-mark capacity-mark" aria-hidden="true">◎</span>
              </div>
              <div class="capacity-visual">
                <div class="capacity-ring" id="capacity-ring" aria-label="Capacity utilization">
                  <div class="ring-center">
                    <strong id="capacity-percent">0%</strong>
                    <span>of target selected</span>
                  </div>
                </div>
                <div class="capacity-legend" id="capacity-legend"></div>
              </div>
              <div class="capacity-footnote" id="capacity-footnote"></div>
            </article>
          </div>

          <div class="interpretation-note">
            <span class="note-icon" aria-hidden="true">i</span>
            <p><strong>Interpretation:</strong> Predicted probabilities summarize model estimates, not observed outcomes or expected losses. Portfolio patterns are descriptive and do not show that an intervention will change outcomes.</p>
          </div>
        </section>

        <section class="explore-view" id="explore-view" aria-labelledby="explore-title" hidden>
          <div class="section-heading explore-heading">
            <div>
              <p class="eyebrow">COHORT EXPLORATION</p>
              <h2 id="explore-title">Explore portfolio</h2>
              <p class="section-description">Filter scored customers and compare descriptive groups.</p>
            </div>
            <span class="portfolio-count" id="explore-count">0 of 0 customers</span>
          </div>

          <section class="card filters-card" aria-labelledby="filters-title">
            <div class="card-heading filter-heading">
              <div>
                <h3 id="filters-title">Find a cohort</h3>
                <p>Every filter applies to the full scored portfolio. Counts below show the filtered denominator.</p>
              </div>
              <button class="text-button" id="reset-filters" type="button">Reset filters</button>
            </div>
            <div class="filter-grid">
              <label class="filter-control">
                <span>Customer ID</span>
                <input id="filter-customer-id" type="search" inputmode="numeric" placeholder="Search ID" />
              </label>
              <label class="filter-control">
                <span>Minimum predicted risk</span>
                <input id="filter-score-min" type="number" min="0" max="1" step="0.01" value="0" />
              </label>
              <label class="filter-control">
                <span>Maximum predicted risk</span>
                <input id="filter-score-max" type="number" min="0" max="1" step="0.01" value="1" />
              </label>
              <label class="filter-control">
                <span>Reference risk band</span>
                <select id="filter-risk-band">
                  <option value="">All bands</option>
                  <option>Lower</option><option>Moderate</option><option>Elevated</option><option>Highest</option>
                </select>
              </label>
              <label class="filter-control">
                <span>Review status</span>
                <select id="filter-review-status">
                  <option value="">All customers</option>
                  <option value="selected">Selected for review</option>
                  <option value="not-selected">Not selected</option>
                </select>
              </label>
              <label class="filter-control">
                <span>Filter by input field</span>
                <select id="filter-feature">
                  <option value="">No input filter</option>
                </select>
              </label>
              <div class="filter-control feature-value-control" id="feature-value-control" hidden></div>
            </div>
            <p class="filter-message" id="filter-message" role="status"></p>
          </section>

          <div class="explore-summary-grid">
            <article class="card distribution-card">
              <div class="card-heading">
                <div><h3>Predicted-risk distribution</h3><p>Fixed 10 percentage-point bins; shares use the filtered cohort.</p></div>
              </div>
              <div class="score-distribution" id="score-distribution" role="list" aria-label="Predicted-risk distribution"></div>
            </article>
            <article class="card group-card">
              <div class="card-heading group-heading">
                <div><h3>Compare groups</h3><p>Descriptive summaries for the filtered cohort.</p></div>
                <label class="group-field"><span>Group by</span><select id="group-by-field"></select></label>
              </div>
              <div class="table-scroll">
                <table class="group-table">
                  <thead><tr><th scope="col">Group</th><th scope="col">Customers</th><th scope="col">Share</th><th scope="col">Mean risk</th><th scope="col">Selected</th></tr></thead>
                  <tbody id="group-summary-body"></tbody>
                </table>
              </div>
              <p class="table-note" id="group-table-note">For numeric fields, groups use quartile boundaries from the full portfolio.</p>
            </article>
          </div>

          <section class="card customer-results-card" aria-labelledby="customer-results-title">
            <div class="card-heading">
              <div><h3 id="customer-results-title">Matching customers</h3><p>Rows are ordered by the API's risk rank. The table shows a page at a time.</p></div>
              <span class="portfolio-count" id="page-count">0–0 of 0</span>
            </div>
            <div class="table-scroll">
              <table class="customer-table">
                <thead><tr><th scope="col">Rank</th><th scope="col">Customer ID</th><th scope="col">Predicted risk</th><th scope="col">Risk band</th><th scope="col">Review status</th></tr></thead>
                <tbody id="customer-results-body"></tbody>
              </table>
            </div>
            <div class="pagination-controls">
              <span id="page-status">Page 1 of 1</span>
              <div><button class="secondary-button" id="previous-page" type="button" disabled>Previous</button><button class="secondary-button" id="next-page" type="button" disabled>Next</button></div>
            </div>
          </section>

          <div class="interpretation-note">
            <span class="note-icon" aria-hidden="true">i</span>
            <p><strong>Interpretation:</strong> Filtered groups describe this uploaded portfolio. They do not establish causes, treatment effects, or fairness conclusions. Encoded input values are shown as supplied; category codes are not given inferred labels.</p>
          </div>
        </section>

        <section class="empty-state" id="empty-state" aria-labelledby="empty-title">
          <div class="empty-illustration" aria-hidden="true">
            <span class="illustration-card card-one"></span>
            <span class="illustration-card card-two"></span>
            <span class="illustration-chart"><i></i><i></i><i></i><i></i></span>
          </div>
          <h2 id="empty-title">Your portfolio overview will appear here</h2>
          <p>Upload a customer file above to see the portfolio summary and review-capacity breakdown.</p>
        </section>

        <footer class="page-footer">
          <span>Credit risk review · Analyst workspace</span>
          <span>Model estimates support review prioritization only</span>
        </footer>
      </main>
    </div>
  </body>
</html>

```

### `src/propensity_prediction/dashboard/static/styles.css`

```css
:root {
  color-scheme: light;
  --canvas: #f4f7f4;
  --surface: #ffffff;
  --surface-muted: #f8faf8;
  --ink: #263a36;
  --ink-strong: #1a302b;
  --ink-muted: #62746f;
  --ink-soft: #7c8b86;
  --line: #e1e9e4;
  --line-strong: #d1ded7;
  --teal: #287c70;
  --teal-dark: #1f685e;
  --teal-soft: #e6f1ed;
  --blue: #6487a2;
  --blue-soft: #eaf0f5;
  --amber: #aa7740;
  --amber-soft: #f5eee3;
  --rose: #a45f62;
  --rose-soft: #f5e9e8;
  --shadow: 0 10px 30px rgb(36 63 53 / 5%);
  --radius: 18px;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
}

* { box-sizing: border-box; }

body {
  min-width: 320px;
  min-height: 100vh;
  margin: 0;
  background: var(--canvas);
  color: var(--ink);
  font-size: 14px;
  line-height: 1.55;
}

button, input { font: inherit; }
button { color: inherit; }
a { color: inherit; }
[hidden] { display: none !important; }

:focus-visible {
  outline: 3px solid #75a99d;
  outline-offset: 3px;
}

.app-shell { min-height: 100vh; }

.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 5;
  display: flex;
  width: 248px;
  flex-direction: column;
  padding: 26px 18px 20px;
  border-right: 1px solid var(--line);
  background: #fbfcfa;
}

.brand {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 2px 8px 28px;
  text-decoration: none;
}

.brand-mark {
  display: grid;
  width: 39px;
  height: 39px;
  place-items: center;
  border-radius: 13px;
  background: var(--teal-dark);
  color: #fff;
  font-family: "Manrope", sans-serif;
  font-size: 19px;
  font-weight: 800;
}

.brand-copy { display: grid; line-height: 1.25; }
.brand-copy strong { color: var(--ink-strong); font-size: 15px; font-weight: 700; }
.brand-copy span { margin-top: 3px; color: var(--ink-muted); font-size: 11px; }

.nav-label, .eyebrow {
  color: var(--ink-soft);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .12em;
}

.nav-label { margin: 0 10px 10px; }
.primary-nav { display: grid; gap: 5px; }

.nav-link {
  display: flex;
  min-height: 44px;
  align-items: center;
  gap: 11px;
  padding: 0 11px;
  border-radius: 10px;
  color: #566963;
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
}

.nav-link.is-active {
  background: var(--teal-soft);
  color: #245f55;
  font-weight: 700;
}

.nav-icon {
  display: inline-grid;
  width: 22px;
  place-items: center;
  color: currentColor;
  font-size: 18px;
  line-height: 1;
}

.nav-link.is-disabled { color: #77857f; cursor: not-allowed; }
.nav-link:not(.is-disabled):hover { background: #f0f5f1; color: var(--teal-dark); }
.nav-soon {
  margin-left: auto;
  color: #77857f;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: .08em;
}

.sidebar-bottom { display: grid; gap: 17px; margin-top: auto; }
.sidebar-note, .interpretation-note {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  border: 1px solid #dfe9e3;
  background: #f1f6f2;
  color: #475d55;
}

.sidebar-note { padding: 12px 11px; border-radius: 12px; }
.sidebar-note p, .interpretation-note p { margin: 0; font-size: 11px; line-height: 1.55; }
.note-icon {
  display: inline-grid;
  width: 18px;
  height: 18px;
  flex: 0 0 auto;
  place-items: center;
  border: 1px solid #9bb5a9;
  border-radius: 50%;
  color: #3f6d5d;
  font-size: 11px;
  font-weight: 700;
}

.service-status { display: flex; align-items: center; gap: 8px; padding: 0 7px; color: var(--ink-muted); font-size: 11px; }
.status-dot, .meta-dot { width: 8px; height: 8px; border-radius: 50%; background: #b3c0b9; }
.service-status.is-ready .status-dot { background: #38876d; box-shadow: 0 0 0 3px #e2f0e8; }
.service-status.is-error .status-dot { background: #a45f62; box-shadow: 0 0 0 3px #f5e9e8; }

.main-content { max-width: 1540px; min-height: 100vh; margin-left: 248px; padding: 0 44px 24px; }
.topbar { display: flex; height: 72px; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--line); }
.breadcrumb { color: var(--ink-muted); font-size: 12px; }
.breadcrumb span { margin: 0 7px; color: #9aa8a2; }
.topbar-actions { display: flex; align-items: center; gap: 16px; }
.text-button { padding: 6px 2px; border: 0; background: transparent; color: #4c665e; cursor: pointer; font-size: 12px; font-weight: 600; }
.text-button:hover { color: var(--teal-dark); }
.avatar { display: grid; width: 31px; height: 31px; place-items: center; border: 1px solid #dce5df; border-radius: 50%; background: #e9f0eb; color: #426257; font-size: 10px; font-weight: 700; }

.page-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; padding: 31px 0 22px; }
.page-heading .eyebrow, .section-heading .eyebrow { margin: 0 0 6px; }
h1, h2, h3, p { margin-top: 0; }
h1, h2, h3 { color: var(--ink-strong); font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
h1 { margin-bottom: 6px; font-size: clamp(24px, 2.4vw, 32px); font-weight: 700; letter-spacing: -.04em; line-height: 1.2; }
.page-description { margin: 0; color: var(--ink-muted); font-size: 13px; }
.analysis-meta { display: inline-flex; align-items: center; gap: 8px; padding: 7px 11px; border: 1px solid var(--line); border-radius: 99px; background: var(--surface); color: #50665e; font-size: 11px; white-space: nowrap; }
.analysis-meta .meta-dot { background: #3c8a6f; }

.analysis-panel {
  display: grid;
  grid-template-columns: minmax(220px, .78fr) minmax(380px, 1.45fr);
  gap: 28px;
  padding: 22px 24px;
  border: 1px solid #dce7e0;
  border-radius: var(--radius);
  background: linear-gradient(116deg, #edf4ef, #f9fbf8 65%);
  box-shadow: var(--shadow);
}

.analysis-panel-copy { align-self: center; }
.step-badge { display: inline-block; margin-bottom: 9px; color: #4e7d6e; font-size: 9px; font-weight: 700; letter-spacing: .13em; }
.analysis-panel h2 { margin: 0 0 6px; font-size: 17px; letter-spacing: -.025em; }
.analysis-panel-copy p { max-width: 330px; margin: 0; color: var(--ink-muted); font-size: 12px; line-height: 1.6; }
.analysis-form { display: grid; align-content: center; gap: 12px; }
.file-drop { display: flex; min-height: 70px; align-items: center; gap: 12px; padding: 10px 12px; border: 1px dashed #aabeb2; border-radius: 12px; background: rgb(255 255 255 / 76%); cursor: pointer; }
.file-drop:hover, .file-drop:focus-within { border-color: var(--teal); background: #fff; }
.upload-icon { display: grid; width: 38px; height: 38px; flex: 0 0 auto; place-items: center; border-radius: 11px; background: #e7f1eb; color: #3d7461; font-size: 22px; font-weight: 500; }
.file-drop-copy { display: grid; min-width: 0; gap: 3px; }
.file-drop-copy strong { overflow: hidden; color: var(--ink-strong); font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.file-drop-copy span { color: var(--ink-muted); font-size: 10px; }
.browse-button { margin-left: auto; padding: 7px 10px; border: 1px solid var(--line-strong); border-radius: 8px; background: #fff; color: #395b50; font-size: 10px; font-weight: 700; white-space: nowrap; }
.visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; clip-path: inset(50%); }
.form-actions { display: flex; align-items: flex-end; justify-content: space-between; gap: 14px; }
.capacity-field { display: grid; gap: 5px; color: #536760; font-size: 10px; font-weight: 600; }
.capacity-input-wrap { display: flex; height: 36px; align-items: center; gap: 8px; padding: 0 9px; border: 1px solid var(--line-strong); border-radius: 8px; background: #fff; color: var(--ink-muted); font-size: 10px; }
.capacity-input-wrap input { width: 78px; border: 0; outline: none; background: transparent; color: var(--ink-strong); font-size: 12px; font-weight: 600; }
.capacity-input-wrap input:focus-visible { outline: 2px solid #75a99d; outline-offset: 2px; }
.primary-button { display: inline-flex; min-height: 37px; align-items: center; justify-content: center; gap: 15px; padding: 0 15px; border: 1px solid var(--teal-dark); border-radius: 8px; background: var(--teal-dark); color: #fff; cursor: pointer; font-size: 11px; font-weight: 700; transition: background .15s ease, transform .15s ease; }
.primary-button:hover { transform: translateY(-1px); background: #19584f; }
.primary-button:disabled { cursor: wait; opacity: .72; transform: none; }
.form-message { margin: 0; color: #8b4448; font-size: 11px; line-height: 1.5; }
.form-message.is-success { color: #34735d; }

.results-section { padding-top: 31px; }
.section-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 18px; margin-bottom: 15px; }
.section-heading h2 { margin: 0 0 5px; font-size: 19px; letter-spacing: -.03em; }
.section-description { margin: 0; color: var(--ink-muted); font-size: 11px; }
.portfolio-count { padding: 6px 10px; border: 1px solid var(--line); border-radius: 99px; background: #fff; color: #587069; font-size: 10px; font-weight: 600; white-space: nowrap; }
.metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 13px; margin-bottom: 15px; }
.metric-card { min-height: 112px; padding: 16px 17px; border: 1px solid var(--line); border-radius: 14px; background: var(--surface); box-shadow: 0 5px 16px rgb(36 63 53 / 3%); }
.metric-card-top { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.metric-label { color: var(--ink-muted); font-size: 10px; font-weight: 600; }
.metric-icon { display: grid; width: 27px; height: 27px; place-items: center; border-radius: 9px; background: var(--teal-soft); color: #397366; font-size: 13px; }
.metric-card:nth-child(2) .metric-icon { background: var(--blue-soft); color: #597b96; }
.metric-card:nth-child(3) .metric-icon { background: var(--amber-soft); color: #8d6639; }
.metric-card:nth-child(4) .metric-icon { background: var(--rose-soft); color: #92575a; }
.metric-value { display: block; margin-top: 9px; color: var(--ink-strong); font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; font-size: 25px; font-weight: 700; letter-spacing: -.04em; line-height: 1.15; }
.metric-help { display: block; margin-top: 5px; color: var(--ink-soft); font-size: 9px; }

.insight-grid { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(300px, .85fr); gap: 15px; }
.card { min-width: 0; padding: 19px 20px 17px; border: 1px solid var(--line); border-radius: 15px; background: var(--surface); box-shadow: 0 5px 16px rgb(36 63 53 / 3%); }
.card-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 15px; margin-bottom: 18px; }
.card-heading h3 { margin: 0 0 4px; font-size: 14px; letter-spacing: -.02em; }
.card-heading p { margin: 0; color: var(--ink-muted); font-size: 10px; }
.chart-mark { display: grid; width: 30px; height: 30px; flex: 0 0 auto; place-items: center; border-radius: 9px; background: #edf4ef; color: #547c69; font-size: 17px; }
.capacity-mark { background: #edf1f5; color: #617b91; }
.band-list { display: grid; gap: 14px; }
.band-row { display: grid; grid-template-columns: 77px minmax(70px, 1fr) 58px; align-items: center; gap: 12px; }
.band-label { color: #4b6058; font-size: 10px; font-weight: 600; }
.band-track { height: 10px; overflow: hidden; border-radius: 99px; background: #edf1ee; }
.band-fill { display: block; height: 100%; min-width: 0; border-radius: inherit; transition: width .45s ease; }
.band-row[data-band="Lower"] .band-fill { background: #76a994; }
.band-row[data-band="Moderate"] .band-fill { background: #7894a8; }
.band-row[data-band="Elevated"] .band-fill { background: #c49a61; }
.band-row[data-band="Highest"] .band-fill { background: #b97778; }
.band-value { color: #3f554c; font-size: 10px; font-variant-numeric: tabular-nums; text-align: right; }
.band-value strong { color: var(--ink-strong); font-weight: 700; }
.band-value span { color: var(--ink-soft); }
.chart-note { margin-top: 17px; padding-top: 12px; border-top: 1px solid #edf1ee; color: var(--ink-muted); }
.chart-note summary { width: fit-content; color: #466e61; cursor: pointer; font-size: 10px; font-weight: 600; }
.chart-note p { max-width: 640px; margin: 9px 0 0; font-size: 10px; line-height: 1.6; }

.capacity-visual { display: flex; min-height: 150px; align-items: center; justify-content: center; gap: clamp(18px, 4vw, 47px); }
.capacity-ring { display: grid; width: 142px; height: 142px; flex: 0 0 auto; place-items: center; border-radius: 50%; background: conic-gradient(#438675 0deg, #438675 0deg, #e8efeb 0deg 360deg); }
.ring-center { display: grid; width: 110px; height: 110px; align-content: center; justify-items: center; border-radius: 50%; background: #fff; }
.ring-center strong { color: var(--ink-strong); font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; font-size: 24px; letter-spacing: -.04em; }
.ring-center span { color: var(--ink-muted); font-size: 9px; }
.capacity-legend { display: grid; gap: 13px; }
.legend-item { display: grid; grid-template-columns: 9px auto; align-items: start; gap: 8px; color: var(--ink-muted); font-size: 10px; }
.legend-dot { width: 8px; height: 8px; margin-top: 4px; border-radius: 50%; background: #438675; }
.legend-item:nth-child(2) .legend-dot { background: #9bb9aa; }
.legend-item:nth-child(3) .legend-dot { background: #d5ded8; }
.legend-copy { display: grid; gap: 1px; }
.legend-copy strong { color: #42574f; font-size: 11px; font-weight: 700; }
.legend-copy span { color: var(--ink-soft); font-size: 9px; }
.capacity-footnote { min-height: 28px; margin-top: 9px; padding-top: 10px; border-top: 1px solid #edf1ee; color: var(--ink-muted); font-size: 9px; line-height: 1.5; }

.interpretation-note { align-items: flex-start; margin-top: 15px; padding: 11px 13px; border-radius: 11px; }
.interpretation-note p { font-size: 10px; }
.interpretation-note strong { color: #38584d; }

.explore-view { padding-top: 31px; }
.explore-heading { margin-bottom: 15px; }
.filters-card { margin-bottom: 15px; }
.filter-heading { align-items: center; margin-bottom: 15px; }
.filter-heading .text-button { flex: 0 0 auto; }
.filter-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.filter-control { display: grid; min-width: 0; gap: 5px; color: #536760; font-size: 10px; font-weight: 600; }
.filter-control input, .filter-control select, .group-field select {
  width: 100%; min-width: 0; height: 36px; padding: 0 9px; border: 1px solid var(--line-strong);
  border-radius: 8px; background: #fff; color: var(--ink-strong); font-size: 11px;
}
.feature-value-control { align-content: end; }
.feature-value-control[hidden] { display: none; }
.feature-value-control > span { color: #536760; font-size: 10px; font-weight: 600; }
.feature-range-inputs { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.filter-message { min-height: 16px; margin: 8px 0 0; color: #8b4448; font-size: 10px; }
.explore-summary-grid { display: grid; grid-template-columns: minmax(0, .85fr) minmax(0, 1.15fr); gap: 15px; margin-bottom: 15px; }
.distribution-card, .group-card { min-width: 0; }
.score-distribution { display: grid; gap: 8px; }
.distribution-row { display: grid; grid-template-columns: 48px minmax(40px, 1fr) 77px; align-items: center; gap: 9px; }
.distribution-label { color: #4b6058; font-size: 9px; font-variant-numeric: tabular-nums; }
.distribution-track { display: block; height: 9px; overflow: hidden; border-radius: 99px; background: #edf1ee; }
.distribution-fill { display: block; height: 100%; border-radius: inherit; background: #6b9b87; transition: width .25s ease; }
.distribution-value { color: var(--ink-muted); font-size: 9px; font-variant-numeric: tabular-nums; text-align: right; white-space: nowrap; }
.group-heading { align-items: center; }
.group-field { display: grid; min-width: 110px; gap: 3px; color: var(--ink-muted); font-size: 9px; }
.group-field select { height: 31px; }
.table-scroll { width: 100%; overflow: auto; }
.group-table, .customer-table { width: 100%; border-collapse: collapse; font-size: 10px; text-align: left; }
.group-table th, .customer-table th { padding: 9px 8px; border-bottom: 1px solid var(--line-strong); color: var(--ink-muted); font-size: 9px; font-weight: 700; white-space: nowrap; }
.group-table td, .customer-table td { padding: 9px 8px; border-bottom: 1px solid #edf1ee; color: #40564d; font-variant-numeric: tabular-nums; white-space: nowrap; }
.group-table tbody tr:last-child td, .customer-table tbody tr:last-child td { border-bottom: 0; }
.table-note { margin: 10px 0 0; color: var(--ink-soft); font-size: 9px; line-height: 1.5; }
.customer-results-card { margin-bottom: 15px; }
.customer-results-card .card-heading { align-items: center; margin-bottom: 9px; }
.pagination-controls { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-top: 12px; padding-top: 12px; border-top: 1px solid #edf1ee; color: var(--ink-muted); font-size: 10px; }
.pagination-controls > div { display: flex; gap: 7px; }
.secondary-button { min-height: 30px; padding: 0 10px; border: 1px solid var(--line-strong); border-radius: 7px; background: #fff; color: #456258; cursor: pointer; font-size: 10px; font-weight: 600; }
.secondary-button:disabled { cursor: default; color: #9aa8a2; background: #f7f9f7; }

.empty-state { display: grid; justify-items: center; padding: 34px 20px 30px; color: var(--ink-muted); text-align: center; }
.empty-illustration { position: relative; width: 126px; height: 91px; margin-bottom: 13px; }
.illustration-card { position: absolute; width: 80px; height: 56px; border: 1px solid #dce7e0; border-radius: 10px; background: #fff; box-shadow: var(--shadow); }
.card-one { top: 7px; left: 16px; transform: rotate(-8deg); }
.card-two { top: 5px; left: 35px; transform: rotate(7deg); }
.illustration-chart { position: absolute; right: 9px; bottom: 8px; display: flex; width: 57px; height: 41px; align-items: flex-end; gap: 5px; padding: 6px; border: 1px solid #dce7e0; border-radius: 9px; background: #f8fbf8; }
.illustration-chart i { flex: 1; border-radius: 3px 3px 1px 1px; background: #8bb7a4; }
.illustration-chart i:nth-child(1) { height: 36%; }
.illustration-chart i:nth-child(2) { height: 58%; background: #9bb1bb; }
.illustration-chart i:nth-child(3) { height: 45%; background: #cfb082; }
.illustration-chart i:nth-child(4) { height: 78%; background: #c18787; }
.empty-state h2 { margin: 0 0 5px; font-size: 15px; letter-spacing: -.02em; }
.empty-state p { max-width: 410px; margin: 0; color: var(--ink-muted); font-size: 11px; }
.page-footer { display: flex; justify-content: space-between; gap: 15px; margin-top: 12px; padding: 14px 0 3px; border-top: 1px solid var(--line); color: var(--ink-soft); font-size: 9px; }

@media (max-width: 1120px) {
  .main-content { padding-right: 28px; padding-left: 28px; }
  .sidebar { width: 220px; }
  .main-content { margin-left: 220px; }
  .analysis-panel { grid-template-columns: 1fr; gap: 16px; }
  .analysis-panel-copy p { max-width: 520px; }
  .filter-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 820px) {
  .sidebar { position: static; width: auto; height: auto; padding: 13px 18px; border-right: 0; border-bottom: 1px solid var(--line); }
  .brand { padding: 0; }
  .nav-label, .sidebar-bottom { display: none; }
  .primary-nav { display: flex; overflow-x: auto; gap: 4px; margin-top: 13px; }
  .nav-link { min-height: 38px; flex: 0 0 auto; padding: 0 10px; font-size: 11px; }
  .nav-icon { width: 16px; font-size: 15px; }
  .nav-soon { display: none; }
  .main-content { margin-left: 0; padding: 0 20px 20px; }
  .topbar { height: 55px; }
  .insight-grid { grid-template-columns: 1fr; }
  .explore-summary-grid { grid-template-columns: 1fr; }
}

@media (max-width: 560px) {
  .main-content { padding-right: 14px; padding-left: 14px; }
  .page-heading { align-items: flex-start; flex-direction: column; gap: 10px; padding: 23px 0 17px; }
  .analysis-panel { padding: 17px 14px; }
  .file-drop { gap: 9px; }
  .browse-button { padding: 7px; font-size: 9px; }
  .file-drop-copy span { max-width: 180px; font-size: 9px; }
  .form-actions { align-items: stretch; flex-direction: column; }
  .capacity-field { align-items: flex-start; }
  .primary-button { width: 100%; }
  .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; }
  .metric-card { min-height: 104px; padding: 13px; }
  .metric-value { font-size: 22px; }
  .card { padding: 16px 14px; }
  .band-row { grid-template-columns: 68px minmax(45px, 1fr) 52px; gap: 8px; }
  .capacity-visual { gap: 17px; }
  .capacity-ring { width: 120px; height: 120px; }
  .ring-center { width: 94px; height: 94px; }
  .ring-center strong { font-size: 21px; }
  .section-heading { align-items: flex-start; flex-direction: column; }
  .filter-grid { grid-template-columns: 1fr 1fr; }
  .group-heading { align-items: flex-start; flex-direction: column; }
  .page-footer { flex-direction: column; gap: 4px; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; }
}

```

### `src/propensity_prediction/dashboard/static/app.js`

```javascript
"use strict";

const INTEGER_FIELDS = new Set([
  "ID", "SEX", "EDUCATION", "MARRIAGE",
  "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
]);
const NON_NEGATIVE_FIELDS = new Set([
  "LIMIT_BAL", "PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6",
]);
const INTEGER_RANGES = {
  SEX: [1, 2],
  EDUCATION: [0, 4],
  MARRIAGE: [0, 3],
};
const CATEGORICAL_FIELDS = new Set([
  "SEX", "EDUCATION", "MARRIAGE", "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
]);
const PAGE_SIZE = 50;

const elements = {
  form: document.querySelector("#analysis-form"),
  file: document.querySelector("#portfolio-file"),
  fileName: document.querySelector("#file-name"),
  fileHint: document.querySelector("#file-hint"),
  capacity: document.querySelector("#review-capacity"),
  runButton: document.querySelector("#run-analysis"),
  formMessage: document.querySelector("#form-message"),
  status: document.querySelector("#service-status"),
  healthCheck: document.querySelector("#health-check"),
  emptyState: document.querySelector("#empty-state"),
  results: document.querySelector("#results-section"),
  metrics: document.querySelector("#metric-grid"),
  riskBands: document.querySelector("#risk-band-chart"),
  riskReference: document.querySelector("#risk-band-reference"),
  capacityRing: document.querySelector("#capacity-ring"),
  capacityPercent: document.querySelector("#capacity-percent"),
  capacityLegend: document.querySelector("#capacity-legend"),
  capacityFootnote: document.querySelector("#capacity-footnote"),
  portfolioCount: document.querySelector("#portfolio-count"),
  analysisMeta: document.querySelector("#analysis-meta"),
  analysisMetaText: document.querySelector("#analysis-meta-text"),
  exploreView: document.querySelector("#explore-view"),
  viewLinks: [...document.querySelectorAll("[data-view]")],
  exploreCount: document.querySelector("#explore-count"),
  customerIdFilter: document.querySelector("#filter-customer-id"),
  scoreMinFilter: document.querySelector("#filter-score-min"),
  scoreMaxFilter: document.querySelector("#filter-score-max"),
  riskBandFilter: document.querySelector("#filter-risk-band"),
  reviewStatusFilter: document.querySelector("#filter-review-status"),
  featureFilter: document.querySelector("#filter-feature"),
  featureValueControl: document.querySelector("#feature-value-control"),
  resetFilters: document.querySelector("#reset-filters"),
  filterMessage: document.querySelector("#filter-message"),
  groupByField: document.querySelector("#group-by-field"),
  scoreDistribution: document.querySelector("#score-distribution"),
  groupSummaryBody: document.querySelector("#group-summary-body"),
  groupTableNote: document.querySelector("#group-table-note"),
  customerResultsBody: document.querySelector("#customer-results-body"),
  pageCount: document.querySelector("#page-count"),
  pageStatus: document.querySelector("#page-status"),
  previousPage: document.querySelector("#previous-page"),
  nextPage: document.querySelector("#next-page"),
};

let dashboardConfig = null;
let selectedFile = null;
let currentPortfolio = [];
let currentResult = null;
let filteredPortfolio = [];
let currentPage = 0;
let activeView = "overview";
const quartileBoundaryCache = new Map();

const percentFormatter = new Intl.NumberFormat(undefined, {
  style: "percent",
  maximumFractionDigits: 1,
});
const numberFormatter = new Intl.NumberFormat(undefined, {
  maximumFractionDigits: 0,
});

function showMessage(message, kind = "error") {
  elements.formMessage.textContent = message;
  elements.formMessage.hidden = false;
  elements.formMessage.classList.toggle("is-success", kind === "success");
}

function clearMessage() {
  elements.formMessage.textContent = "";
  elements.formMessage.hidden = true;
  elements.formMessage.classList.remove("is-success");
}

function setServiceStatus(ready, message) {
  elements.status.classList.toggle("is-ready", ready);
  elements.status.classList.toggle("is-error", !ready);
  elements.status.lastChild.textContent = ` ${message}`;
}

function parseCsv(text) {
  const source = text.replace(/^\uFEFF/, "");
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;
  let afterQuote = false;

  for (let index = 0; index < source.length; index += 1) {
    const character = source[index];
    const next = source[index + 1];

    if (inQuotes) {
      if (character === '"' && next === '"') {
        field += '"';
        index += 1;
      } else if (character === '"') {
        inQuotes = false;
        afterQuote = true;
      } else {
        field += character;
      }
      continue;
    }

    if (afterQuote) {
      if (character === ",") {
        row.push(field);
        field = "";
        afterQuote = false;
      } else if (character === "\n" || character === "\r") {
        row.push(field);
        appendCsvRow(rows, row);
        row = [];
        field = "";
        afterQuote = false;
        if (character === "\r" && next === "\n") index += 1;
      } else if (character === " " || character === "\t") {
        // Ignore whitespace between a closing quote and its delimiter.
      } else {
        throw new Error("The CSV has invalid characters after a quoted value.");
      }
      continue;
    }

    if (character === '"') {
      if (field.length > 0) {
        throw new Error("The CSV contains a quote inside an unquoted value.");
      }
      inQuotes = true;
    } else if (character === ",") {
      row.push(field);
      field = "";
    } else if (character === "\n" || character === "\r") {
      row.push(field);
      appendCsvRow(rows, row);
      row = [];
      field = "";
      if (character === "\r" && next === "\n") index += 1;
    } else {
      field += character;
    }
  }

  if (inQuotes) throw new Error("The CSV contains an unclosed quoted value.");
  if (field.length > 0 || row.length > 0 || afterQuote) {
    row.push(field);
    appendCsvRow(rows, row);
  }
  return rows;
}

function appendCsvRow(rows, row) {
  if (row.length === 1 && row[0] === "") return;
  rows.push(row);
}

function parseNumeric(value, column, csvRowNumber) {
  const trimmed = value.trim();
  const decimalPattern = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/;
  if (!decimalPattern.test(trimmed)) {
    throw new Error(`${column} must contain numeric values. Check CSV row ${csvRowNumber}.`);
  }
  const number = Number(trimmed);
  if (!Number.isFinite(number)) {
    throw new Error(`${column} must contain finite numeric values. Check CSV row ${csvRowNumber}.`);
  }
  if (INTEGER_FIELDS.has(column) && !Number.isInteger(number)) {
    throw new Error(`${column} must contain integer values. Check CSV row ${csvRowNumber}.`);
  }
  if (column === "ID" && !Number.isSafeInteger(number)) {
    throw new Error(`ID must be a safely representable integer. Check CSV row ${csvRowNumber}.`);
  }
  if (NON_NEGATIVE_FIELDS.has(column) && number < 0) {
    throw new Error(`${column} must be non-negative. Check CSV row ${csvRowNumber}.`);
  }
  if (Object.hasOwn(INTEGER_RANGES, column)) {
    const [minimum, maximum] = INTEGER_RANGES[column];
    if (number < minimum || number > maximum) {
      throw new Error(`${column} must use values from ${minimum} through ${maximum}. Check CSV row ${csvRowNumber}.`);
    }
  }
  return number;
}

function validateCsvRows(rows) {
  if (!rows.length) throw new Error("The CSV is empty.");
  const [headers, ...dataRows] = rows;
  if (!headers.length || headers.every((header) => header === "")) {
    throw new Error("The CSV must include a header row.");
  }
  if (new Set(headers).size !== headers.length) {
    throw new Error("The CSV contains duplicate column names.");
  }
  if (headers.includes("DEFAULT")) {
    throw new Error("DEFAULT is a historical outcome, not an input for prediction. Upload a prediction-time file without this column.");
  }

  const required = dashboardConfig.required_columns;
  const missing = required.filter((column) => !headers.includes(column));
  const extra = headers.filter((column) => !required.includes(column));
  if (missing.length || extra.length) {
    const problems = [];
    if (missing.length) problems.push(`Missing required columns: ${missing.join(", ")}.`);
    if (extra.length) problems.push(`Unrecognized columns: ${extra.join(", ")}.`);
    throw new Error(problems.join(" "));
  }
  if (!dataRows.length) throw new Error("The CSV must contain at least one customer row.");
  if (dataRows.length > dashboardConfig.max_customer_rows) {
    throw new Error(`The CSV contains ${numberFormatter.format(dataRows.length)} customer rows; the maximum is ${numberFormatter.format(dashboardConfig.max_customer_rows)}. Split the portfolio into smaller files.`);
  }

  const seenIds = new Set();
  return dataRows.map((values, rowIndex) => {
    const csvRowNumber = rowIndex + 2;
    if (values.length !== headers.length) {
      throw new Error(`CSV row ${csvRowNumber} has ${values.length} values; expected ${headers.length}.`);
    }
    const sourceRow = Object.fromEntries(headers.map((header, index) => [header, values[index]]));
    const customer = {};
    for (const column of required) {
      const value = sourceRow[column];
      if (value === undefined || value.trim() === "") {
        throw new Error(`${column} cannot be blank. Check CSV row ${csvRowNumber}.`);
      }
      customer[column] = parseNumeric(value, column, csvRowNumber);
    }
    if (seenIds.has(customer.ID)) {
      throw new Error(`ID values must be unique. Duplicate ID ${customer.ID} appears in CSV row ${csvRowNumber}.`);
    }
    seenIds.add(customer.ID);
    return customer;
  });
}

function formatCount(value) {
  return numberFormatter.format(value);
}

function formatPercent(value) {
  return percentFormatter.format(value);
}

function renderMetricCards(result) {
  const capacity = result.capacity;
  const summary = result.portfolio_summary.probability_summary;
  const metrics = [
    { label: "Customers scored", value: formatCount(result.population_count), help: "Full uploaded portfolio", icon: "▦" },
    { label: "Mean predicted risk", value: formatPercent(summary.mean), help: "Average model estimate", icon: "⌁" },
    { label: "Selected for review", value: formatCount(capacity.selected_count), help: "Under the supplied capacity", icon: "✓" },
    { label: "Unused capacity", value: formatCount(capacity.unused_capacity), help: "After tie-aware selection", icon: "↗" },
  ];

  elements.metrics.replaceChildren(...metrics.map((metric) => {
    const card = document.createElement("article");
    card.className = "metric-card";
    card.innerHTML = `
      <div class="metric-card-top">
        <span class="metric-label">${metric.label}</span>
        <span class="metric-icon" aria-hidden="true">${metric.icon}</span>
      </div>
      <strong class="metric-value">${metric.value}</strong>
      <span class="metric-help">${metric.help}</span>
    `;
    return card;
  }));
}

function renderRiskBands(summary) {
  const bands = summary.risk_bands;
  elements.riskBands.replaceChildren(...bands.map((band) => {
    const row = document.createElement("div");
    row.className = "band-row";
    row.dataset.band = band.label;
    row.setAttribute("role", "listitem");

    const label = document.createElement("span");
    label.className = "band-label";
    label.textContent = band.label;

    const track = document.createElement("span");
    track.className = "band-track";
    track.setAttribute("aria-hidden", "true");
    const fill = document.createElement("span");
    fill.className = "band-fill";
    fill.style.width = `${Math.max(0, Math.min(1, band.portfolio_share)) * 100}%`;
    track.append(fill);

    const value = document.createElement("span");
    value.className = "band-value";
    value.innerHTML = `<strong>${formatCount(band.customer_count)}</strong> <span>· ${formatPercent(band.portfolio_share)}</span>`;
    row.append(label, track, value);
    return row;
  }));
  elements.riskReference.textContent = `${summary.risk_band_reference}. The fixed validation-cohort method is descriptive; these bands are not action thresholds.`;
}

function renderCapacity(result) {
  const capacity = result.capacity;
  const denominator = capacity.target_review_count;
  const utilization = denominator > 0 ? capacity.selected_count / denominator : 0;
  const safeUtilization = Math.max(0, Math.min(1, utilization));
  const percentage = denominator > 0 ? Math.round(safeUtilization * 100) : null;
  const degrees = safeUtilization * 360;

  elements.capacityRing.style.background = `conic-gradient(#438675 0deg ${degrees}deg, #e8efeb ${degrees}deg 360deg)`;
  elements.capacityPercent.textContent = percentage === null ? "—" : `${percentage}%`;

  const items = [
    { label: "Requested", count: capacity.requested_review_count, note: "Analyst capacity" },
    { label: "Selected", count: capacity.selected_count, note: "Entered the queue" },
    { label: "Unused", count: capacity.unused_capacity, note: "Tie-aware remainder" },
  ];
  elements.capacityLegend.replaceChildren(...items.map((item) => {
    const entry = document.createElement("div");
    entry.className = "legend-item";
    const dot = document.createElement("span");
    dot.className = "legend-dot";
    dot.setAttribute("aria-hidden", "true");
    const copy = document.createElement("span");
    copy.className = "legend-copy";
    const strong = document.createElement("strong");
    strong.textContent = `${item.label}: ${formatCount(item.count)}`;
    const note = document.createElement("span");
    note.textContent = item.note;
    copy.append(strong, note);
    entry.append(dot, copy);
    return entry;
  }));

  if (denominator === 0) {
    elements.capacityFootnote.textContent = "No review capacity was requested; no customers were selected.";
  } else if (capacity.unused_capacity > 0) {
    elements.capacityFootnote.textContent = "Some capacity remained unused because the queue keeps equal-score customers together at the selection boundary.";
  } else {
    elements.capacityFootnote.textContent = "The requested target was filled. Equal-score groups are kept together at the selection boundary.";
  }
}

function getRiskBand(record) {
  const score = record.predicted_default_probability;
  return currentResult.portfolio_summary.risk_bands.find((band) =>
    (band.lower_bound_exclusive === null || score > band.lower_bound_exclusive)
    && (band.upper_bound_inclusive === null || score <= band.upper_bound_inclusive)
  )?.label ?? "Unassigned";
}

function resetExploreFilters() {
  elements.customerIdFilter.value = "";
  elements.scoreMinFilter.value = "0";
  elements.scoreMaxFilter.value = "1";
  elements.riskBandFilter.value = "";
  elements.reviewStatusFilter.value = "";
  elements.featureFilter.value = "";
  elements.featureValueControl.replaceChildren();
  elements.featureValueControl.hidden = true;
  elements.filterMessage.textContent = "";
  currentPage = 0;
}

function initializeExploreFields() {
  const fields = dashboardConfig.required_columns.filter((field) => field !== "ID");
  elements.featureFilter.replaceChildren(new Option("No input filter", ""));
  elements.groupByField.replaceChildren(...fields.map((field) => new Option(field, field)));
  elements.featureFilter.append(...fields.map((field) => new Option(field, field)));
  elements.groupByField.value = "SEX";
}

function renderFeatureValueControl() {
  const field = elements.featureFilter.value;
  elements.featureValueControl.replaceChildren();
  if (!field || !currentPortfolio.length) {
    elements.featureValueControl.hidden = true;
    return;
  }
  elements.featureValueControl.hidden = false;
  if (CATEGORICAL_FIELDS.has(field)) {
    const label = document.createElement("label");
    label.className = "filter-control";
    const title = document.createElement("span");
    title.textContent = `${field} value`;
    const select = document.createElement("select");
    select.id = "feature-filter-value";
    select.append(new Option("All values", ""));
    [...new Set(currentPortfolio.map((row) => row[field]))]
      .sort((left, right) => left - right)
      .forEach((value) => select.append(new Option(String(value), String(value))));
    select.addEventListener("change", () => runExploreFilters(true));
    label.append(title, select);
    elements.featureValueControl.append(label);
    return;
  }

  const values = currentPortfolio.map((row) => row[field]);
  const minimum = Math.min(...values);
  const maximum = Math.max(...values);
  const label = document.createElement("span");
  label.textContent = `${field} range`;
  const inputs = document.createElement("div");
  inputs.className = "feature-range-inputs";
  for (const [caption, id, value] of [["Min", "feature-filter-min", minimum], ["Max", "feature-filter-max", maximum]]) {
    const inputLabel = document.createElement("label");
    inputLabel.className = "visually-hidden";
    inputLabel.htmlFor = id;
    inputLabel.textContent = `${field} ${caption.toLowerCase()}`;
    const input = document.createElement("input");
    input.type = "number";
    input.id = id;
    input.step = "any";
    input.value = String(value);
    input.dataset.bound = caption.toLowerCase();
    input.addEventListener("input", () => runExploreFilters(true));
    inputs.append(inputLabel, input);
  }
  elements.featureValueControl.append(label, inputs);
}

function numericQuantile(values, proportion) {
  const sorted = [...values].sort((left, right) => left - right);
  const position = (sorted.length - 1) * proportion;
  const lower = Math.floor(position);
  const fraction = position - lower;
  return sorted[lower + 1] === undefined
    ? sorted[lower]
    : sorted[lower] + fraction * (sorted[lower + 1] - sorted[lower]);
}

function getQuartileBoundaries(field) {
  if (!quartileBoundaryCache.has(field)) {
    const values = currentPortfolio.map((row) => row[field]);
    quartileBoundaryCache.set(field, [
      numericQuantile(values, 0.25),
      numericQuantile(values, 0.5),
      numericQuantile(values, 0.75),
    ]);
  }
  return quartileBoundaryCache.get(field);
}

function getQuartileIndex(value, field) {
  const [first, second, third] = getQuartileBoundaries(field);
  if (value <= first) return 0;
  if (value <= second) return 1;
  if (value <= third) return 2;
  return 3;
}

function getGroupLabel(value, field, index = null) {
  if (CATEGORICAL_FIELDS.has(field)) return String(value);
  const [first, second, third] = getQuartileBoundaries(field);
  const formatBoundary = (boundary) => boundary.toLocaleString(undefined, { maximumSignificantDigits: 7 });
  if (index === 0) return `≤ ${formatBoundary(first)}`;
  if (index === 1) return `${formatBoundary(first)} – ${formatBoundary(second)}`;
  if (index === 2) return `${formatBoundary(second)} – ${formatBoundary(third)}`;
  return `> ${formatBoundary(third)}`;
}

function applyExploreFilters() {
  const idQuery = elements.customerIdFilter.value.trim();
  const minimumScore = elements.scoreMinFilter.value === "" ? 0 : Number(elements.scoreMinFilter.value);
  const maximumScore = elements.scoreMaxFilter.value === "" ? 1 : Number(elements.scoreMaxFilter.value);
  if (minimumScore > maximumScore) {
    elements.filterMessage.textContent = "Minimum predicted risk must not exceed maximum predicted risk.";
    return null;
  }
  elements.filterMessage.textContent = "";
  const band = elements.riskBandFilter.value;
  const reviewStatus = elements.reviewStatusFilter.value;
  const field = elements.featureFilter.value;
  const categoryValue = document.querySelector("#feature-filter-value")?.value ?? "";
  const featureMinimum = document.querySelector("#feature-filter-min")?.value;
  const featureMaximum = document.querySelector("#feature-filter-max")?.value;

  return currentPortfolio.filter((record) => {
    const score = record.predicted_default_probability;
    if (idQuery && !String(record.customer_id).includes(idQuery)) return false;
    if (score < minimumScore || score > maximumScore) return false;
    if (band && getRiskBand(record) !== band) return false;
    if (reviewStatus === "selected" && !record.selected_for_review) return false;
    if (reviewStatus === "not-selected" && record.selected_for_review) return false;
    if (field && CATEGORICAL_FIELDS.has(field) && categoryValue && String(record[field]) !== categoryValue) return false;
    if (field && !CATEGORICAL_FIELDS.has(field)) {
      if (featureMinimum !== undefined && featureMinimum !== "" && record[field] < Number(featureMinimum)) return false;
      if (featureMaximum !== undefined && featureMaximum !== "" && record[field] > Number(featureMaximum)) return false;
    }
    return true;
  });
}

function renderScoreDistribution(rows) {
  const bins = Array.from({ length: 10 }, (_, index) => ({
    lower: index / 10,
    upper: (index + 1) / 10,
    count: 0,
  }));
  rows.forEach((record) => {
    const index = Math.min(9, Math.floor(record.predicted_default_probability * 10));
    bins[index].count += 1;
  });
  const denominator = rows.length;
  elements.scoreDistribution.replaceChildren(...bins.map((bin) => {
    const row = document.createElement("div");
    row.className = "distribution-row";
    row.setAttribute("role", "listitem");
    const label = document.createElement("span");
    label.className = "distribution-label";
    label.textContent = `${Math.round(bin.lower * 100)}–${Math.round(bin.upper * 100)}%`;
    const track = document.createElement("span");
    track.className = "distribution-track";
    track.setAttribute("aria-hidden", "true");
    const fill = document.createElement("span");
    fill.className = "distribution-fill";
    const share = denominator ? bin.count / denominator : 0;
    fill.style.width = `${share * 100}%`;
    track.append(fill);
    const value = document.createElement("span");
    value.className = "distribution-value";
    value.textContent = `${formatCount(bin.count)} · ${formatPercent(share)}`;
    row.append(label, track, value);
    return row;
  }));
}

function renderGroupSummary(rows) {
  const field = elements.groupByField.value;
  if (!rows.length) {
    const emptyRow = document.createElement("tr");
    const message = document.createElement("td");
    message.colSpan = 5;
    message.textContent = "No customers match the current filters.";
    emptyRow.append(message);
    elements.groupSummaryBody.replaceChildren(emptyRow);
    elements.groupTableNote.textContent = "Adjust or reset the filters to compare groups.";
    return;
  }
  const groups = new Map();
  rows.forEach((record) => {
    const groupKey = CATEGORICAL_FIELDS.has(field)
      ? String(record[field])
      : String(getQuartileIndex(record[field], field));
    if (!groups.has(groupKey)) {
      const groupIndex = CATEGORICAL_FIELDS.has(field) ? null : Number(groupKey);
      groups.set(groupKey, { label: getGroupLabel(record[field], field, groupIndex), records: [] });
    }
    groups.get(groupKey).records.push(record);
  });
  const orderedGroups = [...groups.entries()].sort((left, right) => {
    if (CATEGORICAL_FIELDS.has(field)) return Number(left[0]) - Number(right[0]);
    return Number(left[0]) - Number(right[0]);
  });
  elements.groupSummaryBody.replaceChildren(...orderedGroups.map(([, group]) => {
    const { label, records } = group;
    const row = document.createElement("tr");
    const values = [
      label,
      formatCount(records.length),
      formatPercent(rows.length ? records.length / rows.length : 0),
      formatPercent(records.reduce((sum, item) => sum + item.predicted_default_probability, 0) / records.length),
      formatCount(records.filter((item) => item.selected_for_review).length),
    ];
    values.forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    return row;
  }));
  elements.groupTableNote.textContent = CATEGORICAL_FIELDS.has(field)
    ? `Encoded values for ${field} are shown as supplied; group shares use the filtered cohort.`
    : `Quartile boundaries for ${field} are calculated from the full portfolio; shares use the filtered cohort.`;
}

function renderCustomerTable(rows) {
  const pageCount = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  currentPage = Math.min(currentPage, pageCount - 1);
  const start = currentPage * PAGE_SIZE;
  const visibleRows = rows.slice(start, start + PAGE_SIZE);
  const tableRows = visibleRows.map((record) => {
    const row = document.createElement("tr");
    const values = [
      formatCount(record.risk_rank),
      formatCount(record.customer_id),
      formatPercent(record.predicted_default_probability),
      getRiskBand(record),
      record.selected_for_review ? "Selected" : "Not selected",
    ];
    values.forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    return row;
  });
  if (!rows.length) {
    const emptyRow = document.createElement("tr");
    const message = document.createElement("td");
    message.colSpan = 5;
    message.textContent = "No customers match the current filters.";
    emptyRow.append(message);
    tableRows.push(emptyRow);
  }
  elements.customerResultsBody.replaceChildren(...tableRows);
  const first = rows.length ? start + 1 : 0;
  const last = Math.min(start + PAGE_SIZE, rows.length);
  elements.pageCount.textContent = `${formatCount(first)}–${formatCount(last)} of ${formatCount(rows.length)}`;
  elements.pageStatus.textContent = `Page ${currentPage + 1} of ${pageCount}`;
  elements.previousPage.disabled = currentPage === 0;
  elements.nextPage.disabled = currentPage >= pageCount - 1;
}

function runExploreFilters(resetPage = false) {
  if (resetPage) currentPage = 0;
  const rows = applyExploreFilters();
  if (rows === null) return;
  filteredPortfolio = rows;
  elements.exploreCount.textContent = `${formatCount(rows.length)} of ${formatCount(currentPortfolio.length)} customers`;
  renderScoreDistribution(rows);
  renderGroupSummary(rows);
  renderCustomerTable(rows);
}

function setActiveView(view) {
  if (view === "explore" && !currentResult) return;
  activeView = view;
  elements.results.hidden = view !== "overview" || !currentResult;
  elements.exploreView.hidden = view !== "explore" || !currentResult;
  elements.emptyState.hidden = Boolean(currentResult);
  elements.viewLinks.forEach((link) => {
    const active = link.dataset.view === view;
    link.classList.toggle("is-active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  document.querySelector(".breadcrumb").lastChild.textContent = ` ${view === "overview" ? "Overview" : "Explore portfolio"}`;
}

function renderOverview(result, inputRows) {
  currentResult = result;
  const inputsById = new Map(inputRows.map((row) => [row.ID, row]));
  currentPortfolio = result.customers.map((scoredRow) => ({
    ...inputsById.get(scoredRow.customer_id),
    ...scoredRow,
  }));
  quartileBoundaryCache.clear();
  initializeExploreFields();
  resetExploreFilters();
  renderMetricCards(result);
  renderRiskBands(result.portfolio_summary);
  renderCapacity(result);
  elements.portfolioCount.textContent = `${formatCount(result.population_count)} customers`;
  elements.analysisMetaText.textContent = `Scored ${new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}`;
  elements.analysisMeta.hidden = false;
  runExploreFilters();
  setActiveView("overview");
  elements.results.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function readSelectedFile() {
  if (!selectedFile) throw new Error("Choose a CSV file before running the analysis.");
  const text = await selectedFile.text();
  return validateCsvRows(parseCsv(text));
}

async function loadDashboardConfig() {
  const response = await fetch("/v1/dashboard-config");
  if (!response.ok) throw new Error("The dashboard configuration could not be loaded.");
  dashboardConfig = await response.json();
  elements.fileHint.textContent = `ID and all 23 predictors · up to ${formatCount(dashboardConfig.max_customer_rows)} customers`;
  elements.capacity.max = String(dashboardConfig.max_customer_rows);
}

async function checkService() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("The scoring service is unavailable.");
    const health = await response.json();
    if (!health.model_loaded) throw new Error("The API is running, but the model is not loaded.");
    setServiceStatus(true, "Scoring service ready");
  } catch (error) {
    setServiceStatus(false, error.message || "Scoring service unavailable");
  }
}

elements.file.addEventListener("change", () => {
  selectedFile = elements.file.files?.[0] ?? null;
  clearMessage();
  if (selectedFile) {
    elements.fileName.textContent = selectedFile.name;
    elements.fileHint.textContent = `${(selectedFile.size / 1024).toFixed(0)} KB · ready to validate`;
    elements.fileName.title = selectedFile.name;
  } else {
    elements.fileName.textContent = "Choose a CSV file";
  }
});

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearMessage();
  elements.runButton.disabled = true;
  elements.runButton.querySelector("span:first-child").textContent = "Scoring portfolio…";

  try {
    if (!dashboardConfig) await loadDashboardConfig();
    const customers = await readSelectedFile();
    if (elements.capacity.value.trim() === "") {
      throw new Error("Enter a review capacity.");
    }
    const capacity = Number(elements.capacity.value);
    if (!Number.isSafeInteger(capacity) || capacity < 0) {
      throw new Error("Review capacity must be a non-negative whole number.");
    }

    const response = await fetch("/v1/review-queue", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ customers, max_review_count: capacity }),
    });
    const payload = await response.json();
    if (!response.ok) {
      const details = payload?.error?.details?.filter(Boolean).join(" ");
      throw new Error(details || payload?.error?.message || "The scoring request failed.");
    }

    renderOverview(payload, customers);
    setServiceStatus(true, "Scoring service ready");
    showMessage(`Analysis complete for ${formatCount(payload.population_count)} customers.`, "success");
  } catch (error) {
    showMessage(error.message || "The portfolio could not be scored.");
  } finally {
    elements.runButton.disabled = false;
    elements.runButton.querySelector("span:first-child").textContent = "Run analysis";
  }
});

elements.healthCheck.addEventListener("click", checkService);

elements.viewLinks.forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    setActiveView(link.dataset.view);
    if (currentResult) window.location.hash = link.dataset.view;
  });
});

[
  elements.customerIdFilter,
  elements.scoreMinFilter,
  elements.scoreMaxFilter,
  elements.riskBandFilter,
  elements.reviewStatusFilter,
].forEach((control) => control.addEventListener("input", () => runExploreFilters(true)));
[
  elements.riskBandFilter,
  elements.reviewStatusFilter,
].forEach((control) => control.addEventListener("change", () => runExploreFilters(true)));
elements.featureFilter.addEventListener("change", () => {
  renderFeatureValueControl();
  runExploreFilters(true);
});
elements.groupByField.addEventListener("change", () => runExploreFilters(true));
elements.resetFilters.addEventListener("click", () => {
  resetExploreFilters();
  runExploreFilters(true);
});
elements.previousPage.addEventListener("click", () => {
  currentPage = Math.max(0, currentPage - 1);
  renderCustomerTable(filteredPortfolio);
});
elements.nextPage.addEventListener("click", () => {
  currentPage += 1;
  renderCustomerTable(filteredPortfolio);
});

loadDashboardConfig()
  .then(checkService)
  .catch((error) => setServiceStatus(false, error.message));

```

## Limitations to carry forward

- Local filters describe only the uploaded portfolio and are not estimates of causes, intervention outcomes, or fairness.
- Encoded category fields are left as numeric codes until a verified label dictionary is separately agreed.
- Numeric quartile groups can be empty where a field has many tied values; the boundary rule is inclusive and stable, so tied values stay in the same bucket.
- The initial design scans the complete portfolio on each filter change. A 30,000-row responsiveness measurement remains part of Step 9.14.

---

<a id="step-9-7"></a>
## Step 9.7

# Phase 9.7 — Explain Review Capacity and Queue Construction

## Decision

The user chose **Option A: explain the current API result**. The dashboard presents the exact queue already returned by `POST /v1/review-queue`. The API/service remains the only implementation of ranking, tie handling, and selection. No API endpoint or response schema change was needed.

## Queue policy in plain language

1. The API ranks customers by descending predicted default probability.
2. Customers with equal probabilities share the same competition rank.
3. The target count is the smaller of requested capacity and portfolio size.
4. The API selects complete equal-score groups while they fit within the target.
5. If the next tied group would exceed the remaining target, the API leaves that entire group and all lower-scoring groups out. It does not split a tie and does not exceed the target.
6. Unused capacity is the target count minus actual selected count.

The queue output includes a reason code and reason sentence per customer. The dashboard groups these returned reasons into counts; it does not infer or rebuild the decision policy in JavaScript.

## What changed

- The sidebar's **Review queue** item is now a working view.
- Four cards show requested capacity, target count, actual selected count, and unused capacity. Target count is explicitly the capacity capped at portfolio size.
- The view describes descending-risk ranking, competition ranks for equal scores, whole-group selection, and boundary-tie behavior.
- A reason summary counts the API's exact per-customer reason messages, including zero-capacity, tie-boundary, and below-capacity outcomes when present.
- A paginated selected-customer table shows the API's rank, ID, predicted probability, and reason.
- The upload panel now says that changing capacity does not change displayed results until **Run analysis** completes. That run sends the portfolio and new capacity through the existing API again.
- No cumulative sum of probabilities or causal/capture claim was added. The view explains actual API output only.

## Step-by-step code walkthrough

### 1. Review Queue view (`index.html`)

The sidebar link uses the same `data-view` navigation pattern as Overview and Explore. The new `queue-view` contains:

- Capacity cards populated from the response's `capacity` object.
- A short three-part explanation of the decision rule.
- A reason-code rollup table built from the API's per-customer `reason_code` and `reason` fields.
- A selected-only table with rank, customer ID, predicted score, and API explanation, paginated at 50 rows.
- A nearby interpretation note stating that ranking is not an intervention recommendation or intervention-effect estimate.

### 2. Capacity metrics (`renderQueueView` in `app.js`)

The function reads `requested_review_count`, `target_review_count`, `selected_count`, and `unused_capacity` directly. The filled fraction is selected divided by target, with an em dash for a zero target. It does not derive a new target or make selection decisions. `population_count` appears beside the view title so the portfolio size is visible.

### 3. Reason rollup

`renderQueueView` walks the response's already-ranked `customers` list and counts rows by `reason_code`, keeping the corresponding API reason sentence. The UI creates safe text nodes and displays count totals. This is an aggregation of returned decision explanations; no customer is assigned a new reason.

### 4. Selected queue table and pagination

`renderSelectedQueue` filters the API result only by its `selected_for_review` boolean, preserving API order. It renders at most 50 rows per page and uses the response's `risk_rank`, customer ID, predicted probability, and reason. The empty state appears if capacity is zero or a boundary tie leaves no selected records. Previous/Next controls update only the visible page.

### 5. Navigation and refresh behavior

`setActiveView` now supports `queue` and shows it only when a completed result exists. When a new analysis succeeds, `renderOverview` rebuilds the capacity and queue explanation from the new API response. Editing the capacity field alone leaves the prior queue visible; the inline note and queue-view note both identify **Run analysis** as the refresh action.

### 6. Styling (`styles.css`)

The view reuses the existing calm light cards, typography, tables, and pagination. Capacity cards use a four-column grid that becomes two columns on small screens. The policy and reason cards stack on narrower screens. Reason sentences wrap in their table cells rather than forcing the whole page wide.

## Browser verification

- With the 10-customer sample at requested capacity 4, the page showed target 4, selected 4, unused 0, four selected customers in API rank order, and six lower-capacity exclusions.
- With a generated 30,000-row sample derived from the supplied 10-row CSV (same predictor profiles repeated, unique IDs) at requested capacity 100, the API selected 0, reported 100 unused, and returned 3,000 customers at the tied boundary and 27,000 below that boundary. The dashboard displayed those exact reason totals and the empty selected-queue state. This verifies tie explanations with a deliberately large equal-score group; it is not a representative portfolio analysis.
- `git diff --check` passed.

## Complete code listings

The following are the full current contents of the frontend files changed for Step 9.7. The integrated source also includes Steps 9.5 and 9.6 so the view can be understood in context.


### `src/propensity_prediction/dashboard/static/index.html`

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#f4f7f4" />
    <meta
      name="description"
      content="Understand a scored customer portfolio and its review capacity."
    />
    <title>Portfolio overview | Credit risk review</title>
    <link rel="stylesheet" href="/styles.css" />
    <script src="/app.js" defer></script>
  </head>
  <body>
    <div class="app-shell">
      <aside class="sidebar" aria-label="Dashboard navigation">
        <a class="brand" href="/" aria-label="Portfolio review home">
          <span class="brand-mark" aria-hidden="true">P</span>
          <span class="brand-copy">
            <strong>Portfolio</strong>
            <span>Risk review</span>
          </span>
        </a>

        <p class="nav-label">WORKSPACE</p>
        <nav class="primary-nav" aria-label="Primary">
          <a class="nav-link is-active" href="#overview" data-view="overview" aria-current="page">
            <span class="nav-icon" aria-hidden="true">▦</span>
            <span>Overview</span>
          </a>
          <a class="nav-link" href="#explore" data-view="explore">
            <span class="nav-icon" aria-hidden="true">⌕</span>
            <span>Explore portfolio</span>
          </a>
          <a class="nav-link" href="#queue" data-view="queue">
            <span class="nav-icon" aria-hidden="true">≡</span>
            <span>Review queue</span>
          </a>
        </nav>

        <div class="sidebar-bottom">
          <div class="sidebar-note">
            <span class="note-icon" aria-hidden="true">i</span>
            <p>Predicted risk helps prioritize review. It is not an outcome or an action recommendation.</p>
          </div>
          <span class="service-status" id="service-status" role="status">
            <span class="status-dot" aria-hidden="true"></span>
            Checking portfolio scoring
          </span>
        </div>
      </aside>

      <main class="main-content" id="overview">
        <header class="topbar">
          <div class="breadcrumb">Workspace <span aria-hidden="true">/</span> Overview</div>
          <div class="topbar-actions">
            <button class="text-button" id="health-check" type="button">Check status</button>
            <span class="avatar" aria-hidden="true">AR</span>
          </div>
        </header>

        <section class="page-heading" aria-labelledby="page-title">
          <div>
            <p class="eyebrow">PORTFOLIO INSIGHTS</p>
            <h1 id="page-title">Portfolio overview</h1>
            <p class="page-description">A clear view of predicted risk and review capacity for your customer portfolio.</p>
          </div>
          <div class="analysis-meta" id="analysis-meta" hidden>
            <span class="meta-dot" aria-hidden="true"></span>
            <span id="analysis-meta-text">Analysis complete</span>
          </div>
        </section>

        <section class="analysis-panel" aria-labelledby="analysis-title">
          <div class="analysis-panel-copy">
            <span class="step-badge">NEW ANALYSIS</span>
            <h2 id="analysis-title">Start with a customer portfolio</h2>
            <p>Upload a prediction-time CSV, set your review capacity, and score the full portfolio.</p>
          </div>
          <form id="analysis-form" class="analysis-form">
            <label class="file-drop" for="portfolio-file">
              <span class="upload-icon" aria-hidden="true">↑</span>
              <span class="file-drop-copy">
                <strong id="file-name">Choose a CSV file</strong>
                <span id="file-hint">ID and all 23 predictors · up to 30,000 customers</span>
              </span>
              <span class="browse-button">Browse files</span>
            </label>
            <input id="portfolio-file" class="visually-hidden" type="file" accept=".csv,text/csv" />
            <div class="form-actions">
              <label class="capacity-field" for="review-capacity">
                <span>Review capacity</span>
                <span class="capacity-input-wrap">
                  <input id="review-capacity" type="number" min="0" step="1" value="10" inputmode="numeric" />
                  <span>customers</span>
                </span>
              </label>
              <button class="primary-button" id="run-analysis" type="submit">
                <span>Run analysis</span><span aria-hidden="true">→</span>
              </button>
            </div>
            <p class="capacity-refresh-note">Changing capacity takes effect when you run the analysis; the current results stay in place until then.</p>
            <p class="form-message" id="form-message" role="alert" hidden></p>
          </form>
        </section>

        <section class="results-section" id="results-section" aria-labelledby="results-title" hidden>
          <div class="section-heading">
            <div>
              <p class="eyebrow">AT A GLANCE</p>
              <h2 id="results-title">Portfolio snapshot</h2>
              <p class="section-description">Summary of model estimates for the full uploaded portfolio.</p>
            </div>
            <span class="portfolio-count" id="portfolio-count"></span>
          </div>

          <div class="metric-grid" id="metric-grid" aria-label="Portfolio summary metrics"></div>

          <div class="insight-grid">
            <article class="card band-card" aria-labelledby="bands-title">
              <div class="card-heading">
                <div>
                  <h3 id="bands-title">Predicted risk bands</h3>
                  <p>How customers are distributed across the fixed reference bands.</p>
                </div>
                <span class="chart-mark" aria-hidden="true">▥</span>
              </div>
              <div class="band-list" id="risk-band-chart" role="list"></div>
              <details class="chart-note">
                <summary>How to read these bands</summary>
                <p id="risk-band-reference"></p>
                <p>These bands describe relative predicted risk. They are not action thresholds and do not change queue selection.</p>
              </details>
            </article>

            <article class="card capacity-card" aria-labelledby="capacity-title">
              <div class="card-heading">
                <div>
                  <h3 id="capacity-title">Review capacity</h3>
                  <p>How the requested capacity translated into the queue.</p>
                </div>
                <span class="chart-mark capacity-mark" aria-hidden="true">◎</span>
              </div>
              <div class="capacity-visual">
                <div class="capacity-ring" id="capacity-ring" aria-label="Capacity utilization">
                  <div class="ring-center">
                    <strong id="capacity-percent">0%</strong>
                    <span>of target selected</span>
                  </div>
                </div>
                <div class="capacity-legend" id="capacity-legend"></div>
              </div>
              <div class="capacity-footnote" id="capacity-footnote"></div>
            </article>
          </div>

          <div class="interpretation-note">
            <span class="note-icon" aria-hidden="true">i</span>
            <p><strong>Interpretation:</strong> Predicted probabilities summarize model estimates, not observed outcomes or expected losses. Portfolio patterns are descriptive and do not show that an intervention will change outcomes.</p>
          </div>
        </section>

        <section class="explore-view" id="explore-view" aria-labelledby="explore-title" hidden>
          <div class="section-heading explore-heading">
            <div>
              <p class="eyebrow">COHORT EXPLORATION</p>
              <h2 id="explore-title">Explore portfolio</h2>
              <p class="section-description">Filter scored customers and compare descriptive groups.</p>
            </div>
            <span class="portfolio-count" id="explore-count">0 of 0 customers</span>
          </div>

          <section class="card filters-card" aria-labelledby="filters-title">
            <div class="card-heading filter-heading">
              <div>
                <h3 id="filters-title">Find a cohort</h3>
                <p>Every filter applies to the full scored portfolio. Counts below show the filtered denominator.</p>
              </div>
              <button class="text-button" id="reset-filters" type="button">Reset filters</button>
            </div>
            <div class="filter-grid">
              <label class="filter-control">
                <span>Customer ID</span>
                <input id="filter-customer-id" type="search" inputmode="numeric" placeholder="Search ID" />
              </label>
              <label class="filter-control">
                <span>Minimum predicted risk</span>
                <input id="filter-score-min" type="number" min="0" max="1" step="0.01" value="0" />
              </label>
              <label class="filter-control">
                <span>Maximum predicted risk</span>
                <input id="filter-score-max" type="number" min="0" max="1" step="0.01" value="1" />
              </label>
              <label class="filter-control">
                <span>Reference risk band</span>
                <select id="filter-risk-band">
                  <option value="">All bands</option>
                  <option>Lower</option><option>Moderate</option><option>Elevated</option><option>Highest</option>
                </select>
              </label>
              <label class="filter-control">
                <span>Review status</span>
                <select id="filter-review-status">
                  <option value="">All customers</option>
                  <option value="selected">Selected for review</option>
                  <option value="not-selected">Not selected</option>
                </select>
              </label>
              <label class="filter-control">
                <span>Filter by input field</span>
                <select id="filter-feature">
                  <option value="">No input filter</option>
                </select>
              </label>
              <div class="filter-control feature-value-control" id="feature-value-control" hidden></div>
            </div>
            <p class="filter-message" id="filter-message" role="status"></p>
          </section>

          <div class="explore-summary-grid">
            <article class="card distribution-card">
              <div class="card-heading">
                <div><h3>Predicted-risk distribution</h3><p>Fixed 10 percentage-point bins; shares use the filtered cohort.</p></div>
              </div>
              <div class="score-distribution" id="score-distribution" role="list" aria-label="Predicted-risk distribution"></div>
            </article>
            <article class="card group-card">
              <div class="card-heading group-heading">
                <div><h3>Compare groups</h3><p>Descriptive summaries for the filtered cohort.</p></div>
                <label class="group-field"><span>Group by</span><select id="group-by-field"></select></label>
              </div>
              <div class="table-scroll">
                <table class="group-table">
                  <thead><tr><th scope="col">Group</th><th scope="col">Customers</th><th scope="col">Share</th><th scope="col">Mean risk</th><th scope="col">Selected</th></tr></thead>
                  <tbody id="group-summary-body"></tbody>
                </table>
              </div>
              <p class="table-note" id="group-table-note">For numeric fields, groups use quartile boundaries from the full portfolio.</p>
            </article>
          </div>

          <section class="card customer-results-card" aria-labelledby="customer-results-title">
            <div class="card-heading">
              <div><h3 id="customer-results-title">Matching customers</h3><p>Customers are ordered from highest to lowest predicted risk. The table shows a page at a time.</p></div>
              <span class="portfolio-count" id="page-count">0–0 of 0</span>
            </div>
            <div class="table-scroll">
              <table class="customer-table">
                <thead><tr><th scope="col">Rank</th><th scope="col">Customer ID</th><th scope="col">Predicted risk</th><th scope="col">Risk band</th><th scope="col">Review status</th></tr></thead>
                <tbody id="customer-results-body"></tbody>
              </table>
            </div>
            <div class="pagination-controls">
              <span id="page-status">Page 1 of 1</span>
              <div><button class="secondary-button" id="previous-page" type="button" disabled>Previous</button><button class="secondary-button" id="next-page" type="button" disabled>Next</button></div>
            </div>
          </section>

          <div class="interpretation-note">
            <span class="note-icon" aria-hidden="true">i</span>
            <p><strong>Interpretation:</strong> Filtered groups describe this uploaded portfolio. They do not establish causes, treatment effects, or fairness conclusions. Encoded input values are shown as supplied; category codes are not given inferred labels.</p>
          </div>
        </section>

        <section class="queue-view" id="queue-view" aria-labelledby="queue-title" hidden>
          <div class="section-heading queue-heading">
            <div>
              <p class="eyebrow">CAPACITY DECISION</p>
              <h2 id="queue-title">Review queue</h2>
              <p class="section-description">How your review capacity shaped the ranked customer list.</p>
            </div>
            <span class="portfolio-count" id="queue-population-count"></span>
          </div>

          <div class="queue-metric-grid" id="queue-metric-grid" aria-label="Queue capacity summary"></div>

          <div class="queue-explanation-grid">
            <article class="card queue-policy-card">
              <div class="card-heading">
                <div><h3>How selection works</h3><p>A consistent selection rule determines who enters the review list.</p></div>
                <span class="chart-mark capacity-mark" aria-hidden="true">↕</span>
              </div>
              <ol class="queue-policy-list">
                <li><strong>Rank by predicted risk.</strong><span>Customers are ordered from highest to lowest predicted default probability. Equal scores receive the same rank, so later ranks account for all customers ahead.</span></li>
                <li><strong>Keep equal scores together.</strong><span>Customers with the same risk score enter the review list together when the group fits within your capacity.</span></li>
                <li><strong>Stop at a boundary tie.</strong><span>If the next tied group would exceed the remaining target, that whole group and all lower-scoring groups are left out.</span></li>
              </ol>
              <div class="queue-refresh-note"><strong>To change capacity:</strong> edit Review capacity above and click Run analysis. This queue shows the result from the last completed run.</div>
            </article>

            <article class="card queue-outcomes-card">
              <div class="card-heading">
                <div><h3>Why customers were selected or left out</h3><p>These totals explain why customers entered the review list or remained outside it.</p></div>
              </div>
              <div class="table-scroll">
                <table class="group-table">
                  <thead><tr><th scope="col">Queue outcome</th><th scope="col">Customers</th></tr></thead>
                  <tbody id="queue-reasons-body"></tbody>
                </table>
              </div>
              <p class="table-note">Unused capacity can occur when a full tied score group cannot fit. The queue never splits that group or exceeds its target.</p>
            </article>
          </div>

          <section class="card selected-queue-card" aria-labelledby="selected-queue-title">
            <div class="card-heading">
              <div><h3 id="selected-queue-title">Selected customers</h3><p>Customers are listed from highest to lowest predicted risk.</p></div>
              <span class="portfolio-count" id="queue-page-count">0–0 of 0</span>
            </div>
            <div class="table-scroll">
              <table class="customer-table">
                <thead><tr><th scope="col">Rank</th><th scope="col">Customer ID</th><th scope="col">Predicted risk</th><th scope="col">Selection reason</th></tr></thead>
                <tbody id="selected-queue-body"></tbody>
              </table>
            </div>
            <div class="pagination-controls">
              <span id="queue-page-status">Page 1 of 1</span>
              <div><button class="secondary-button" id="queue-previous-page" type="button" disabled>Previous</button><button class="secondary-button" id="queue-next-page" type="button" disabled>Next</button></div>
            </div>
          </section>

          <div class="interpretation-note">
            <span class="note-icon" aria-hidden="true">i</span>
            <p><strong>Interpretation:</strong> This view explains a model-ranked review policy under the requested capacity. It does not recommend an intervention or estimate the effect of reviewing a customer.</p>
          </div>
        </section>

        <section class="empty-state" id="empty-state" aria-labelledby="empty-title">
          <div class="empty-illustration" aria-hidden="true">
            <span class="illustration-card card-one"></span>
            <span class="illustration-card card-two"></span>
            <span class="illustration-chart"><i></i><i></i><i></i><i></i></span>
          </div>
          <h2 id="empty-title">Your portfolio overview will appear here</h2>
          <p>Upload a customer file above to see the portfolio summary and review-capacity breakdown.</p>
        </section>

        <footer class="page-footer">
          <span>Credit risk review · Analyst workspace</span>
          <span>Model estimates support review prioritization only</span>
        </footer>
      </main>
    </div>
  </body>
</html>

```

### `src/propensity_prediction/dashboard/static/styles.css`

```css
:root {
  color-scheme: light;
  --canvas: #f4f7f4;
  --surface: #ffffff;
  --surface-muted: #f8faf8;
  --ink: #263a36;
  --ink-strong: #1a302b;
  --ink-muted: #62746f;
  --ink-soft: #7c8b86;
  --line: #e1e9e4;
  --line-strong: #d1ded7;
  --teal: #287c70;
  --teal-dark: #1f685e;
  --teal-soft: #e6f1ed;
  --blue: #6487a2;
  --blue-soft: #eaf0f5;
  --amber: #aa7740;
  --amber-soft: #f5eee3;
  --rose: #a45f62;
  --rose-soft: #f5e9e8;
  --shadow: 0 10px 30px rgb(36 63 53 / 5%);
  --radius: 18px;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
}

* { box-sizing: border-box; }

body {
  min-width: 320px;
  min-height: 100vh;
  margin: 0;
  background: var(--canvas);
  color: var(--ink);
  font-size: 14px;
  line-height: 1.55;
}

button, input { font: inherit; }
button { color: inherit; }
a { color: inherit; }
[hidden] { display: none !important; }

:focus-visible {
  outline: 3px solid #75a99d;
  outline-offset: 3px;
}

.app-shell { min-height: 100vh; }

.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 5;
  display: flex;
  width: 248px;
  flex-direction: column;
  padding: 26px 18px 20px;
  border-right: 1px solid var(--line);
  background: #fbfcfa;
}

.brand {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 2px 8px 28px;
  text-decoration: none;
}

.brand-mark {
  display: grid;
  width: 39px;
  height: 39px;
  place-items: center;
  border-radius: 13px;
  background: var(--teal-dark);
  color: #fff;
  font-family: "Manrope", sans-serif;
  font-size: 19px;
  font-weight: 800;
}

.brand-copy { display: grid; line-height: 1.25; }
.brand-copy strong { color: var(--ink-strong); font-size: 15px; font-weight: 700; }
.brand-copy span { margin-top: 3px; color: var(--ink-muted); font-size: 11px; }

.nav-label, .eyebrow {
  color: var(--ink-soft);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .12em;
}

.nav-label { margin: 0 10px 10px; }
.primary-nav { display: grid; gap: 5px; }

.nav-link {
  display: flex;
  min-height: 44px;
  align-items: center;
  gap: 11px;
  padding: 0 11px;
  border-radius: 10px;
  color: #566963;
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
}

.nav-link.is-active {
  background: var(--teal-soft);
  color: #245f55;
  font-weight: 700;
}

.nav-icon {
  display: inline-grid;
  width: 22px;
  place-items: center;
  color: currentColor;
  font-size: 18px;
  line-height: 1;
}

.nav-link.is-disabled { color: #77857f; cursor: not-allowed; }
.nav-link:not(.is-disabled):hover { background: #f0f5f1; color: var(--teal-dark); }
.nav-soon {
  margin-left: auto;
  color: #77857f;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: .08em;
}

.sidebar-bottom { display: grid; gap: 17px; margin-top: auto; }
.sidebar-note, .interpretation-note {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  border: 1px solid #dfe9e3;
  background: #f1f6f2;
  color: #475d55;
}

.sidebar-note { padding: 12px 11px; border-radius: 12px; }
.sidebar-note p, .interpretation-note p { margin: 0; font-size: 11px; line-height: 1.55; }
.note-icon {
  display: inline-grid;
  width: 18px;
  height: 18px;
  flex: 0 0 auto;
  place-items: center;
  border: 1px solid #9bb5a9;
  border-radius: 50%;
  color: #3f6d5d;
  font-size: 11px;
  font-weight: 700;
}

.service-status { display: flex; align-items: center; gap: 8px; padding: 0 7px; color: var(--ink-muted); font-size: 11px; }
.status-dot, .meta-dot { width: 8px; height: 8px; border-radius: 50%; background: #b3c0b9; }
.service-status.is-ready .status-dot { background: #38876d; box-shadow: 0 0 0 3px #e2f0e8; }
.service-status.is-error .status-dot { background: #a45f62; box-shadow: 0 0 0 3px #f5e9e8; }

.main-content { max-width: 1540px; min-height: 100vh; margin-left: 248px; padding: 0 44px 24px; }
.topbar { display: flex; height: 72px; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--line); }
.breadcrumb { color: var(--ink-muted); font-size: 12px; }
.breadcrumb span { margin: 0 7px; color: #9aa8a2; }
.topbar-actions { display: flex; align-items: center; gap: 16px; }
.text-button { padding: 6px 2px; border: 0; background: transparent; color: #4c665e; cursor: pointer; font-size: 12px; font-weight: 600; }
.text-button:hover { color: var(--teal-dark); }
.avatar { display: grid; width: 31px; height: 31px; place-items: center; border: 1px solid #dce5df; border-radius: 50%; background: #e9f0eb; color: #426257; font-size: 10px; font-weight: 700; }

.page-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; padding: 31px 0 22px; }
.page-heading .eyebrow, .section-heading .eyebrow { margin: 0 0 6px; }
h1, h2, h3, p { margin-top: 0; }
h1, h2, h3 { color: var(--ink-strong); font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
h1 { margin-bottom: 6px; font-size: clamp(24px, 2.4vw, 32px); font-weight: 700; letter-spacing: -.04em; line-height: 1.2; }
.page-description { margin: 0; color: var(--ink-muted); font-size: 13px; }
.analysis-meta { display: inline-flex; align-items: center; gap: 8px; padding: 7px 11px; border: 1px solid var(--line); border-radius: 99px; background: var(--surface); color: #50665e; font-size: 11px; white-space: nowrap; }
.analysis-meta .meta-dot { background: #3c8a6f; }

.analysis-panel {
  display: grid;
  grid-template-columns: minmax(220px, .78fr) minmax(380px, 1.45fr);
  gap: 28px;
  padding: 22px 24px;
  border: 1px solid #dce7e0;
  border-radius: var(--radius);
  background: linear-gradient(116deg, #edf4ef, #f9fbf8 65%);
  box-shadow: var(--shadow);
}

.analysis-panel-copy { align-self: center; }
.step-badge { display: inline-block; margin-bottom: 9px; color: #4e7d6e; font-size: 9px; font-weight: 700; letter-spacing: .13em; }
.analysis-panel h2 { margin: 0 0 6px; font-size: 17px; letter-spacing: -.025em; }
.analysis-panel-copy p { max-width: 330px; margin: 0; color: var(--ink-muted); font-size: 12px; line-height: 1.6; }
.analysis-form { display: grid; align-content: center; gap: 12px; }
.file-drop { display: flex; min-height: 70px; align-items: center; gap: 12px; padding: 10px 12px; border: 1px dashed #aabeb2; border-radius: 12px; background: rgb(255 255 255 / 76%); cursor: pointer; }
.file-drop:hover, .file-drop:focus-within { border-color: var(--teal); background: #fff; }
.upload-icon { display: grid; width: 38px; height: 38px; flex: 0 0 auto; place-items: center; border-radius: 11px; background: #e7f1eb; color: #3d7461; font-size: 22px; font-weight: 500; }
.file-drop-copy { display: grid; min-width: 0; gap: 3px; }
.file-drop-copy strong { overflow: hidden; color: var(--ink-strong); font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.file-drop-copy span { color: var(--ink-muted); font-size: 10px; }
.browse-button { margin-left: auto; padding: 7px 10px; border: 1px solid var(--line-strong); border-radius: 8px; background: #fff; color: #395b50; font-size: 10px; font-weight: 700; white-space: nowrap; }
.visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; clip-path: inset(50%); }
.form-actions { display: flex; align-items: flex-end; justify-content: space-between; gap: 14px; }
.capacity-field { display: grid; gap: 5px; color: #536760; font-size: 10px; font-weight: 600; }
.capacity-input-wrap { display: flex; height: 36px; align-items: center; gap: 8px; padding: 0 9px; border: 1px solid var(--line-strong); border-radius: 8px; background: #fff; color: var(--ink-muted); font-size: 10px; }
.capacity-input-wrap input { width: 78px; border: 0; outline: none; background: transparent; color: var(--ink-strong); font-size: 12px; font-weight: 600; }
.capacity-input-wrap input:focus-visible { outline: 2px solid #75a99d; outline-offset: 2px; }
.primary-button { display: inline-flex; min-height: 37px; align-items: center; justify-content: center; gap: 15px; padding: 0 15px; border: 1px solid var(--teal-dark); border-radius: 8px; background: var(--teal-dark); color: #fff; cursor: pointer; font-size: 11px; font-weight: 700; transition: background .15s ease, transform .15s ease; }
.primary-button:hover { transform: translateY(-1px); background: #19584f; }
.primary-button:disabled { cursor: wait; opacity: .72; transform: none; }
.form-message { margin: 0; color: #8b4448; font-size: 11px; line-height: 1.5; }
.form-message.is-success { color: #34735d; }
.capacity-refresh-note { margin: -4px 0 0; color: var(--ink-soft); font-size: 9px; line-height: 1.45; }

.results-section { padding-top: 31px; }
.section-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 18px; margin-bottom: 15px; }
.section-heading h2 { margin: 0 0 5px; font-size: 19px; letter-spacing: -.03em; }
.section-description { margin: 0; color: var(--ink-muted); font-size: 11px; }
.portfolio-count { padding: 6px 10px; border: 1px solid var(--line); border-radius: 99px; background: #fff; color: #587069; font-size: 10px; font-weight: 600; white-space: nowrap; }
.metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 13px; margin-bottom: 15px; }
.metric-card { min-height: 112px; padding: 16px 17px; border: 1px solid var(--line); border-radius: 14px; background: var(--surface); box-shadow: 0 5px 16px rgb(36 63 53 / 3%); }
.metric-card-top { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.metric-label { color: var(--ink-muted); font-size: 10px; font-weight: 600; }
.metric-icon { display: grid; width: 27px; height: 27px; place-items: center; border-radius: 9px; background: var(--teal-soft); color: #397366; font-size: 13px; }
.metric-card:nth-child(2) .metric-icon { background: var(--blue-soft); color: #597b96; }
.metric-card:nth-child(3) .metric-icon { background: var(--amber-soft); color: #8d6639; }
.metric-card:nth-child(4) .metric-icon { background: var(--rose-soft); color: #92575a; }
.metric-value { display: block; margin-top: 9px; color: var(--ink-strong); font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; font-size: 25px; font-weight: 700; letter-spacing: -.04em; line-height: 1.15; }
.metric-help { display: block; margin-top: 5px; color: var(--ink-soft); font-size: 9px; }

.insight-grid { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(300px, .85fr); gap: 15px; }
.card { min-width: 0; padding: 19px 20px 17px; border: 1px solid var(--line); border-radius: 15px; background: var(--surface); box-shadow: 0 5px 16px rgb(36 63 53 / 3%); }
.card-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 15px; margin-bottom: 18px; }
.card-heading h3 { margin: 0 0 4px; font-size: 14px; letter-spacing: -.02em; }
.card-heading p { margin: 0; color: var(--ink-muted); font-size: 10px; }
.chart-mark { display: grid; width: 30px; height: 30px; flex: 0 0 auto; place-items: center; border-radius: 9px; background: #edf4ef; color: #547c69; font-size: 17px; }
.capacity-mark { background: #edf1f5; color: #617b91; }
.band-list { display: grid; gap: 14px; }
.band-row { display: grid; grid-template-columns: 77px minmax(70px, 1fr) 58px; align-items: center; gap: 12px; }
.band-label { color: #4b6058; font-size: 10px; font-weight: 600; }
.band-track { height: 10px; overflow: hidden; border-radius: 99px; background: #edf1ee; }
.band-fill { display: block; height: 100%; min-width: 0; border-radius: inherit; transition: width .45s ease; }
.band-row[data-band="Lower"] .band-fill { background: #76a994; }
.band-row[data-band="Moderate"] .band-fill { background: #7894a8; }
.band-row[data-band="Elevated"] .band-fill { background: #c49a61; }
.band-row[data-band="Highest"] .band-fill { background: #b97778; }
.band-value { color: #3f554c; font-size: 10px; font-variant-numeric: tabular-nums; text-align: right; }
.band-value strong { color: var(--ink-strong); font-weight: 700; }
.band-value span { color: var(--ink-soft); }
.chart-note { margin-top: 17px; padding-top: 12px; border-top: 1px solid #edf1ee; color: var(--ink-muted); }
.chart-note summary { width: fit-content; color: #466e61; cursor: pointer; font-size: 10px; font-weight: 600; }
.chart-note p { max-width: 640px; margin: 9px 0 0; font-size: 10px; line-height: 1.6; }

.capacity-visual { display: flex; min-height: 150px; align-items: center; justify-content: center; gap: clamp(18px, 4vw, 47px); }
.capacity-ring { display: grid; width: 142px; height: 142px; flex: 0 0 auto; place-items: center; border-radius: 50%; background: conic-gradient(#438675 0deg, #438675 0deg, #e8efeb 0deg 360deg); }
.ring-center { display: grid; width: 110px; height: 110px; align-content: center; justify-items: center; border-radius: 50%; background: #fff; }
.ring-center strong { color: var(--ink-strong); font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; font-size: 24px; letter-spacing: -.04em; }
.ring-center span { color: var(--ink-muted); font-size: 9px; }
.capacity-legend { display: grid; gap: 13px; }
.legend-item { display: grid; grid-template-columns: 9px auto; align-items: start; gap: 8px; color: var(--ink-muted); font-size: 10px; }
.legend-dot { width: 8px; height: 8px; margin-top: 4px; border-radius: 50%; background: #438675; }
.legend-item:nth-child(2) .legend-dot { background: #9bb9aa; }
.legend-item:nth-child(3) .legend-dot { background: #d5ded8; }
.legend-copy { display: grid; gap: 1px; }
.legend-copy strong { color: #42574f; font-size: 11px; font-weight: 700; }
.legend-copy span { color: var(--ink-soft); font-size: 9px; }
.capacity-footnote { min-height: 28px; margin-top: 9px; padding-top: 10px; border-top: 1px solid #edf1ee; color: var(--ink-muted); font-size: 9px; line-height: 1.5; }

.interpretation-note { align-items: flex-start; margin-top: 15px; padding: 11px 13px; border-radius: 11px; }
.interpretation-note p { font-size: 10px; }
.interpretation-note strong { color: #38584d; }

.explore-view { padding-top: 31px; }
.explore-heading { margin-bottom: 15px; }
.filters-card { margin-bottom: 15px; }
.filter-heading { align-items: center; margin-bottom: 15px; }
.filter-heading .text-button { flex: 0 0 auto; }
.filter-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.filter-control { display: grid; min-width: 0; gap: 5px; color: #536760; font-size: 10px; font-weight: 600; }
.filter-control input, .filter-control select, .group-field select {
  width: 100%; min-width: 0; height: 36px; padding: 0 9px; border: 1px solid var(--line-strong);
  border-radius: 8px; background: #fff; color: var(--ink-strong); font-size: 11px;
}
.feature-value-control { align-content: end; }
.feature-value-control[hidden] { display: none; }
.feature-value-control > span { color: #536760; font-size: 10px; font-weight: 600; }
.feature-range-inputs { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.filter-message { min-height: 16px; margin: 8px 0 0; color: #8b4448; font-size: 10px; }
.explore-summary-grid { display: grid; grid-template-columns: minmax(0, .85fr) minmax(0, 1.15fr); gap: 15px; margin-bottom: 15px; }
.distribution-card, .group-card { min-width: 0; }
.score-distribution { display: grid; gap: 8px; }
.distribution-row { display: grid; grid-template-columns: 48px minmax(40px, 1fr) 77px; align-items: center; gap: 9px; }
.distribution-label { color: #4b6058; font-size: 9px; font-variant-numeric: tabular-nums; }
.distribution-track { display: block; height: 9px; overflow: hidden; border-radius: 99px; background: #edf1ee; }
.distribution-fill { display: block; height: 100%; border-radius: inherit; background: #6b9b87; transition: width .25s ease; }
.distribution-value { color: var(--ink-muted); font-size: 9px; font-variant-numeric: tabular-nums; text-align: right; white-space: nowrap; }
.group-heading { align-items: center; }
.group-field { display: grid; min-width: 110px; gap: 3px; color: var(--ink-muted); font-size: 9px; }
.group-field select { height: 31px; }
.table-scroll { width: 100%; overflow: auto; }
.group-table, .customer-table { width: 100%; border-collapse: collapse; font-size: 10px; text-align: left; }
.group-table th, .customer-table th { padding: 9px 8px; border-bottom: 1px solid var(--line-strong); color: var(--ink-muted); font-size: 9px; font-weight: 700; white-space: nowrap; }
.group-table td, .customer-table td { padding: 9px 8px; border-bottom: 1px solid #edf1ee; color: #40564d; font-variant-numeric: tabular-nums; white-space: nowrap; }
.group-table tbody tr:last-child td, .customer-table tbody tr:last-child td { border-bottom: 0; }
.table-note { margin: 10px 0 0; color: var(--ink-soft); font-size: 9px; line-height: 1.5; }
.customer-results-card { margin-bottom: 15px; }
.customer-results-card .card-heading { align-items: center; margin-bottom: 9px; }
.pagination-controls { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-top: 12px; padding-top: 12px; border-top: 1px solid #edf1ee; color: var(--ink-muted); font-size: 10px; }
.pagination-controls > div { display: flex; gap: 7px; }
.secondary-button { min-height: 30px; padding: 0 10px; border: 1px solid var(--line-strong); border-radius: 7px; background: #fff; color: #456258; cursor: pointer; font-size: 10px; font-weight: 600; }
.secondary-button:disabled { cursor: default; color: #9aa8a2; background: #f7f9f7; }

.queue-view { padding-top: 31px; }
.queue-heading { margin-bottom: 15px; }
.queue-metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 13px; margin-bottom: 15px; }
.queue-metric-card { display: grid; min-height: 105px; align-content: start; gap: 2px; }
.queue-metric-card .metric-value { margin-top: 6px; }
.queue-explanation-grid { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(300px, .9fr); gap: 15px; margin-bottom: 15px; }
.queue-policy-list { display: grid; gap: 14px; margin: 0; padding: 0; list-style: none; counter-reset: queue-step; }
.queue-policy-list li { display: grid; grid-template-columns: 25px minmax(0, 1fr); column-gap: 10px; counter-increment: queue-step; }
.queue-policy-list li::before { content: counter(queue-step); display: grid; width: 24px; height: 24px; grid-row: span 2; place-items: center; border-radius: 8px; background: var(--teal-soft); color: #397366; font-size: 10px; font-weight: 700; }
.queue-policy-list strong { color: #38584d; font-size: 11px; }
.queue-policy-list span { margin-top: 2px; color: var(--ink-muted); font-size: 10px; line-height: 1.5; }
.queue-refresh-note { margin-top: 18px; padding: 11px 12px; border: 1px solid #e2eae4; border-radius: 9px; background: var(--surface-muted); color: var(--ink-muted); font-size: 10px; line-height: 1.5; }
.queue-refresh-note strong { color: #3c6558; }
.queue-outcomes-card .group-table td:first-child { min-width: 180px; white-space: normal; line-height: 1.45; }
.selected-queue-card { margin-bottom: 15px; }
.selected-queue-card .customer-table td:last-child { min-width: 300px; white-space: normal; line-height: 1.45; }

.empty-state { display: grid; justify-items: center; padding: 34px 20px 30px; color: var(--ink-muted); text-align: center; }
.empty-illustration { position: relative; width: 126px; height: 91px; margin-bottom: 13px; }
.illustration-card { position: absolute; width: 80px; height: 56px; border: 1px solid #dce7e0; border-radius: 10px; background: #fff; box-shadow: var(--shadow); }
.card-one { top: 7px; left: 16px; transform: rotate(-8deg); }
.card-two { top: 5px; left: 35px; transform: rotate(7deg); }
.illustration-chart { position: absolute; right: 9px; bottom: 8px; display: flex; width: 57px; height: 41px; align-items: flex-end; gap: 5px; padding: 6px; border: 1px solid #dce7e0; border-radius: 9px; background: #f8fbf8; }
.illustration-chart i { flex: 1; border-radius: 3px 3px 1px 1px; background: #8bb7a4; }
.illustration-chart i:nth-child(1) { height: 36%; }
.illustration-chart i:nth-child(2) { height: 58%; background: #9bb1bb; }
.illustration-chart i:nth-child(3) { height: 45%; background: #cfb082; }
.illustration-chart i:nth-child(4) { height: 78%; background: #c18787; }
.empty-state h2 { margin: 0 0 5px; font-size: 15px; letter-spacing: -.02em; }
.empty-state p { max-width: 410px; margin: 0; color: var(--ink-muted); font-size: 11px; }
.page-footer { display: flex; justify-content: space-between; gap: 15px; margin-top: 12px; padding: 14px 0 3px; border-top: 1px solid var(--line); color: var(--ink-soft); font-size: 9px; }

@media (max-width: 1120px) {
  .main-content { padding-right: 28px; padding-left: 28px; }
  .sidebar { width: 220px; }
  .main-content { margin-left: 220px; }
  .analysis-panel { grid-template-columns: 1fr; gap: 16px; }
  .analysis-panel-copy p { max-width: 520px; }
  .filter-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .queue-explanation-grid { grid-template-columns: 1fr; }
}

@media (max-width: 820px) {
  .sidebar { position: static; width: auto; height: auto; padding: 13px 18px; border-right: 0; border-bottom: 1px solid var(--line); }
  .brand { padding: 0; }
  .nav-label, .sidebar-bottom { display: none; }
  .primary-nav { display: flex; overflow-x: auto; gap: 4px; margin-top: 13px; }
  .nav-link { min-height: 38px; flex: 0 0 auto; padding: 0 10px; font-size: 11px; }
  .nav-icon { width: 16px; font-size: 15px; }
  .nav-soon { display: none; }
  .main-content { margin-left: 0; padding: 0 20px 20px; }
  .topbar { height: 55px; }
  .insight-grid { grid-template-columns: 1fr; }
  .explore-summary-grid { grid-template-columns: 1fr; }
  .queue-metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; }
}

@media (max-width: 560px) {
  .main-content { padding-right: 14px; padding-left: 14px; }
  .page-heading { align-items: flex-start; flex-direction: column; gap: 10px; padding: 23px 0 17px; }
  .analysis-panel { padding: 17px 14px; }
  .file-drop { gap: 9px; }
  .browse-button { padding: 7px; font-size: 9px; }
  .file-drop-copy span { max-width: 180px; font-size: 9px; }
  .form-actions { align-items: stretch; flex-direction: column; }
  .capacity-field { align-items: flex-start; }
  .primary-button { width: 100%; }
  .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; }
  .metric-card { min-height: 104px; padding: 13px; }
  .metric-value { font-size: 22px; }
  .card { padding: 16px 14px; }
  .band-row { grid-template-columns: 68px minmax(45px, 1fr) 52px; gap: 8px; }
  .capacity-visual { gap: 17px; }
  .capacity-ring { width: 120px; height: 120px; }
  .ring-center { width: 94px; height: 94px; }
  .ring-center strong { font-size: 21px; }
  .section-heading { align-items: flex-start; flex-direction: column; }
  .filter-grid { grid-template-columns: 1fr 1fr; }
  .group-heading { align-items: flex-start; flex-direction: column; }
  .page-footer { flex-direction: column; gap: 4px; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; }
}

```

### `src/propensity_prediction/dashboard/static/app.js`

```javascript
"use strict";

const INTEGER_FIELDS = new Set([
  "ID", "SEX", "EDUCATION", "MARRIAGE",
  "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
]);
const NON_NEGATIVE_FIELDS = new Set([
  "LIMIT_BAL", "PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6",
]);
const INTEGER_RANGES = {
  SEX: [1, 2],
  EDUCATION: [0, 4],
  MARRIAGE: [0, 3],
};
const CATEGORICAL_FIELDS = new Set([
  "SEX", "EDUCATION", "MARRIAGE", "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
]);
const PAGE_SIZE = 50;

const elements = {
  form: document.querySelector("#analysis-form"),
  file: document.querySelector("#portfolio-file"),
  fileName: document.querySelector("#file-name"),
  fileHint: document.querySelector("#file-hint"),
  capacity: document.querySelector("#review-capacity"),
  runButton: document.querySelector("#run-analysis"),
  formMessage: document.querySelector("#form-message"),
  status: document.querySelector("#service-status"),
  healthCheck: document.querySelector("#health-check"),
  emptyState: document.querySelector("#empty-state"),
  results: document.querySelector("#results-section"),
  metrics: document.querySelector("#metric-grid"),
  riskBands: document.querySelector("#risk-band-chart"),
  riskReference: document.querySelector("#risk-band-reference"),
  capacityRing: document.querySelector("#capacity-ring"),
  capacityPercent: document.querySelector("#capacity-percent"),
  capacityLegend: document.querySelector("#capacity-legend"),
  capacityFootnote: document.querySelector("#capacity-footnote"),
  portfolioCount: document.querySelector("#portfolio-count"),
  analysisMeta: document.querySelector("#analysis-meta"),
  analysisMetaText: document.querySelector("#analysis-meta-text"),
  exploreView: document.querySelector("#explore-view"),
  queueView: document.querySelector("#queue-view"),
  viewLinks: [...document.querySelectorAll("[data-view]")],
  exploreCount: document.querySelector("#explore-count"),
  customerIdFilter: document.querySelector("#filter-customer-id"),
  scoreMinFilter: document.querySelector("#filter-score-min"),
  scoreMaxFilter: document.querySelector("#filter-score-max"),
  riskBandFilter: document.querySelector("#filter-risk-band"),
  reviewStatusFilter: document.querySelector("#filter-review-status"),
  featureFilter: document.querySelector("#filter-feature"),
  featureValueControl: document.querySelector("#feature-value-control"),
  resetFilters: document.querySelector("#reset-filters"),
  filterMessage: document.querySelector("#filter-message"),
  groupByField: document.querySelector("#group-by-field"),
  scoreDistribution: document.querySelector("#score-distribution"),
  groupSummaryBody: document.querySelector("#group-summary-body"),
  groupTableNote: document.querySelector("#group-table-note"),
  customerResultsBody: document.querySelector("#customer-results-body"),
  pageCount: document.querySelector("#page-count"),
  pageStatus: document.querySelector("#page-status"),
  previousPage: document.querySelector("#previous-page"),
  nextPage: document.querySelector("#next-page"),
  queuePopulationCount: document.querySelector("#queue-population-count"),
  queueMetricGrid: document.querySelector("#queue-metric-grid"),
  queueReasonsBody: document.querySelector("#queue-reasons-body"),
  selectedQueueBody: document.querySelector("#selected-queue-body"),
  queuePageCount: document.querySelector("#queue-page-count"),
  queuePageStatus: document.querySelector("#queue-page-status"),
  queuePreviousPage: document.querySelector("#queue-previous-page"),
  queueNextPage: document.querySelector("#queue-next-page"),
};

let dashboardConfig = null;
let selectedFile = null;
let currentPortfolio = [];
let currentResult = null;
let filteredPortfolio = [];
let currentPage = 0;
let queuePage = 0;
let activeView = "overview";
const quartileBoundaryCache = new Map();

const percentFormatter = new Intl.NumberFormat(undefined, {
  style: "percent",
  maximumFractionDigits: 1,
});
const numberFormatter = new Intl.NumberFormat(undefined, {
  maximumFractionDigits: 0,
});

function showMessage(message, kind = "error") {
  elements.formMessage.textContent = message;
  elements.formMessage.hidden = false;
  elements.formMessage.classList.toggle("is-success", kind === "success");
}

function clearMessage() {
  elements.formMessage.textContent = "";
  elements.formMessage.hidden = true;
  elements.formMessage.classList.remove("is-success");
}

function setServiceStatus(ready, message) {
  elements.status.classList.toggle("is-ready", ready);
  elements.status.classList.toggle("is-error", !ready);
  elements.status.lastChild.textContent = ` ${message}`;
}

function parseCsv(text) {
  const source = text.replace(/^\uFEFF/, "");
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;
  let afterQuote = false;

  for (let index = 0; index < source.length; index += 1) {
    const character = source[index];
    const next = source[index + 1];

    if (inQuotes) {
      if (character === '"' && next === '"') {
        field += '"';
        index += 1;
      } else if (character === '"') {
        inQuotes = false;
        afterQuote = true;
      } else {
        field += character;
      }
      continue;
    }

    if (afterQuote) {
      if (character === ",") {
        row.push(field);
        field = "";
        afterQuote = false;
      } else if (character === "\n" || character === "\r") {
        row.push(field);
        appendCsvRow(rows, row);
        row = [];
        field = "";
        afterQuote = false;
        if (character === "\r" && next === "\n") index += 1;
      } else if (character === " " || character === "\t") {
        // Ignore whitespace between a closing quote and its delimiter.
      } else {
        throw new Error("The CSV has invalid characters after a quoted value.");
      }
      continue;
    }

    if (character === '"') {
      if (field.length > 0) {
        throw new Error("The CSV contains a quote inside an unquoted value.");
      }
      inQuotes = true;
    } else if (character === ",") {
      row.push(field);
      field = "";
    } else if (character === "\n" || character === "\r") {
      row.push(field);
      appendCsvRow(rows, row);
      row = [];
      field = "";
      if (character === "\r" && next === "\n") index += 1;
    } else {
      field += character;
    }
  }

  if (inQuotes) throw new Error("The CSV contains an unclosed quoted value.");
  if (field.length > 0 || row.length > 0 || afterQuote) {
    row.push(field);
    appendCsvRow(rows, row);
  }
  return rows;
}

function appendCsvRow(rows, row) {
  if (row.length === 1 && row[0] === "") return;
  rows.push(row);
}

function parseNumeric(value, column, csvRowNumber) {
  const trimmed = value.trim();
  const decimalPattern = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/;
  if (!decimalPattern.test(trimmed)) {
    throw new Error(`${column} must contain numeric values. Check CSV row ${csvRowNumber}.`);
  }
  const number = Number(trimmed);
  if (!Number.isFinite(number)) {
    throw new Error(`${column} must contain finite numeric values. Check CSV row ${csvRowNumber}.`);
  }
  if (INTEGER_FIELDS.has(column) && !Number.isInteger(number)) {
    throw new Error(`${column} must contain integer values. Check CSV row ${csvRowNumber}.`);
  }
  if (column === "ID" && !Number.isSafeInteger(number)) {
    throw new Error(`ID must be a safely representable integer. Check CSV row ${csvRowNumber}.`);
  }
  if (NON_NEGATIVE_FIELDS.has(column) && number < 0) {
    throw new Error(`${column} must be non-negative. Check CSV row ${csvRowNumber}.`);
  }
  if (Object.hasOwn(INTEGER_RANGES, column)) {
    const [minimum, maximum] = INTEGER_RANGES[column];
    if (number < minimum || number > maximum) {
      throw new Error(`${column} must use values from ${minimum} through ${maximum}. Check CSV row ${csvRowNumber}.`);
    }
  }
  return number;
}

function validateCsvRows(rows) {
  if (!rows.length) throw new Error("The CSV is empty.");
  const [headers, ...dataRows] = rows;
  if (!headers.length || headers.every((header) => header === "")) {
    throw new Error("The CSV must include a header row.");
  }
  if (new Set(headers).size !== headers.length) {
    throw new Error("The CSV contains duplicate column names.");
  }
  if (headers.includes("DEFAULT")) {
    throw new Error("DEFAULT is a historical outcome, not an input for prediction. Upload a prediction-time file without this column.");
  }

  const required = dashboardConfig.required_columns;
  const missing = required.filter((column) => !headers.includes(column));
  const extra = headers.filter((column) => !required.includes(column));
  if (missing.length || extra.length) {
    const problems = [];
    if (missing.length) problems.push(`Missing required columns: ${missing.join(", ")}.`);
    if (extra.length) problems.push(`Unrecognized columns: ${extra.join(", ")}.`);
    throw new Error(problems.join(" "));
  }
  if (!dataRows.length) throw new Error("The CSV must contain at least one customer row.");
  if (dataRows.length > dashboardConfig.max_customer_rows) {
    throw new Error(`The CSV contains ${numberFormatter.format(dataRows.length)} customer rows; the maximum is ${numberFormatter.format(dashboardConfig.max_customer_rows)}. Split the portfolio into smaller files.`);
  }

  const seenIds = new Set();
  return dataRows.map((values, rowIndex) => {
    const csvRowNumber = rowIndex + 2;
    if (values.length !== headers.length) {
      throw new Error(`CSV row ${csvRowNumber} has ${values.length} values; expected ${headers.length}.`);
    }
    const sourceRow = Object.fromEntries(headers.map((header, index) => [header, values[index]]));
    const customer = {};
    for (const column of required) {
      const value = sourceRow[column];
      if (value === undefined || value.trim() === "") {
        throw new Error(`${column} cannot be blank. Check CSV row ${csvRowNumber}.`);
      }
      customer[column] = parseNumeric(value, column, csvRowNumber);
    }
    if (seenIds.has(customer.ID)) {
      throw new Error(`ID values must be unique. Duplicate ID ${customer.ID} appears in CSV row ${csvRowNumber}.`);
    }
    seenIds.add(customer.ID);
    return customer;
  });
}

function formatCount(value) {
  return numberFormatter.format(value);
}

function formatPercent(value) {
  return percentFormatter.format(value);
}

function renderMetricCards(result) {
  const capacity = result.capacity;
  const summary = result.portfolio_summary.probability_summary;
  const metrics = [
    { label: "Customers scored", value: formatCount(result.population_count), help: "Full uploaded portfolio", icon: "▦" },
    { label: "Mean predicted risk", value: formatPercent(summary.mean), help: "Average model estimate", icon: "⌁" },
    { label: "Selected for review", value: formatCount(capacity.selected_count), help: "Under the supplied capacity", icon: "✓" },
    { label: "Unused capacity", value: formatCount(capacity.unused_capacity), help: "After tie-aware selection", icon: "↗" },
  ];

  elements.metrics.replaceChildren(...metrics.map((metric) => {
    const card = document.createElement("article");
    card.className = "metric-card";
    card.innerHTML = `
      <div class="metric-card-top">
        <span class="metric-label">${metric.label}</span>
        <span class="metric-icon" aria-hidden="true">${metric.icon}</span>
      </div>
      <strong class="metric-value">${metric.value}</strong>
      <span class="metric-help">${metric.help}</span>
    `;
    return card;
  }));
}

function renderRiskBands(summary) {
  const bands = summary.risk_bands;
  elements.riskBands.replaceChildren(...bands.map((band) => {
    const row = document.createElement("div");
    row.className = "band-row";
    row.dataset.band = band.label;
    row.setAttribute("role", "listitem");

    const label = document.createElement("span");
    label.className = "band-label";
    label.textContent = band.label;

    const track = document.createElement("span");
    track.className = "band-track";
    track.setAttribute("aria-hidden", "true");
    const fill = document.createElement("span");
    fill.className = "band-fill";
    fill.style.width = `${Math.max(0, Math.min(1, band.portfolio_share)) * 100}%`;
    track.append(fill);

    const value = document.createElement("span");
    value.className = "band-value";
    value.innerHTML = `<strong>${formatCount(band.customer_count)}</strong> <span>· ${formatPercent(band.portfolio_share)}</span>`;
    row.append(label, track, value);
    return row;
  }));
  elements.riskReference.textContent = `${summary.risk_band_reference}. The fixed validation-cohort method is descriptive; these bands are not action thresholds.`;
}

function renderCapacity(result) {
  const capacity = result.capacity;
  const denominator = capacity.target_review_count;
  const utilization = denominator > 0 ? capacity.selected_count / denominator : 0;
  const safeUtilization = Math.max(0, Math.min(1, utilization));
  const percentage = denominator > 0 ? Math.round(safeUtilization * 100) : null;
  const degrees = safeUtilization * 360;

  elements.capacityRing.style.background = `conic-gradient(#438675 0deg ${degrees}deg, #e8efeb ${degrees}deg 360deg)`;
  elements.capacityPercent.textContent = percentage === null ? "—" : `${percentage}%`;

  const items = [
    { label: "Requested", count: capacity.requested_review_count, note: "Analyst capacity" },
    { label: "Selected", count: capacity.selected_count, note: "Entered the queue" },
    { label: "Unused", count: capacity.unused_capacity, note: "Tie-aware remainder" },
  ];
  elements.capacityLegend.replaceChildren(...items.map((item) => {
    const entry = document.createElement("div");
    entry.className = "legend-item";
    const dot = document.createElement("span");
    dot.className = "legend-dot";
    dot.setAttribute("aria-hidden", "true");
    const copy = document.createElement("span");
    copy.className = "legend-copy";
    const strong = document.createElement("strong");
    strong.textContent = `${item.label}: ${formatCount(item.count)}`;
    const note = document.createElement("span");
    note.textContent = item.note;
    copy.append(strong, note);
    entry.append(dot, copy);
    return entry;
  }));

  if (denominator === 0) {
    elements.capacityFootnote.textContent = "No review capacity was requested; no customers were selected.";
  } else if (capacity.unused_capacity > 0) {
    elements.capacityFootnote.textContent = "Some capacity remained unused because the queue keeps equal-score customers together at the selection boundary.";
  } else {
    elements.capacityFootnote.textContent = "The requested target was filled. Equal-score groups are kept together at the selection boundary.";
  }
}

function getRiskBand(record) {
  const score = record.predicted_default_probability;
  return currentResult.portfolio_summary.risk_bands.find((band) =>
    (band.lower_bound_exclusive === null || score > band.lower_bound_exclusive)
    && (band.upper_bound_inclusive === null || score <= band.upper_bound_inclusive)
  )?.label ?? "Unassigned";
}

function resetExploreFilters() {
  elements.customerIdFilter.value = "";
  elements.scoreMinFilter.value = "0";
  elements.scoreMaxFilter.value = "1";
  elements.riskBandFilter.value = "";
  elements.reviewStatusFilter.value = "";
  elements.featureFilter.value = "";
  elements.featureValueControl.replaceChildren();
  elements.featureValueControl.hidden = true;
  elements.filterMessage.textContent = "";
  currentPage = 0;
}

function initializeExploreFields() {
  const fields = dashboardConfig.required_columns.filter((field) => field !== "ID");
  elements.featureFilter.replaceChildren(new Option("No input filter", ""));
  elements.groupByField.replaceChildren(...fields.map((field) => new Option(field, field)));
  elements.featureFilter.append(...fields.map((field) => new Option(field, field)));
  elements.groupByField.value = "SEX";
}

function renderFeatureValueControl() {
  const field = elements.featureFilter.value;
  elements.featureValueControl.replaceChildren();
  if (!field || !currentPortfolio.length) {
    elements.featureValueControl.hidden = true;
    return;
  }
  elements.featureValueControl.hidden = false;
  if (CATEGORICAL_FIELDS.has(field)) {
    const label = document.createElement("label");
    label.className = "filter-control";
    const title = document.createElement("span");
    title.textContent = `${field} value`;
    const select = document.createElement("select");
    select.id = "feature-filter-value";
    select.append(new Option("All values", ""));
    [...new Set(currentPortfolio.map((row) => row[field]))]
      .sort((left, right) => left - right)
      .forEach((value) => select.append(new Option(String(value), String(value))));
    select.addEventListener("change", () => runExploreFilters(true));
    label.append(title, select);
    elements.featureValueControl.append(label);
    return;
  }

  const values = currentPortfolio.map((row) => row[field]);
  const minimum = Math.min(...values);
  const maximum = Math.max(...values);
  const label = document.createElement("span");
  label.textContent = `${field} range`;
  const inputs = document.createElement("div");
  inputs.className = "feature-range-inputs";
  for (const [caption, id, value] of [["Min", "feature-filter-min", minimum], ["Max", "feature-filter-max", maximum]]) {
    const inputLabel = document.createElement("label");
    inputLabel.className = "visually-hidden";
    inputLabel.htmlFor = id;
    inputLabel.textContent = `${field} ${caption.toLowerCase()}`;
    const input = document.createElement("input");
    input.type = "number";
    input.id = id;
    input.step = "any";
    input.value = String(value);
    input.dataset.bound = caption.toLowerCase();
    input.addEventListener("input", () => runExploreFilters(true));
    inputs.append(inputLabel, input);
  }
  elements.featureValueControl.append(label, inputs);
}

function numericQuantile(values, proportion) {
  const sorted = [...values].sort((left, right) => left - right);
  const position = (sorted.length - 1) * proportion;
  const lower = Math.floor(position);
  const fraction = position - lower;
  return sorted[lower + 1] === undefined
    ? sorted[lower]
    : sorted[lower] + fraction * (sorted[lower + 1] - sorted[lower]);
}

function getQuartileBoundaries(field) {
  if (!quartileBoundaryCache.has(field)) {
    const values = currentPortfolio.map((row) => row[field]);
    quartileBoundaryCache.set(field, [
      numericQuantile(values, 0.25),
      numericQuantile(values, 0.5),
      numericQuantile(values, 0.75),
    ]);
  }
  return quartileBoundaryCache.get(field);
}

function getQuartileIndex(value, field) {
  const [first, second, third] = getQuartileBoundaries(field);
  if (value <= first) return 0;
  if (value <= second) return 1;
  if (value <= third) return 2;
  return 3;
}

function getGroupLabel(value, field, index = null) {
  if (CATEGORICAL_FIELDS.has(field)) return String(value);
  const [first, second, third] = getQuartileBoundaries(field);
  const formatBoundary = (boundary) => boundary.toLocaleString(undefined, { maximumSignificantDigits: 7 });
  if (index === 0) return `≤ ${formatBoundary(first)}`;
  if (index === 1) return `${formatBoundary(first)} – ${formatBoundary(second)}`;
  if (index === 2) return `${formatBoundary(second)} – ${formatBoundary(third)}`;
  return `> ${formatBoundary(third)}`;
}

function applyExploreFilters() {
  const idQuery = elements.customerIdFilter.value.trim();
  const minimumScore = elements.scoreMinFilter.value === "" ? 0 : Number(elements.scoreMinFilter.value);
  const maximumScore = elements.scoreMaxFilter.value === "" ? 1 : Number(elements.scoreMaxFilter.value);
  if (minimumScore > maximumScore) {
    elements.filterMessage.textContent = "Minimum predicted risk must not exceed maximum predicted risk.";
    return null;
  }
  elements.filterMessage.textContent = "";
  const band = elements.riskBandFilter.value;
  const reviewStatus = elements.reviewStatusFilter.value;
  const field = elements.featureFilter.value;
  const categoryValue = document.querySelector("#feature-filter-value")?.value ?? "";
  const featureMinimum = document.querySelector("#feature-filter-min")?.value;
  const featureMaximum = document.querySelector("#feature-filter-max")?.value;

  return currentPortfolio.filter((record) => {
    const score = record.predicted_default_probability;
    if (idQuery && !String(record.customer_id).includes(idQuery)) return false;
    if (score < minimumScore || score > maximumScore) return false;
    if (band && getRiskBand(record) !== band) return false;
    if (reviewStatus === "selected" && !record.selected_for_review) return false;
    if (reviewStatus === "not-selected" && record.selected_for_review) return false;
    if (field && CATEGORICAL_FIELDS.has(field) && categoryValue && String(record[field]) !== categoryValue) return false;
    if (field && !CATEGORICAL_FIELDS.has(field)) {
      if (featureMinimum !== undefined && featureMinimum !== "" && record[field] < Number(featureMinimum)) return false;
      if (featureMaximum !== undefined && featureMaximum !== "" && record[field] > Number(featureMaximum)) return false;
    }
    return true;
  });
}

function renderScoreDistribution(rows) {
  const bins = Array.from({ length: 10 }, (_, index) => ({
    lower: index / 10,
    upper: (index + 1) / 10,
    count: 0,
  }));
  rows.forEach((record) => {
    const index = Math.min(9, Math.floor(record.predicted_default_probability * 10));
    bins[index].count += 1;
  });
  const denominator = rows.length;
  elements.scoreDistribution.replaceChildren(...bins.map((bin) => {
    const row = document.createElement("div");
    row.className = "distribution-row";
    row.setAttribute("role", "listitem");
    const label = document.createElement("span");
    label.className = "distribution-label";
    label.textContent = `${Math.round(bin.lower * 100)}–${Math.round(bin.upper * 100)}%`;
    const track = document.createElement("span");
    track.className = "distribution-track";
    track.setAttribute("aria-hidden", "true");
    const fill = document.createElement("span");
    fill.className = "distribution-fill";
    const share = denominator ? bin.count / denominator : 0;
    fill.style.width = `${share * 100}%`;
    track.append(fill);
    const value = document.createElement("span");
    value.className = "distribution-value";
    value.textContent = `${formatCount(bin.count)} · ${formatPercent(share)}`;
    row.append(label, track, value);
    return row;
  }));
}

function renderGroupSummary(rows) {
  const field = elements.groupByField.value;
  if (!rows.length) {
    const emptyRow = document.createElement("tr");
    const message = document.createElement("td");
    message.colSpan = 5;
    message.textContent = "No customers match the current filters.";
    emptyRow.append(message);
    elements.groupSummaryBody.replaceChildren(emptyRow);
    elements.groupTableNote.textContent = "Adjust or reset the filters to compare groups.";
    return;
  }
  const groups = new Map();
  rows.forEach((record) => {
    const groupKey = CATEGORICAL_FIELDS.has(field)
      ? String(record[field])
      : String(getQuartileIndex(record[field], field));
    if (!groups.has(groupKey)) {
      const groupIndex = CATEGORICAL_FIELDS.has(field) ? null : Number(groupKey);
      groups.set(groupKey, { label: getGroupLabel(record[field], field, groupIndex), records: [] });
    }
    groups.get(groupKey).records.push(record);
  });
  const orderedGroups = [...groups.entries()].sort((left, right) => {
    if (CATEGORICAL_FIELDS.has(field)) return Number(left[0]) - Number(right[0]);
    return Number(left[0]) - Number(right[0]);
  });
  elements.groupSummaryBody.replaceChildren(...orderedGroups.map(([, group]) => {
    const { label, records } = group;
    const row = document.createElement("tr");
    const values = [
      label,
      formatCount(records.length),
      formatPercent(rows.length ? records.length / rows.length : 0),
      formatPercent(records.reduce((sum, item) => sum + item.predicted_default_probability, 0) / records.length),
      formatCount(records.filter((item) => item.selected_for_review).length),
    ];
    values.forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    return row;
  }));
  elements.groupTableNote.textContent = CATEGORICAL_FIELDS.has(field)
    ? `Encoded values for ${field} are shown as supplied; group shares use the filtered cohort.`
    : `Quartile boundaries for ${field} are calculated from the full portfolio; shares use the filtered cohort.`;
}

function renderCustomerTable(rows) {
  const pageCount = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  currentPage = Math.min(currentPage, pageCount - 1);
  const start = currentPage * PAGE_SIZE;
  const visibleRows = rows.slice(start, start + PAGE_SIZE);
  const tableRows = visibleRows.map((record) => {
    const row = document.createElement("tr");
    const values = [
      formatCount(record.risk_rank),
      formatCount(record.customer_id),
      formatPercent(record.predicted_default_probability),
      getRiskBand(record),
      record.selected_for_review ? "Selected" : "Not selected",
    ];
    values.forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    return row;
  });
  if (!rows.length) {
    const emptyRow = document.createElement("tr");
    const message = document.createElement("td");
    message.colSpan = 5;
    message.textContent = "No customers match the current filters.";
    emptyRow.append(message);
    tableRows.push(emptyRow);
  }
  elements.customerResultsBody.replaceChildren(...tableRows);
  const first = rows.length ? start + 1 : 0;
  const last = Math.min(start + PAGE_SIZE, rows.length);
  elements.pageCount.textContent = `${formatCount(first)}–${formatCount(last)} of ${formatCount(rows.length)}`;
  elements.pageStatus.textContent = `Page ${currentPage + 1} of ${pageCount}`;
  elements.previousPage.disabled = currentPage === 0;
  elements.nextPage.disabled = currentPage >= pageCount - 1;
}

function runExploreFilters(resetPage = false) {
  if (resetPage) currentPage = 0;
  const rows = applyExploreFilters();
  if (rows === null) return;
  filteredPortfolio = rows;
  elements.exploreCount.textContent = `${formatCount(rows.length)} of ${formatCount(currentPortfolio.length)} customers`;
  renderScoreDistribution(rows);
  renderGroupSummary(rows);
  renderCustomerTable(rows);
}

function renderQueueView(result) {
  const capacity = result.capacity;
  queuePage = 0;
  elements.queuePopulationCount.textContent = `${formatCount(result.population_count)} customers scored`;
  const utilization = capacity.target_review_count > 0
    ? formatPercent(capacity.selected_count / capacity.target_review_count)
    : "—";
  const metrics = [
    { label: "Requested capacity", value: formatCount(capacity.requested_review_count), help: "Analyst-entered limit" },
    { label: "Target count", value: formatCount(capacity.target_review_count), help: "Capped at portfolio size" },
    { label: "Selected for review", value: formatCount(capacity.selected_count), help: `${utilization} of target filled` },
    { label: "Unused capacity", value: formatCount(capacity.unused_capacity), help: "Target minus selected" },
  ];
  elements.queueMetricGrid.replaceChildren(...metrics.map((metric) => {
    const card = document.createElement("article");
    card.className = "metric-card queue-metric-card";
    const label = document.createElement("span");
    label.className = "metric-label";
    label.textContent = metric.label;
    const value = document.createElement("strong");
    value.className = "metric-value";
    value.textContent = metric.value;
    const help = document.createElement("span");
    help.className = "metric-help";
    help.textContent = metric.help;
    card.append(label, value, help);
    return card;
  }));

  const reasonGroups = new Map();
  result.customers.forEach((record) => {
    if (!reasonGroups.has(record.reason_code)) {
      reasonGroups.set(record.reason_code, { reason: record.reason, count: 0 });
    }
    reasonGroups.get(record.reason_code).count += 1;
  });
  elements.queueReasonsBody.replaceChildren(...[...reasonGroups.values()].map((group) => {
    const row = document.createElement("tr");
    const reason = document.createElement("td");
    reason.textContent = group.reason;
    const count = document.createElement("td");
    count.textContent = formatCount(group.count);
    row.append(reason, count);
    return row;
  }));
  renderSelectedQueue(result.customers.filter((record) => record.selected_for_review));
}

function renderSelectedQueue(selectedCustomers) {
  const pageCount = Math.max(1, Math.ceil(selectedCustomers.length / PAGE_SIZE));
  queuePage = Math.min(queuePage, pageCount - 1);
  const start = queuePage * PAGE_SIZE;
  const currentRows = selectedCustomers.slice(start, start + PAGE_SIZE);
  const rows = currentRows.map((record) => {
    const row = document.createElement("tr");
    [
      formatCount(record.risk_rank),
      formatCount(record.customer_id),
      formatPercent(record.predicted_default_probability),
      record.reason,
    ].forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    return row;
  });
  if (!selectedCustomers.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 4;
    cell.textContent = "No customers were selected under this capacity.";
    row.append(cell);
    rows.push(row);
  }
  elements.selectedQueueBody.replaceChildren(...rows);
  const first = selectedCustomers.length ? start + 1 : 0;
  const last = Math.min(start + PAGE_SIZE, selectedCustomers.length);
  elements.queuePageCount.textContent = `${formatCount(first)}–${formatCount(last)} of ${formatCount(selectedCustomers.length)}`;
  elements.queuePageStatus.textContent = `Page ${queuePage + 1} of ${pageCount}`;
  elements.queuePreviousPage.disabled = queuePage === 0;
  elements.queueNextPage.disabled = queuePage >= pageCount - 1;
}

function setActiveView(view) {
  if (view !== "overview" && !currentResult) return;
  activeView = view;
  elements.results.hidden = view !== "overview" || !currentResult;
  elements.exploreView.hidden = view !== "explore" || !currentResult;
  elements.queueView.hidden = view !== "queue" || !currentResult;
  elements.emptyState.hidden = Boolean(currentResult);
  elements.viewLinks.forEach((link) => {
    const active = link.dataset.view === view;
    link.classList.toggle("is-active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  const viewLabels = { overview: "Overview", explore: "Explore portfolio", queue: "Review queue" };
  document.querySelector(".breadcrumb").lastChild.textContent = ` ${viewLabels[view]}`;
}

function renderOverview(result, inputRows) {
  currentResult = result;
  const inputsById = new Map(inputRows.map((row) => [row.ID, row]));
  currentPortfolio = result.customers.map((scoredRow) => ({
    ...inputsById.get(scoredRow.customer_id),
    ...scoredRow,
  }));
  quartileBoundaryCache.clear();
  initializeExploreFields();
  resetExploreFilters();
  renderQueueView(result);
  renderMetricCards(result);
  renderRiskBands(result.portfolio_summary);
  renderCapacity(result);
  elements.portfolioCount.textContent = `${formatCount(result.population_count)} customers`;
  elements.analysisMetaText.textContent = `Scored ${new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}`;
  elements.analysisMeta.hidden = false;
  runExploreFilters();
  setActiveView("overview");
  elements.results.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function readSelectedFile() {
  if (!selectedFile) throw new Error("Choose a CSV file before running the analysis.");
  const text = await selectedFile.text();
  return validateCsvRows(parseCsv(text));
}

async function loadDashboardConfig() {
  const response = await fetch("/v1/dashboard-config");
  if (!response.ok) throw new Error("The dashboard couldn’t load its setup details. Refresh and try again.");
  dashboardConfig = await response.json();
  elements.fileHint.textContent = `ID and all 23 predictors · up to ${formatCount(dashboardConfig.max_customer_rows)} customers`;
  elements.capacity.max = String(dashboardConfig.max_customer_rows);
}

async function checkService() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("Portfolio scoring is temporarily unavailable.");
    const health = await response.json();
    if (!health.model_loaded) throw new Error("Portfolio scoring isn’t ready yet. Try again shortly.");
    setServiceStatus(true, "Ready to score portfolios");
  } catch (error) {
    setServiceStatus(false, "Portfolio scoring is temporarily unavailable.");
  }
}

elements.file.addEventListener("change", () => {
  selectedFile = elements.file.files?.[0] ?? null;
  clearMessage();
  if (selectedFile) {
    elements.fileName.textContent = selectedFile.name;
    elements.fileHint.textContent = `${(selectedFile.size / 1024).toFixed(0)} KB · ready to validate`;
    elements.fileName.title = selectedFile.name;
  } else {
    elements.fileName.textContent = "Choose a CSV file";
  }
});

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearMessage();
  elements.runButton.disabled = true;
  elements.runButton.querySelector("span:first-child").textContent = "Scoring portfolio…";

  try {
    if (!dashboardConfig) await loadDashboardConfig();
    const customers = await readSelectedFile();
    if (elements.capacity.value.trim() === "") {
      throw new Error("Enter a review capacity.");
    }
    const capacity = Number(elements.capacity.value);
    if (!Number.isSafeInteger(capacity) || capacity < 0) {
      throw new Error("Review capacity must be a non-negative whole number.");
    }

    const response = await fetch("/v1/review-queue", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ customers, max_review_count: capacity }),
    });
    const payload = await response.json();
    if (!response.ok) {
      const details = payload?.error?.details?.filter(Boolean).join(" ");
      throw new Error(details || payload?.error?.message || "The scoring request failed.");
    }

    renderOverview(payload, customers);
    setServiceStatus(true, "Ready to score portfolios");
    showMessage(`Analysis complete for ${formatCount(payload.population_count)} customers.`, "success");
  } catch (error) {
    const message = error instanceof TypeError
      ? "Portfolio scoring is temporarily unavailable. Check your connection and try again."
      : error.message || "The portfolio could not be scored.";
    showMessage(message);
  } finally {
    elements.runButton.disabled = false;
    elements.runButton.querySelector("span:first-child").textContent = "Run analysis";
  }
});

elements.healthCheck.addEventListener("click", checkService);

elements.viewLinks.forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    setActiveView(link.dataset.view);
    if (currentResult) window.location.hash = link.dataset.view;
  });
});

[
  elements.customerIdFilter,
  elements.scoreMinFilter,
  elements.scoreMaxFilter,
  elements.riskBandFilter,
  elements.reviewStatusFilter,
].forEach((control) => control.addEventListener("input", () => runExploreFilters(true)));
[
  elements.riskBandFilter,
  elements.reviewStatusFilter,
].forEach((control) => control.addEventListener("change", () => runExploreFilters(true)));
elements.featureFilter.addEventListener("change", () => {
  renderFeatureValueControl();
  runExploreFilters(true);
});
elements.groupByField.addEventListener("change", () => runExploreFilters(true));
elements.resetFilters.addEventListener("click", () => {
  resetExploreFilters();
  runExploreFilters(true);
});
elements.previousPage.addEventListener("click", () => {
  currentPage = Math.max(0, currentPage - 1);
  renderCustomerTable(filteredPortfolio);
});
elements.nextPage.addEventListener("click", () => {
  currentPage += 1;
  renderCustomerTable(filteredPortfolio);
});
elements.queuePreviousPage.addEventListener("click", () => {
  queuePage = Math.max(0, queuePage - 1);
  renderSelectedQueue(currentResult.customers.filter((record) => record.selected_for_review));
});
elements.queueNextPage.addEventListener("click", () => {
  queuePage += 1;
  renderSelectedQueue(currentResult.customers.filter((record) => record.selected_for_review));
});

loadDashboardConfig()
  .then(checkService)
  .catch(() => setServiceStatus(false, "Portfolio scoring is temporarily unavailable."));

```

## Limits

The current page shows the queue from the last completed scoring request. Changing review capacity requires another request and scoring run; this step does not add a server-side cache or a hypothetical-capacity tool. The queue remains a risk-prioritization rule, not a lending eligibility decision or evidence that reviewing a selected customer changes outcomes.

---

<a id="step-9-8"></a>
## Step 9.8

# Phase 9.8 — Compare Selected and Not Selected Customers

## Decision

The user chose **Option A: side-by-side descriptive statistics**. This step
adds a customer-profile comparison to the Review queue view. It describes the
groups created by the current review capacity and tie-handling policy; it does
not estimate an effect, explain a cause, or compare customer quality.

## What changed

- Added a **Selected and not selected** section below the queue policy and
  outcome summary, before the selected-customer list.
- Showed the size and share of the full uploaded portfolio for each group.
- Compared predicted risk, credit limit, age, average bill amount, and average
  payment amount in the two groups.
- For every measure, showed the median, 25th–75th percentile interval, full
  observed range, number of available records, and number missing.
- Calculated each customer's bill and payment averages across the six supplied
  monthly fields. A customer average is missing if any of its six source values
  is unavailable.
- Kept both groups visible when one is empty, reported exact group sizes, and
  placed interpretation limits beside the comparison.
- Used the full uploaded portfolio regardless of Explore portfolio filters.
  No API schema, queue policy, or database change was needed.

## Definitions and denominators

The selected group consists of records whose `selected_for_review` value is
true in the completed scoring result. The other group contains the remaining
records. The displayed group share is the group count divided by the complete
uploaded portfolio count; it is not the current filtered Explore count.

For each numeric measure, the dashboard omits non-finite values, sorts the
usable values, and calculates the median and quartiles with linear
interpolation at positions `(n - 1) × p`. The full range is the minimum and
maximum usable value. “Available” is the number of usable values for that
measure, and “missing” is the group size minus that number. The CSV validation
currently requires complete numeric inputs, so missing counts are normally
zero; the display remains explicit if a value is unavailable.

The bill and payment measures are per-customer arithmetic means over the six
provided `BILL_AMT1`–`BILL_AMT6` and `PAY_AMT1`–`PAY_AMT6` fields. The
dashboard does not infer a trend or assign a calendar month label. Monetary
amounts retain the source's numeric units; no currency symbol is inferred.

No minimum group size is used to suppress values. Exact group sizes remain
visible, and the nearby note explains that individual records can have more
influence when a group is small. This is appropriate for a descriptive view of
the uploaded data, not a statistical significance or fairness test.

## Step-by-step code walkthrough

### 1. Place the comparison in the queue journey (`index.html`)

The section follows the capacity policy and reason totals and precedes the
selected-customer table. That order lets the analyst first understand the
selection rule, then inspect how the two policy groups differ in this file.
Its copy states that the comparison uses the full uploaded portfolio and is
descriptive. It keeps the bill/payment averaging definition and small-group
caveat close to the displayed numbers.

### 2. Define the measures (`PROFILE_MEASURES` in `app.js`)

The five measures are predicted default probability, credit limit, age, the
per-customer average bill amount, and the per-customer average payment amount.
Each measure pairs a label, a value-reading function, and a display formatter.
Risk uses the dashboard's percentage formatter; the other quantities use
locale-aware numeric formatting without an assumed currency.

`meanOfFields` computes the two six-field per-customer averages. It requires
all six values so an incomplete source row is treated as missing instead of
quietly averaging only the available months.

### 3. Calculate the summaries (`quantile` and `summarizeMeasure`)

`summarizeMeasure` reads finite values for one measure, sorts them, then
returns the count, missing count, minimum, 25th percentile, median, 75th
percentile, and maximum. `quantile` uses linear interpolation between adjacent
values. It returns no numeric summaries for an empty group, avoiding invalid
calculations and divide-by-zero behavior.

### 4. Build the two groups (`renderSelectionProfile`)

The function partitions the already-scored customer records using their
returned selection flag. It does not rerank customers or reconstruct the
capacity rule. Each group heading shows its count and its share of the full
portfolio. An empty group gets an explicit message; a non-empty group gets the
same five measures in the same order for easy comparison.

The function creates DOM elements and assigns content through `textContent`,
so uploaded values are not interpreted as markup. The comparison is rebuilt
after each successful scoring run using the latest completed result.

### 5. Keep the cards readable at different widths (`styles.css`)

The two groups sit side by side on wide screens and stack on narrower screens.
Each measure separates its label from the median, middle half, range, and
available/missing counts. The selected group gets a subtle green tint that
matches the existing light dashboard palette.

## Interpretation limits

The groups are defined by the current risk-ranking and capacity policy.
Predicted risk is one of the selection inputs, so a score difference is
expected from the rule and should not be read as an independent finding.
Differences in credit limit, age, or payment amounts are descriptions of these
two groups; they do not establish why a customer was selected, predict an
observed outcome, imply that an intervention will help, or establish fairness.
This comparison does not adjust for other features or estimate uncertainty.

## Complete frontend code

The following are the complete current frontend files. They include the
dashboard behavior from Steps 9.5–9.7 so the new selection-profile code can be
read in context.

### `src/propensity_prediction/dashboard/static/index.html`

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#f4f7f4" />
    <meta
      name="description"
      content="Understand a scored customer portfolio and its review capacity."
    />
    <title>Portfolio overview | Credit risk review</title>
    <link rel="stylesheet" href="/styles.css" />
    <script src="/app.js" defer></script>
  </head>
  <body>
    <div class="app-shell">
      <aside class="sidebar" aria-label="Dashboard navigation">
        <a class="brand" href="/" aria-label="Portfolio review home">
          <span class="brand-mark" aria-hidden="true">P</span>
          <span class="brand-copy">
            <strong>Portfolio</strong>
            <span>Risk review</span>
          </span>
        </a>

        <p class="nav-label">WORKSPACE</p>
        <nav class="primary-nav" aria-label="Primary">
          <a class="nav-link is-active" href="#overview" data-view="overview" aria-current="page">
            <span class="nav-icon" aria-hidden="true">▦</span>
            <span>Overview</span>
          </a>
          <a class="nav-link" href="#explore" data-view="explore">
            <span class="nav-icon" aria-hidden="true">⌕</span>
            <span>Explore portfolio</span>
          </a>
          <a class="nav-link" href="#queue" data-view="queue">
            <span class="nav-icon" aria-hidden="true">≡</span>
            <span>Review queue</span>
          </a>
        </nav>

        <div class="sidebar-bottom">
          <div class="sidebar-note">
            <span class="note-icon" aria-hidden="true">i</span>
            <p>Predicted risk helps prioritize review. It is not an outcome or an action recommendation.</p>
          </div>
          <span class="service-status" id="service-status" role="status">
            <span class="status-dot" aria-hidden="true"></span>
            Checking portfolio scoring
          </span>
        </div>
      </aside>

      <main class="main-content" id="overview">
        <header class="topbar">
          <div class="breadcrumb">Workspace <span aria-hidden="true">/</span> Overview</div>
          <div class="topbar-actions">
            <button class="text-button" id="health-check" type="button">Check status</button>
            <span class="avatar" aria-hidden="true">AR</span>
          </div>
        </header>

        <section class="page-heading" aria-labelledby="page-title">
          <div>
            <p class="eyebrow">PORTFOLIO INSIGHTS</p>
            <h1 id="page-title">Portfolio overview</h1>
            <p class="page-description">A clear view of predicted risk and review capacity for your customer portfolio.</p>
          </div>
          <div class="analysis-meta" id="analysis-meta" hidden>
            <span class="meta-dot" aria-hidden="true"></span>
            <span id="analysis-meta-text">Analysis complete</span>
          </div>
        </section>

        <section class="analysis-panel" aria-labelledby="analysis-title">
          <div class="analysis-panel-copy">
            <span class="step-badge">NEW ANALYSIS</span>
            <h2 id="analysis-title">Start with a customer portfolio</h2>
            <p>Upload a prediction-time CSV, set your review capacity, and score the full portfolio.</p>
          </div>
          <form id="analysis-form" class="analysis-form">
            <label class="file-drop" for="portfolio-file">
              <span class="upload-icon" aria-hidden="true">↑</span>
              <span class="file-drop-copy">
                <strong id="file-name">Choose a CSV file</strong>
                <span id="file-hint">ID and all 23 predictors · up to 30,000 customers</span>
              </span>
              <span class="browse-button">Browse files</span>
            </label>
            <input id="portfolio-file" class="visually-hidden" type="file" accept=".csv,text/csv" />
            <div class="form-actions">
              <label class="capacity-field" for="review-capacity">
                <span>Review capacity</span>
                <span class="capacity-input-wrap">
                  <input id="review-capacity" type="number" min="0" step="1" value="10" inputmode="numeric" />
                  <span>customers</span>
                </span>
              </label>
              <button class="primary-button" id="run-analysis" type="submit">
                <span>Run analysis</span><span aria-hidden="true">→</span>
              </button>
            </div>
            <p class="capacity-refresh-note">Changing capacity takes effect when you run the analysis; the current results stay in place until then.</p>
            <p class="form-message" id="form-message" role="alert" hidden></p>
          </form>
        </section>

        <section class="results-section" id="results-section" aria-labelledby="results-title" hidden>
          <div class="section-heading">
            <div>
              <p class="eyebrow">AT A GLANCE</p>
              <h2 id="results-title">Portfolio snapshot</h2>
              <p class="section-description">Summary of model estimates for the full uploaded portfolio.</p>
            </div>
            <span class="portfolio-count" id="portfolio-count"></span>
          </div>

          <div class="metric-grid" id="metric-grid" aria-label="Portfolio summary metrics"></div>

          <div class="insight-grid">
            <article class="card band-card" aria-labelledby="bands-title">
              <div class="card-heading">
                <div>
                  <h3 id="bands-title">Predicted risk bands</h3>
                  <p>How customers are distributed across the fixed reference bands.</p>
                </div>
                <span class="chart-mark" aria-hidden="true">▥</span>
              </div>
              <div class="band-list" id="risk-band-chart" role="list"></div>
              <details class="chart-note">
                <summary>How to read these bands</summary>
                <p id="risk-band-reference"></p>
                <p>These bands describe relative predicted risk. They are not action thresholds and do not change queue selection.</p>
              </details>
            </article>

            <article class="card capacity-card" aria-labelledby="capacity-title">
              <div class="card-heading">
                <div>
                  <h3 id="capacity-title">Review capacity</h3>
                  <p>How the requested capacity translated into the queue.</p>
                </div>
                <span class="chart-mark capacity-mark" aria-hidden="true">◎</span>
              </div>
              <div class="capacity-visual">
                <div class="capacity-ring" id="capacity-ring" aria-label="Capacity utilization">
                  <div class="ring-center">
                    <strong id="capacity-percent">0%</strong>
                    <span>of target selected</span>
                  </div>
                </div>
                <div class="capacity-legend" id="capacity-legend"></div>
              </div>
              <div class="capacity-footnote" id="capacity-footnote"></div>
            </article>
          </div>

          <div class="interpretation-note">
            <span class="note-icon" aria-hidden="true">i</span>
            <p><strong>Interpretation:</strong> Predicted probabilities summarize model estimates, not observed outcomes or expected losses. Portfolio patterns are descriptive and do not show that an intervention will change outcomes.</p>
          </div>
        </section>

        <section class="explore-view" id="explore-view" aria-labelledby="explore-title" hidden>
          <div class="section-heading explore-heading">
            <div>
              <p class="eyebrow">COHORT EXPLORATION</p>
              <h2 id="explore-title">Explore portfolio</h2>
              <p class="section-description">Filter scored customers and compare descriptive groups.</p>
            </div>
            <span class="portfolio-count" id="explore-count">0 of 0 customers</span>
          </div>

          <section class="card filters-card" aria-labelledby="filters-title">
            <div class="card-heading filter-heading">
              <div>
                <h3 id="filters-title">Find a cohort</h3>
                <p>Every filter applies to the full scored portfolio. Counts below show the filtered denominator.</p>
              </div>
              <button class="text-button" id="reset-filters" type="button">Reset filters</button>
            </div>
            <div class="filter-grid">
              <label class="filter-control">
                <span>Customer ID</span>
                <input id="filter-customer-id" type="search" inputmode="numeric" placeholder="Search ID" />
              </label>
              <label class="filter-control">
                <span>Minimum predicted risk</span>
                <input id="filter-score-min" type="number" min="0" max="1" step="0.01" value="0" />
              </label>
              <label class="filter-control">
                <span>Maximum predicted risk</span>
                <input id="filter-score-max" type="number" min="0" max="1" step="0.01" value="1" />
              </label>
              <label class="filter-control">
                <span>Reference risk band</span>
                <select id="filter-risk-band">
                  <option value="">All bands</option>
                  <option>Lower</option><option>Moderate</option><option>Elevated</option><option>Highest</option>
                </select>
              </label>
              <label class="filter-control">
                <span>Review status</span>
                <select id="filter-review-status">
                  <option value="">All customers</option>
                  <option value="selected">Selected for review</option>
                  <option value="not-selected">Not selected</option>
                </select>
              </label>
              <label class="filter-control">
                <span>Filter by input field</span>
                <select id="filter-feature">
                  <option value="">No input filter</option>
                </select>
              </label>
              <div class="filter-control feature-value-control" id="feature-value-control" hidden></div>
            </div>
            <p class="filter-message" id="filter-message" role="status"></p>
          </section>

          <div class="explore-summary-grid">
            <article class="card distribution-card">
              <div class="card-heading">
                <div><h3>Predicted-risk distribution</h3><p>Fixed 10 percentage-point bins; shares use the filtered cohort.</p></div>
              </div>
              <div class="score-distribution" id="score-distribution" role="list" aria-label="Predicted-risk distribution"></div>
            </article>
            <article class="card group-card">
              <div class="card-heading group-heading">
                <div><h3>Compare groups</h3><p>Descriptive summaries for the filtered cohort.</p></div>
                <label class="group-field"><span>Group by</span><select id="group-by-field"></select></label>
              </div>
              <div class="table-scroll">
                <table class="group-table">
                  <thead><tr><th scope="col">Group</th><th scope="col">Customers</th><th scope="col">Share</th><th scope="col">Mean risk</th><th scope="col">Selected</th></tr></thead>
                  <tbody id="group-summary-body"></tbody>
                </table>
              </div>
              <p class="table-note" id="group-table-note">For numeric fields, groups use quartile boundaries from the full portfolio.</p>
            </article>
          </div>

          <section class="card customer-results-card" aria-labelledby="customer-results-title">
            <div class="card-heading">
              <div><h3 id="customer-results-title">Matching customers</h3><p>Customers are ordered from highest to lowest predicted risk. The table shows a page at a time.</p></div>
              <span class="portfolio-count" id="page-count">0–0 of 0</span>
            </div>
            <div class="table-scroll">
              <table class="customer-table">
                <thead><tr><th scope="col">Rank</th><th scope="col">Customer ID</th><th scope="col">Predicted risk</th><th scope="col">Risk band</th><th scope="col">Review status</th></tr></thead>
                <tbody id="customer-results-body"></tbody>
              </table>
            </div>
            <div class="pagination-controls">
              <span id="page-status">Page 1 of 1</span>
              <div><button class="secondary-button" id="previous-page" type="button" disabled>Previous</button><button class="secondary-button" id="next-page" type="button" disabled>Next</button></div>
            </div>
          </section>

          <div class="interpretation-note">
            <span class="note-icon" aria-hidden="true">i</span>
            <p><strong>Interpretation:</strong> Filtered groups describe this uploaded portfolio. They do not establish causes, treatment effects, or fairness conclusions. Encoded input values are shown as supplied; category codes are not given inferred labels.</p>
          </div>
        </section>

        <section class="queue-view" id="queue-view" aria-labelledby="queue-title" hidden>
          <div class="section-heading queue-heading">
            <div>
              <p class="eyebrow">CAPACITY DECISION</p>
              <h2 id="queue-title">Review queue</h2>
              <p class="section-description">How your review capacity shaped the ranked customer list.</p>
            </div>
            <span class="portfolio-count" id="queue-population-count"></span>
          </div>

          <div class="queue-metric-grid" id="queue-metric-grid" aria-label="Queue capacity summary"></div>

          <div class="queue-explanation-grid">
            <article class="card queue-policy-card">
              <div class="card-heading">
                <div><h3>How selection works</h3><p>A consistent selection rule determines who enters the review list.</p></div>
                <span class="chart-mark capacity-mark" aria-hidden="true">↕</span>
              </div>
              <ol class="queue-policy-list">
                <li><strong>Rank by predicted risk.</strong><span>Customers are ordered from highest to lowest predicted default probability. Equal scores receive the same rank, so later ranks account for all customers ahead.</span></li>
                <li><strong>Keep equal scores together.</strong><span>Customers with the same risk score enter the review list together when the group fits within your capacity.</span></li>
                <li><strong>Stop at a boundary tie.</strong><span>If the next tied group would exceed the remaining target, that whole group and all lower-scoring groups are left out.</span></li>
              </ol>
              <div class="queue-refresh-note"><strong>To change capacity:</strong> edit Review capacity above and click Run analysis. This queue shows the result from the last completed run.</div>
            </article>

            <article class="card queue-outcomes-card">
              <div class="card-heading">
                <div><h3>Why customers were selected or left out</h3><p>These totals explain why customers entered the review list or remained outside it.</p></div>
              </div>
              <div class="table-scroll">
                <table class="group-table">
                  <thead><tr><th scope="col">Queue outcome</th><th scope="col">Customers</th></tr></thead>
                  <tbody id="queue-reasons-body"></tbody>
                </table>
              </div>
              <p class="table-note">Unused capacity can occur when a full tied score group cannot fit. The queue never splits that group or exceeds its target.</p>
            </article>
          </div>

          <section class="card selection-profile-card" aria-labelledby="selection-profile-title">
            <div class="card-heading">
              <div>
                <h3 id="selection-profile-title">Selected and not selected</h3>
                <p>Compare customer profiles under the current review capacity.</p>
              </div>
              <span class="chart-mark" aria-hidden="true">↔</span>
            </div>
            <p class="selection-profile-context">Summaries use the full uploaded portfolio, regardless of filters in Explore portfolio. Each measure shows the median, middle half of values, full range, and available and missing record counts.</p>
            <div class="selection-profile-groups" id="selection-profile-groups" aria-live="polite"></div>
            <p class="table-note">Average bill and payment amounts are calculated per customer across the six supplied monthly fields. Small groups are shown with their exact count; individual records can have more influence in a small group. These descriptive differences do not show causes, outcomes, or intervention effects.</p>
          </section>

          <section class="card selected-queue-card" aria-labelledby="selected-queue-title">
            <div class="card-heading">
              <div><h3 id="selected-queue-title">Selected customers</h3><p>Customers are listed from highest to lowest predicted risk.</p></div>
              <span class="portfolio-count" id="queue-page-count">0–0 of 0</span>
            </div>
            <div class="table-scroll">
              <table class="customer-table">
                <thead><tr><th scope="col">Rank</th><th scope="col">Customer ID</th><th scope="col">Predicted risk</th><th scope="col">Selection reason</th></tr></thead>
                <tbody id="selected-queue-body"></tbody>
              </table>
            </div>
            <div class="pagination-controls">
              <span id="queue-page-status">Page 1 of 1</span>
              <div><button class="secondary-button" id="queue-previous-page" type="button" disabled>Previous</button><button class="secondary-button" id="queue-next-page" type="button" disabled>Next</button></div>
            </div>
          </section>

          <div class="interpretation-note">
            <span class="note-icon" aria-hidden="true">i</span>
            <p><strong>Interpretation:</strong> This view explains a model-ranked review policy under the requested capacity. It does not recommend an intervention or estimate the effect of reviewing a customer.</p>
          </div>
        </section>

        <section class="empty-state" id="empty-state" aria-labelledby="empty-title">
          <div class="empty-illustration" aria-hidden="true">
            <span class="illustration-card card-one"></span>
            <span class="illustration-card card-two"></span>
            <span class="illustration-chart"><i></i><i></i><i></i><i></i></span>
          </div>
          <h2 id="empty-title">Your portfolio overview will appear here</h2>
          <p>Upload a customer file above to see the portfolio summary and review-capacity breakdown.</p>
        </section>

        <footer class="page-footer">
          <span>Credit risk review · Analyst workspace</span>
          <span>Model estimates support review prioritization only</span>
        </footer>
      </main>
    </div>
  </body>
</html>
```

### `src/propensity_prediction/dashboard/static/styles.css`

```css
:root {
  color-scheme: light;
  --canvas: #f4f7f4;
  --surface: #ffffff;
  --surface-muted: #f8faf8;
  --ink: #263a36;
  --ink-strong: #1a302b;
  --ink-muted: #62746f;
  --ink-soft: #7c8b86;
  --line: #e1e9e4;
  --line-strong: #d1ded7;
  --teal: #287c70;
  --teal-dark: #1f685e;
  --teal-soft: #e6f1ed;
  --blue: #6487a2;
  --blue-soft: #eaf0f5;
  --amber: #aa7740;
  --amber-soft: #f5eee3;
  --rose: #a45f62;
  --rose-soft: #f5e9e8;
  --shadow: 0 10px 30px rgb(36 63 53 / 5%);
  --radius: 18px;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
}

* { box-sizing: border-box; }

body {
  min-width: 320px;
  min-height: 100vh;
  margin: 0;
  background: var(--canvas);
  color: var(--ink);
  font-size: 14px;
  line-height: 1.55;
}

button, input { font: inherit; }
button { color: inherit; }
a { color: inherit; }
[hidden] { display: none !important; }

:focus-visible {
  outline: 3px solid #75a99d;
  outline-offset: 3px;
}

.app-shell { min-height: 100vh; }

.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 5;
  display: flex;
  width: 248px;
  flex-direction: column;
  padding: 26px 18px 20px;
  border-right: 1px solid var(--line);
  background: #fbfcfa;
}

.brand {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 2px 8px 28px;
  text-decoration: none;
}

.brand-mark {
  display: grid;
  width: 39px;
  height: 39px;
  place-items: center;
  border-radius: 13px;
  background: var(--teal-dark);
  color: #fff;
  font-family: "Manrope", sans-serif;
  font-size: 19px;
  font-weight: 800;
}

.brand-copy { display: grid; line-height: 1.25; }
.brand-copy strong { color: var(--ink-strong); font-size: 15px; font-weight: 700; }
.brand-copy span { margin-top: 3px; color: var(--ink-muted); font-size: 11px; }

.nav-label, .eyebrow {
  color: var(--ink-soft);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .12em;
}

.nav-label { margin: 0 10px 10px; }
.primary-nav { display: grid; gap: 5px; }

.nav-link {
  display: flex;
  min-height: 44px;
  align-items: center;
  gap: 11px;
  padding: 0 11px;
  border-radius: 10px;
  color: #566963;
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
}

.nav-link.is-active {
  background: var(--teal-soft);
  color: #245f55;
  font-weight: 700;
}

.nav-icon {
  display: inline-grid;
  width: 22px;
  place-items: center;
  color: currentColor;
  font-size: 18px;
  line-height: 1;
}

.nav-link.is-disabled { color: #77857f; cursor: not-allowed; }
.nav-link:not(.is-disabled):hover { background: #f0f5f1; color: var(--teal-dark); }
.nav-soon {
  margin-left: auto;
  color: #77857f;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: .08em;
}

.sidebar-bottom { display: grid; gap: 17px; margin-top: auto; }
.sidebar-note, .interpretation-note {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  border: 1px solid #dfe9e3;
  background: #f1f6f2;
  color: #475d55;
}

.sidebar-note { padding: 12px 11px; border-radius: 12px; }
.sidebar-note p, .interpretation-note p { margin: 0; font-size: 11px; line-height: 1.55; }
.note-icon {
  display: inline-grid;
  width: 18px;
  height: 18px;
  flex: 0 0 auto;
  place-items: center;
  border: 1px solid #9bb5a9;
  border-radius: 50%;
  color: #3f6d5d;
  font-size: 11px;
  font-weight: 700;
}

.service-status { display: flex; align-items: center; gap: 8px; padding: 0 7px; color: var(--ink-muted); font-size: 11px; }
.status-dot, .meta-dot { width: 8px; height: 8px; border-radius: 50%; background: #b3c0b9; }
.service-status.is-ready .status-dot { background: #38876d; box-shadow: 0 0 0 3px #e2f0e8; }
.service-status.is-error .status-dot { background: #a45f62; box-shadow: 0 0 0 3px #f5e9e8; }

.main-content { max-width: 1540px; min-height: 100vh; margin-left: 248px; padding: 0 44px 24px; }
.topbar { display: flex; height: 72px; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--line); }
.breadcrumb { color: var(--ink-muted); font-size: 12px; }
.breadcrumb span { margin: 0 7px; color: #9aa8a2; }
.topbar-actions { display: flex; align-items: center; gap: 16px; }
.text-button { padding: 6px 2px; border: 0; background: transparent; color: #4c665e; cursor: pointer; font-size: 12px; font-weight: 600; }
.text-button:hover { color: var(--teal-dark); }
.avatar { display: grid; width: 31px; height: 31px; place-items: center; border: 1px solid #dce5df; border-radius: 50%; background: #e9f0eb; color: #426257; font-size: 10px; font-weight: 700; }

.page-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; padding: 31px 0 22px; }
.page-heading .eyebrow, .section-heading .eyebrow { margin: 0 0 6px; }
h1, h2, h3, p { margin-top: 0; }
h1, h2, h3 { color: var(--ink-strong); font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
h1 { margin-bottom: 6px; font-size: clamp(24px, 2.4vw, 32px); font-weight: 700; letter-spacing: -.04em; line-height: 1.2; }
.page-description { margin: 0; color: var(--ink-muted); font-size: 13px; }
.analysis-meta { display: inline-flex; align-items: center; gap: 8px; padding: 7px 11px; border: 1px solid var(--line); border-radius: 99px; background: var(--surface); color: #50665e; font-size: 11px; white-space: nowrap; }
.analysis-meta .meta-dot { background: #3c8a6f; }

.analysis-panel {
  display: grid;
  grid-template-columns: minmax(220px, .78fr) minmax(380px, 1.45fr);
  gap: 28px;
  padding: 22px 24px;
  border: 1px solid #dce7e0;
  border-radius: var(--radius);
  background: linear-gradient(116deg, #edf4ef, #f9fbf8 65%);
  box-shadow: var(--shadow);
}

.analysis-panel-copy { align-self: center; }
.step-badge { display: inline-block; margin-bottom: 9px; color: #4e7d6e; font-size: 9px; font-weight: 700; letter-spacing: .13em; }
.analysis-panel h2 { margin: 0 0 6px; font-size: 17px; letter-spacing: -.025em; }
.analysis-panel-copy p { max-width: 330px; margin: 0; color: var(--ink-muted); font-size: 12px; line-height: 1.6; }
.analysis-form { display: grid; align-content: center; gap: 12px; }
.file-drop { display: flex; min-height: 70px; align-items: center; gap: 12px; padding: 10px 12px; border: 1px dashed #aabeb2; border-radius: 12px; background: rgb(255 255 255 / 76%); cursor: pointer; }
.file-drop:hover, .file-drop:focus-within { border-color: var(--teal); background: #fff; }
.upload-icon { display: grid; width: 38px; height: 38px; flex: 0 0 auto; place-items: center; border-radius: 11px; background: #e7f1eb; color: #3d7461; font-size: 22px; font-weight: 500; }
.file-drop-copy { display: grid; min-width: 0; gap: 3px; }
.file-drop-copy strong { overflow: hidden; color: var(--ink-strong); font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.file-drop-copy span { color: var(--ink-muted); font-size: 10px; }
.browse-button { margin-left: auto; padding: 7px 10px; border: 1px solid var(--line-strong); border-radius: 8px; background: #fff; color: #395b50; font-size: 10px; font-weight: 700; white-space: nowrap; }
.visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; clip-path: inset(50%); }
.form-actions { display: flex; align-items: flex-end; justify-content: space-between; gap: 14px; }
.capacity-field { display: grid; gap: 5px; color: #536760; font-size: 10px; font-weight: 600; }
.capacity-input-wrap { display: flex; height: 36px; align-items: center; gap: 8px; padding: 0 9px; border: 1px solid var(--line-strong); border-radius: 8px; background: #fff; color: var(--ink-muted); font-size: 10px; }
.capacity-input-wrap input { width: 78px; border: 0; outline: none; background: transparent; color: var(--ink-strong); font-size: 12px; font-weight: 600; }
.capacity-input-wrap input:focus-visible { outline: 2px solid #75a99d; outline-offset: 2px; }
.primary-button { display: inline-flex; min-height: 37px; align-items: center; justify-content: center; gap: 15px; padding: 0 15px; border: 1px solid var(--teal-dark); border-radius: 8px; background: var(--teal-dark); color: #fff; cursor: pointer; font-size: 11px; font-weight: 700; transition: background .15s ease, transform .15s ease; }
.primary-button:hover { transform: translateY(-1px); background: #19584f; }
.primary-button:disabled { cursor: wait; opacity: .72; transform: none; }
.form-message { margin: 0; color: #8b4448; font-size: 11px; line-height: 1.5; }
.form-message.is-success { color: #34735d; }
.capacity-refresh-note { margin: -4px 0 0; color: var(--ink-soft); font-size: 9px; line-height: 1.45; }

.results-section { padding-top: 31px; }
.section-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 18px; margin-bottom: 15px; }
.section-heading h2 { margin: 0 0 5px; font-size: 19px; letter-spacing: -.03em; }
.section-description { margin: 0; color: var(--ink-muted); font-size: 11px; }
.portfolio-count { padding: 6px 10px; border: 1px solid var(--line); border-radius: 99px; background: #fff; color: #587069; font-size: 10px; font-weight: 600; white-space: nowrap; }
.metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 13px; margin-bottom: 15px; }
.metric-card { min-height: 112px; padding: 16px 17px; border: 1px solid var(--line); border-radius: 14px; background: var(--surface); box-shadow: 0 5px 16px rgb(36 63 53 / 3%); }
.metric-card-top { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.metric-label { color: var(--ink-muted); font-size: 10px; font-weight: 600; }
.metric-icon { display: grid; width: 27px; height: 27px; place-items: center; border-radius: 9px; background: var(--teal-soft); color: #397366; font-size: 13px; }
.metric-card:nth-child(2) .metric-icon { background: var(--blue-soft); color: #597b96; }
.metric-card:nth-child(3) .metric-icon { background: var(--amber-soft); color: #8d6639; }
.metric-card:nth-child(4) .metric-icon { background: var(--rose-soft); color: #92575a; }
.metric-value { display: block; margin-top: 9px; color: var(--ink-strong); font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; font-size: 25px; font-weight: 700; letter-spacing: -.04em; line-height: 1.15; }
.metric-help { display: block; margin-top: 5px; color: var(--ink-soft); font-size: 9px; }

.insight-grid { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(300px, .85fr); gap: 15px; }
.card { min-width: 0; padding: 19px 20px 17px; border: 1px solid var(--line); border-radius: 15px; background: var(--surface); box-shadow: 0 5px 16px rgb(36 63 53 / 3%); }
.card-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 15px; margin-bottom: 18px; }
.card-heading h3 { margin: 0 0 4px; font-size: 14px; letter-spacing: -.02em; }
.card-heading p { margin: 0; color: var(--ink-muted); font-size: 10px; }
.chart-mark { display: grid; width: 30px; height: 30px; flex: 0 0 auto; place-items: center; border-radius: 9px; background: #edf4ef; color: #547c69; font-size: 17px; }
.capacity-mark { background: #edf1f5; color: #617b91; }
.band-list { display: grid; gap: 14px; }
.band-row { display: grid; grid-template-columns: 77px minmax(70px, 1fr) 58px; align-items: center; gap: 12px; }
.band-label { color: #4b6058; font-size: 10px; font-weight: 600; }
.band-track { height: 10px; overflow: hidden; border-radius: 99px; background: #edf1ee; }
.band-fill { display: block; height: 100%; min-width: 0; border-radius: inherit; transition: width .45s ease; }
.band-row[data-band="Lower"] .band-fill { background: #76a994; }
.band-row[data-band="Moderate"] .band-fill { background: #7894a8; }
.band-row[data-band="Elevated"] .band-fill { background: #c49a61; }
.band-row[data-band="Highest"] .band-fill { background: #b97778; }
.band-value { color: #3f554c; font-size: 10px; font-variant-numeric: tabular-nums; text-align: right; }
.band-value strong { color: var(--ink-strong); font-weight: 700; }
.band-value span { color: var(--ink-soft); }
.chart-note { margin-top: 17px; padding-top: 12px; border-top: 1px solid #edf1ee; color: var(--ink-muted); }
.chart-note summary { width: fit-content; color: #466e61; cursor: pointer; font-size: 10px; font-weight: 600; }
.chart-note p { max-width: 640px; margin: 9px 0 0; font-size: 10px; line-height: 1.6; }

.capacity-visual { display: flex; min-height: 150px; align-items: center; justify-content: center; gap: clamp(18px, 4vw, 47px); }
.capacity-ring { display: grid; width: 142px; height: 142px; flex: 0 0 auto; place-items: center; border-radius: 50%; background: conic-gradient(#438675 0deg, #438675 0deg, #e8efeb 0deg 360deg); }
.ring-center { display: grid; width: 110px; height: 110px; align-content: center; justify-items: center; border-radius: 50%; background: #fff; }
.ring-center strong { color: var(--ink-strong); font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; font-size: 24px; letter-spacing: -.04em; }
.ring-center span { color: var(--ink-muted); font-size: 9px; }
.capacity-legend { display: grid; gap: 13px; }
.legend-item { display: grid; grid-template-columns: 9px auto; align-items: start; gap: 8px; color: var(--ink-muted); font-size: 10px; }
.legend-dot { width: 8px; height: 8px; margin-top: 4px; border-radius: 50%; background: #438675; }
.legend-item:nth-child(2) .legend-dot { background: #9bb9aa; }
.legend-item:nth-child(3) .legend-dot { background: #d5ded8; }
.legend-copy { display: grid; gap: 1px; }
.legend-copy strong { color: #42574f; font-size: 11px; font-weight: 700; }
.legend-copy span { color: var(--ink-soft); font-size: 9px; }
.capacity-footnote { min-height: 28px; margin-top: 9px; padding-top: 10px; border-top: 1px solid #edf1ee; color: var(--ink-muted); font-size: 9px; line-height: 1.5; }

.interpretation-note { align-items: flex-start; margin-top: 15px; padding: 11px 13px; border-radius: 11px; }
.interpretation-note p { font-size: 10px; }
.interpretation-note strong { color: #38584d; }

.explore-view { padding-top: 31px; }
.explore-heading { margin-bottom: 15px; }
.filters-card { margin-bottom: 15px; }
.filter-heading { align-items: center; margin-bottom: 15px; }
.filter-heading .text-button { flex: 0 0 auto; }
.filter-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.filter-control { display: grid; min-width: 0; gap: 5px; color: #536760; font-size: 10px; font-weight: 600; }
.filter-control input, .filter-control select, .group-field select {
  width: 100%; min-width: 0; height: 36px; padding: 0 9px; border: 1px solid var(--line-strong);
  border-radius: 8px; background: #fff; color: var(--ink-strong); font-size: 11px;
}
.feature-value-control { align-content: end; }
.feature-value-control[hidden] { display: none; }
.feature-value-control > span { color: #536760; font-size: 10px; font-weight: 600; }
.feature-range-inputs { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.filter-message { min-height: 16px; margin: 8px 0 0; color: #8b4448; font-size: 10px; }
.explore-summary-grid { display: grid; grid-template-columns: minmax(0, .85fr) minmax(0, 1.15fr); gap: 15px; margin-bottom: 15px; }
.distribution-card, .group-card { min-width: 0; }
.score-distribution { display: grid; gap: 8px; }
.distribution-row { display: grid; grid-template-columns: 48px minmax(40px, 1fr) 77px; align-items: center; gap: 9px; }
.distribution-label { color: #4b6058; font-size: 9px; font-variant-numeric: tabular-nums; }
.distribution-track { display: block; height: 9px; overflow: hidden; border-radius: 99px; background: #edf1ee; }
.distribution-fill { display: block; height: 100%; border-radius: inherit; background: #6b9b87; transition: width .25s ease; }
.distribution-value { color: var(--ink-muted); font-size: 9px; font-variant-numeric: tabular-nums; text-align: right; white-space: nowrap; }
.group-heading { align-items: center; }
.group-field { display: grid; min-width: 110px; gap: 3px; color: var(--ink-muted); font-size: 9px; }
.group-field select { height: 31px; }
.table-scroll { width: 100%; overflow: auto; }
.group-table, .customer-table { width: 100%; border-collapse: collapse; font-size: 10px; text-align: left; }
.group-table th, .customer-table th { padding: 9px 8px; border-bottom: 1px solid var(--line-strong); color: var(--ink-muted); font-size: 9px; font-weight: 700; white-space: nowrap; }
.group-table td, .customer-table td { padding: 9px 8px; border-bottom: 1px solid #edf1ee; color: #40564d; font-variant-numeric: tabular-nums; white-space: nowrap; }
.group-table tbody tr:last-child td, .customer-table tbody tr:last-child td { border-bottom: 0; }
.table-note { margin: 10px 0 0; color: var(--ink-soft); font-size: 9px; line-height: 1.5; }
.customer-results-card { margin-bottom: 15px; }
.customer-results-card .card-heading { align-items: center; margin-bottom: 9px; }
.pagination-controls { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-top: 12px; padding-top: 12px; border-top: 1px solid #edf1ee; color: var(--ink-muted); font-size: 10px; }
.pagination-controls > div { display: flex; gap: 7px; }
.secondary-button { min-height: 30px; padding: 0 10px; border: 1px solid var(--line-strong); border-radius: 7px; background: #fff; color: #456258; cursor: pointer; font-size: 10px; font-weight: 600; }
.secondary-button:disabled { cursor: default; color: #9aa8a2; background: #f7f9f7; }

.queue-view { padding-top: 31px; }
.queue-heading { margin-bottom: 15px; }
.queue-metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 13px; margin-bottom: 15px; }
.queue-metric-card { display: grid; min-height: 105px; align-content: start; gap: 2px; }
.queue-metric-card .metric-value { margin-top: 6px; }
.queue-explanation-grid { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(300px, .9fr); gap: 15px; margin-bottom: 15px; }
.queue-policy-list { display: grid; gap: 14px; margin: 0; padding: 0; list-style: none; counter-reset: queue-step; }
.queue-policy-list li { display: grid; grid-template-columns: 25px minmax(0, 1fr); column-gap: 10px; counter-increment: queue-step; }
.queue-policy-list li::before { content: counter(queue-step); display: grid; width: 24px; height: 24px; grid-row: span 2; place-items: center; border-radius: 8px; background: var(--teal-soft); color: #397366; font-size: 10px; font-weight: 700; }
.queue-policy-list strong { color: #38584d; font-size: 11px; }
.queue-policy-list span { margin-top: 2px; color: var(--ink-muted); font-size: 10px; line-height: 1.5; }
.queue-refresh-note { margin-top: 18px; padding: 11px 12px; border: 1px solid #e2eae4; border-radius: 9px; background: var(--surface-muted); color: var(--ink-muted); font-size: 10px; line-height: 1.5; }
.queue-refresh-note strong { color: #3c6558; }
.queue-outcomes-card .group-table td:first-child { min-width: 180px; white-space: normal; line-height: 1.45; }
.selection-profile-card { margin-bottom: 15px; }
.selection-profile-context { margin: -7px 0 14px; color: var(--ink-muted); font-size: 10px; line-height: 1.5; }
.selection-profile-groups { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.selection-profile-group { min-width: 0; padding: 14px; border: 1px solid var(--line); border-radius: 12px; background: var(--surface-muted); }
.selection-profile-group.is-selected { border-color: #d2e5dc; background: #f5faf6; }
.selection-profile-group-heading { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; padding-bottom: 10px; border-bottom: 1px solid var(--line); }
.selection-profile-group-heading h4 { margin: 0; color: var(--ink-strong); font-size: 11px; }
.selection-profile-group-heading span { color: var(--ink-muted); font-size: 9px; text-align: right; }
.selection-profile-measures { display: grid; margin: 0; }
.selection-profile-measure { display: grid; grid-template-columns: minmax(105px, .8fr) minmax(0, 1.2fr); gap: 10px; padding: 10px 0; border-bottom: 1px solid var(--line); }
.selection-profile-measure:last-child { border-bottom: 0; padding-bottom: 0; }
.selection-profile-measure dt { color: #4b6058; font-size: 10px; font-weight: 600; }
.selection-profile-measure dd { display: grid; gap: 2px; margin: 0; color: var(--ink-muted); font-size: 9px; font-variant-numeric: tabular-nums; }
.selection-profile-measure dd strong { color: var(--ink-strong); font-size: 10px; }
.selection-profile-empty { margin: 14px 0 2px; color: var(--ink-muted); font-size: 10px; }
.selected-queue-card { margin-bottom: 15px; }
.selected-queue-card .customer-table td:last-child { min-width: 300px; white-space: normal; line-height: 1.45; }

.empty-state { display: grid; justify-items: center; padding: 34px 20px 30px; color: var(--ink-muted); text-align: center; }
.empty-illustration { position: relative; width: 126px; height: 91px; margin-bottom: 13px; }
.illustration-card { position: absolute; width: 80px; height: 56px; border: 1px solid #dce7e0; border-radius: 10px; background: #fff; box-shadow: var(--shadow); }
.card-one { top: 7px; left: 16px; transform: rotate(-8deg); }
.card-two { top: 5px; left: 35px; transform: rotate(7deg); }
.illustration-chart { position: absolute; right: 9px; bottom: 8px; display: flex; width: 57px; height: 41px; align-items: flex-end; gap: 5px; padding: 6px; border: 1px solid #dce7e0; border-radius: 9px; background: #f8fbf8; }
.illustration-chart i { flex: 1; border-radius: 3px 3px 1px 1px; background: #8bb7a4; }
.illustration-chart i:nth-child(1) { height: 36%; }
.illustration-chart i:nth-child(2) { height: 58%; background: #9bb1bb; }
.illustration-chart i:nth-child(3) { height: 45%; background: #cfb082; }
.illustration-chart i:nth-child(4) { height: 78%; background: #c18787; }
.empty-state h2 { margin: 0 0 5px; font-size: 15px; letter-spacing: -.02em; }
.empty-state p { max-width: 410px; margin: 0; color: var(--ink-muted); font-size: 11px; }
.page-footer { display: flex; justify-content: space-between; gap: 15px; margin-top: 12px; padding: 14px 0 3px; border-top: 1px solid var(--line); color: var(--ink-soft); font-size: 9px; }

@media (max-width: 1120px) {
  .main-content { padding-right: 28px; padding-left: 28px; }
  .sidebar { width: 220px; }
  .main-content { margin-left: 220px; }
  .analysis-panel { grid-template-columns: 1fr; gap: 16px; }
  .analysis-panel-copy p { max-width: 520px; }
  .filter-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .queue-explanation-grid { grid-template-columns: 1fr; }
}

@media (max-width: 820px) {
  .sidebar { position: static; width: auto; height: auto; padding: 13px 18px; border-right: 0; border-bottom: 1px solid var(--line); }
  .brand { padding: 0; }
  .nav-label, .sidebar-bottom { display: none; }
  .primary-nav { display: flex; overflow-x: auto; gap: 4px; margin-top: 13px; }
  .nav-link { min-height: 38px; flex: 0 0 auto; padding: 0 10px; font-size: 11px; }
  .nav-icon { width: 16px; font-size: 15px; }
  .nav-soon { display: none; }
  .main-content { margin-left: 0; padding: 0 20px 20px; }
  .topbar { height: 55px; }
  .insight-grid { grid-template-columns: 1fr; }
  .explore-summary-grid { grid-template-columns: 1fr; }
  .queue-metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; }
  .selection-profile-groups { grid-template-columns: 1fr; }
}

@media (max-width: 560px) {
  .main-content { padding-right: 14px; padding-left: 14px; }
  .page-heading { align-items: flex-start; flex-direction: column; gap: 10px; padding: 23px 0 17px; }
  .analysis-panel { padding: 17px 14px; }
  .file-drop { gap: 9px; }
  .browse-button { padding: 7px; font-size: 9px; }
  .file-drop-copy span { max-width: 180px; font-size: 9px; }
  .form-actions { align-items: stretch; flex-direction: column; }
  .capacity-field { align-items: flex-start; }
  .primary-button { width: 100%; }
  .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; }
  .metric-card { min-height: 104px; padding: 13px; }
  .metric-value { font-size: 22px; }
  .card { padding: 16px 14px; }
  .band-row { grid-template-columns: 68px minmax(45px, 1fr) 52px; gap: 8px; }
  .capacity-visual { gap: 17px; }
  .capacity-ring { width: 120px; height: 120px; }
  .ring-center { width: 94px; height: 94px; }
  .ring-center strong { font-size: 21px; }
  .section-heading { align-items: flex-start; flex-direction: column; }
  .filter-grid { grid-template-columns: 1fr 1fr; }
  .group-heading { align-items: flex-start; flex-direction: column; }
  .page-footer { flex-direction: column; gap: 4px; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; }
}
```

### `src/propensity_prediction/dashboard/static/app.js`

```javascript
"use strict";

const INTEGER_FIELDS = new Set([
  "ID", "SEX", "EDUCATION", "MARRIAGE",
  "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
]);
const NON_NEGATIVE_FIELDS = new Set([
  "LIMIT_BAL", "PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6",
]);
const INTEGER_RANGES = {
  SEX: [1, 2],
  EDUCATION: [0, 4],
  MARRIAGE: [0, 3],
};
const CATEGORICAL_FIELDS = new Set([
  "SEX", "EDUCATION", "MARRIAGE", "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
]);
const PAGE_SIZE = 50;

const elements = {
  form: document.querySelector("#analysis-form"),
  file: document.querySelector("#portfolio-file"),
  fileName: document.querySelector("#file-name"),
  fileHint: document.querySelector("#file-hint"),
  capacity: document.querySelector("#review-capacity"),
  runButton: document.querySelector("#run-analysis"),
  formMessage: document.querySelector("#form-message"),
  status: document.querySelector("#service-status"),
  healthCheck: document.querySelector("#health-check"),
  emptyState: document.querySelector("#empty-state"),
  results: document.querySelector("#results-section"),
  metrics: document.querySelector("#metric-grid"),
  riskBands: document.querySelector("#risk-band-chart"),
  riskReference: document.querySelector("#risk-band-reference"),
  capacityRing: document.querySelector("#capacity-ring"),
  capacityPercent: document.querySelector("#capacity-percent"),
  capacityLegend: document.querySelector("#capacity-legend"),
  capacityFootnote: document.querySelector("#capacity-footnote"),
  portfolioCount: document.querySelector("#portfolio-count"),
  analysisMeta: document.querySelector("#analysis-meta"),
  analysisMetaText: document.querySelector("#analysis-meta-text"),
  exploreView: document.querySelector("#explore-view"),
  queueView: document.querySelector("#queue-view"),
  viewLinks: [...document.querySelectorAll("[data-view]")],
  exploreCount: document.querySelector("#explore-count"),
  customerIdFilter: document.querySelector("#filter-customer-id"),
  scoreMinFilter: document.querySelector("#filter-score-min"),
  scoreMaxFilter: document.querySelector("#filter-score-max"),
  riskBandFilter: document.querySelector("#filter-risk-band"),
  reviewStatusFilter: document.querySelector("#filter-review-status"),
  featureFilter: document.querySelector("#filter-feature"),
  featureValueControl: document.querySelector("#feature-value-control"),
  resetFilters: document.querySelector("#reset-filters"),
  filterMessage: document.querySelector("#filter-message"),
  groupByField: document.querySelector("#group-by-field"),
  scoreDistribution: document.querySelector("#score-distribution"),
  groupSummaryBody: document.querySelector("#group-summary-body"),
  groupTableNote: document.querySelector("#group-table-note"),
  customerResultsBody: document.querySelector("#customer-results-body"),
  pageCount: document.querySelector("#page-count"),
  pageStatus: document.querySelector("#page-status"),
  previousPage: document.querySelector("#previous-page"),
  nextPage: document.querySelector("#next-page"),
  queuePopulationCount: document.querySelector("#queue-population-count"),
  queueMetricGrid: document.querySelector("#queue-metric-grid"),
  queueReasonsBody: document.querySelector("#queue-reasons-body"),
  selectedQueueBody: document.querySelector("#selected-queue-body"),
  queuePageCount: document.querySelector("#queue-page-count"),
  queuePageStatus: document.querySelector("#queue-page-status"),
  queuePreviousPage: document.querySelector("#queue-previous-page"),
  queueNextPage: document.querySelector("#queue-next-page"),
  selectionProfileGroups: document.querySelector("#selection-profile-groups"),
};

let dashboardConfig = null;
let selectedFile = null;
let currentPortfolio = [];
let currentResult = null;
let filteredPortfolio = [];
let currentPage = 0;
let queuePage = 0;
let activeView = "overview";
const quartileBoundaryCache = new Map();

const percentFormatter = new Intl.NumberFormat(undefined, {
  style: "percent",
  maximumFractionDigits: 1,
});
const numberFormatter = new Intl.NumberFormat(undefined, {
  maximumFractionDigits: 0,
});

function showMessage(message, kind = "error") {
  elements.formMessage.textContent = message;
  elements.formMessage.hidden = false;
  elements.formMessage.classList.toggle("is-success", kind === "success");
}

function clearMessage() {
  elements.formMessage.textContent = "";
  elements.formMessage.hidden = true;
  elements.formMessage.classList.remove("is-success");
}

function setServiceStatus(ready, message) {
  elements.status.classList.toggle("is-ready", ready);
  elements.status.classList.toggle("is-error", !ready);
  elements.status.lastChild.textContent = ` ${message}`;
}

function parseCsv(text) {
  const source = text.replace(/^\uFEFF/, "");
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;
  let afterQuote = false;

  for (let index = 0; index < source.length; index += 1) {
    const character = source[index];
    const next = source[index + 1];

    if (inQuotes) {
      if (character === '"' && next === '"') {
        field += '"';
        index += 1;
      } else if (character === '"') {
        inQuotes = false;
        afterQuote = true;
      } else {
        field += character;
      }
      continue;
    }

    if (afterQuote) {
      if (character === ",") {
        row.push(field);
        field = "";
        afterQuote = false;
      } else if (character === "\n" || character === "\r") {
        row.push(field);
        appendCsvRow(rows, row);
        row = [];
        field = "";
        afterQuote = false;
        if (character === "\r" && next === "\n") index += 1;
      } else if (character === " " || character === "\t") {
        // Ignore whitespace between a closing quote and its delimiter.
      } else {
        throw new Error("The CSV has invalid characters after a quoted value.");
      }
      continue;
    }

    if (character === '"') {
      if (field.length > 0) {
        throw new Error("The CSV contains a quote inside an unquoted value.");
      }
      inQuotes = true;
    } else if (character === ",") {
      row.push(field);
      field = "";
    } else if (character === "\n" || character === "\r") {
      row.push(field);
      appendCsvRow(rows, row);
      row = [];
      field = "";
      if (character === "\r" && next === "\n") index += 1;
    } else {
      field += character;
    }
  }

  if (inQuotes) throw new Error("The CSV contains an unclosed quoted value.");
  if (field.length > 0 || row.length > 0 || afterQuote) {
    row.push(field);
    appendCsvRow(rows, row);
  }
  return rows;
}

function appendCsvRow(rows, row) {
  if (row.length === 1 && row[0] === "") return;
  rows.push(row);
}

function parseNumeric(value, column, csvRowNumber) {
  const trimmed = value.trim();
  const decimalPattern = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/;
  if (!decimalPattern.test(trimmed)) {
    throw new Error(`${column} must contain numeric values. Check CSV row ${csvRowNumber}.`);
  }
  const number = Number(trimmed);
  if (!Number.isFinite(number)) {
    throw new Error(`${column} must contain finite numeric values. Check CSV row ${csvRowNumber}.`);
  }
  if (INTEGER_FIELDS.has(column) && !Number.isInteger(number)) {
    throw new Error(`${column} must contain integer values. Check CSV row ${csvRowNumber}.`);
  }
  if (column === "ID" && !Number.isSafeInteger(number)) {
    throw new Error(`ID must be a safely representable integer. Check CSV row ${csvRowNumber}.`);
  }
  if (NON_NEGATIVE_FIELDS.has(column) && number < 0) {
    throw new Error(`${column} must be non-negative. Check CSV row ${csvRowNumber}.`);
  }
  if (Object.hasOwn(INTEGER_RANGES, column)) {
    const [minimum, maximum] = INTEGER_RANGES[column];
    if (number < minimum || number > maximum) {
      throw new Error(`${column} must use values from ${minimum} through ${maximum}. Check CSV row ${csvRowNumber}.`);
    }
  }
  return number;
}

function validateCsvRows(rows) {
  if (!rows.length) throw new Error("The CSV is empty.");
  const [headers, ...dataRows] = rows;
  if (!headers.length || headers.every((header) => header === "")) {
    throw new Error("The CSV must include a header row.");
  }
  if (new Set(headers).size !== headers.length) {
    throw new Error("The CSV contains duplicate column names.");
  }
  if (headers.includes("DEFAULT")) {
    throw new Error("DEFAULT is a historical outcome, not an input for prediction. Upload a prediction-time file without this column.");
  }

  const required = dashboardConfig.required_columns;
  const missing = required.filter((column) => !headers.includes(column));
  const extra = headers.filter((column) => !required.includes(column));
  if (missing.length || extra.length) {
    const problems = [];
    if (missing.length) problems.push(`Missing required columns: ${missing.join(", ")}.`);
    if (extra.length) problems.push(`Unrecognized columns: ${extra.join(", ")}.`);
    throw new Error(problems.join(" "));
  }
  if (!dataRows.length) throw new Error("The CSV must contain at least one customer row.");
  if (dataRows.length > dashboardConfig.max_customer_rows) {
    throw new Error(`The CSV contains ${numberFormatter.format(dataRows.length)} customer rows; the maximum is ${numberFormatter.format(dashboardConfig.max_customer_rows)}. Split the portfolio into smaller files.`);
  }

  const seenIds = new Set();
  return dataRows.map((values, rowIndex) => {
    const csvRowNumber = rowIndex + 2;
    if (values.length !== headers.length) {
      throw new Error(`CSV row ${csvRowNumber} has ${values.length} values; expected ${headers.length}.`);
    }
    const sourceRow = Object.fromEntries(headers.map((header, index) => [header, values[index]]));
    const customer = {};
    for (const column of required) {
      const value = sourceRow[column];
      if (value === undefined || value.trim() === "") {
        throw new Error(`${column} cannot be blank. Check CSV row ${csvRowNumber}.`);
      }
      customer[column] = parseNumeric(value, column, csvRowNumber);
    }
    if (seenIds.has(customer.ID)) {
      throw new Error(`ID values must be unique. Duplicate ID ${customer.ID} appears in CSV row ${csvRowNumber}.`);
    }
    seenIds.add(customer.ID);
    return customer;
  });
}

function formatCount(value) {
  return numberFormatter.format(value);
}

function formatPercent(value) {
  return percentFormatter.format(value);
}

function formatProfileNumber(value) {
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 1 }).format(value);
}

const PROFILE_MEASURES = [
  { label: "Predicted risk", read: (row) => row.predicted_default_probability, format: formatPercent },
  { label: "Credit limit", read: (row) => row.LIMIT_BAL, format: formatProfileNumber },
  { label: "Age (years)", read: (row) => row.AGE, format: formatProfileNumber },
  {
    label: "Average bill amount",
    read: (row) => meanOfFields(row, ["BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "BILL_AMT4", "BILL_AMT5", "BILL_AMT6"]),
    format: formatProfileNumber,
  },
  {
    label: "Average payment amount",
    read: (row) => meanOfFields(row, ["PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6"]),
    format: formatProfileNumber,
  },
];

function meanOfFields(row, fields) {
  const values = fields.map((field) => row[field]).filter(Number.isFinite);
  if (values.length !== fields.length) return null;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function quantile(sortedValues, fraction) {
  if (!sortedValues.length) return null;
  const position = (sortedValues.length - 1) * fraction;
  const lowerIndex = Math.floor(position);
  const upperIndex = Math.ceil(position);
  const weight = position - lowerIndex;
  return sortedValues[lowerIndex] * (1 - weight) + sortedValues[upperIndex] * weight;
}

function summarizeMeasure(rows, read) {
  const values = rows.map(read).filter(Number.isFinite).sort((left, right) => left - right);
  if (!values.length) return { count: 0, missing: rows.length };
  return {
    count: values.length,
    missing: rows.length - values.length,
    minimum: values[0],
    percentile25: quantile(values, 0.25),
    median: quantile(values, 0.5),
    percentile75: quantile(values, 0.75),
    maximum: values[values.length - 1],
  };
}

function renderSelectionProfile(rows) {
  const groupDefinitions = [
    { label: "Selected for review", selected: true },
    { label: "Not selected", selected: false },
  ];
  const groups = groupDefinitions.map((definition) => {
    const members = rows.filter((row) => row.selected_for_review === definition.selected);
    const group = document.createElement("article");
    group.className = `selection-profile-group${definition.selected ? " is-selected" : ""}`;

    const heading = document.createElement("div");
    heading.className = "selection-profile-group-heading";
    const title = document.createElement("h4");
    title.textContent = definition.label;
    const size = document.createElement("span");
    const share = rows.length ? formatPercent(members.length / rows.length) : "—";
    size.textContent = `${formatCount(members.length)} customers · ${share} of portfolio`;
    heading.append(title, size);
    group.append(heading);

    if (!members.length) {
      const empty = document.createElement("p");
      empty.className = "selection-profile-empty";
      empty.textContent = "No customers fall into this group under the current capacity.";
      group.append(empty);
      return group;
    }

    const list = document.createElement("dl");
    list.className = "selection-profile-measures";
    PROFILE_MEASURES.forEach((measure) => {
      const summary = summarizeMeasure(members, measure.read);
      const item = document.createElement("div");
      item.className = "selection-profile-measure";
      const label = document.createElement("dt");
      label.textContent = measure.label;
      const values = document.createElement("dd");
      if (!summary.count) {
        values.textContent = "No available values";
      } else {
        const median = document.createElement("strong");
        median.textContent = `Median ${measure.format(summary.median)}`;
        const middle = document.createElement("span");
        middle.textContent = `Middle half: ${measure.format(summary.percentile25)}–${measure.format(summary.percentile75)}`;
        const range = document.createElement("span");
        range.textContent = `Range: ${measure.format(summary.minimum)}–${measure.format(summary.maximum)}`;
        const records = document.createElement("span");
        records.textContent = `${formatCount(summary.count)} available · ${formatCount(summary.missing)} missing`;
        values.append(median, middle, range, records);
      }
      item.append(label, values);
      list.append(item);
    });
    group.append(list);
    return group;
  });
  elements.selectionProfileGroups.replaceChildren(...groups);
}

function renderMetricCards(result) {
  const capacity = result.capacity;
  const summary = result.portfolio_summary.probability_summary;
  const metrics = [
    { label: "Customers scored", value: formatCount(result.population_count), help: "Full uploaded portfolio", icon: "▦" },
    { label: "Mean predicted risk", value: formatPercent(summary.mean), help: "Average model estimate", icon: "⌁" },
    { label: "Selected for review", value: formatCount(capacity.selected_count), help: "Under the supplied capacity", icon: "✓" },
    { label: "Unused capacity", value: formatCount(capacity.unused_capacity), help: "After tie-aware selection", icon: "↗" },
  ];

  elements.metrics.replaceChildren(...metrics.map((metric) => {
    const card = document.createElement("article");
    card.className = "metric-card";
    card.innerHTML = `
      <div class="metric-card-top">
        <span class="metric-label">${metric.label}</span>
        <span class="metric-icon" aria-hidden="true">${metric.icon}</span>
      </div>
      <strong class="metric-value">${metric.value}</strong>
      <span class="metric-help">${metric.help}</span>
    `;
    return card;
  }));
}

function renderRiskBands(summary) {
  const bands = summary.risk_bands;
  elements.riskBands.replaceChildren(...bands.map((band) => {
    const row = document.createElement("div");
    row.className = "band-row";
    row.dataset.band = band.label;
    row.setAttribute("role", "listitem");

    const label = document.createElement("span");
    label.className = "band-label";
    label.textContent = band.label;

    const track = document.createElement("span");
    track.className = "band-track";
    track.setAttribute("aria-hidden", "true");
    const fill = document.createElement("span");
    fill.className = "band-fill";
    fill.style.width = `${Math.max(0, Math.min(1, band.portfolio_share)) * 100}%`;
    track.append(fill);

    const value = document.createElement("span");
    value.className = "band-value";
    value.innerHTML = `<strong>${formatCount(band.customer_count)}</strong> <span>· ${formatPercent(band.portfolio_share)}</span>`;
    row.append(label, track, value);
    return row;
  }));
  elements.riskReference.textContent = `${summary.risk_band_reference}. The fixed validation-cohort method is descriptive; these bands are not action thresholds.`;
}

function renderCapacity(result) {
  const capacity = result.capacity;
  const denominator = capacity.target_review_count;
  const utilization = denominator > 0 ? capacity.selected_count / denominator : 0;
  const safeUtilization = Math.max(0, Math.min(1, utilization));
  const percentage = denominator > 0 ? Math.round(safeUtilization * 100) : null;
  const degrees = safeUtilization * 360;

  elements.capacityRing.style.background = `conic-gradient(#438675 0deg ${degrees}deg, #e8efeb ${degrees}deg 360deg)`;
  elements.capacityPercent.textContent = percentage === null ? "—" : `${percentage}%`;

  const items = [
    { label: "Requested", count: capacity.requested_review_count, note: "Analyst capacity" },
    { label: "Selected", count: capacity.selected_count, note: "Entered the queue" },
    { label: "Unused", count: capacity.unused_capacity, note: "Tie-aware remainder" },
  ];
  elements.capacityLegend.replaceChildren(...items.map((item) => {
    const entry = document.createElement("div");
    entry.className = "legend-item";
    const dot = document.createElement("span");
    dot.className = "legend-dot";
    dot.setAttribute("aria-hidden", "true");
    const copy = document.createElement("span");
    copy.className = "legend-copy";
    const strong = document.createElement("strong");
    strong.textContent = `${item.label}: ${formatCount(item.count)}`;
    const note = document.createElement("span");
    note.textContent = item.note;
    copy.append(strong, note);
    entry.append(dot, copy);
    return entry;
  }));

  if (denominator === 0) {
    elements.capacityFootnote.textContent = "No review capacity was requested; no customers were selected.";
  } else if (capacity.unused_capacity > 0) {
    elements.capacityFootnote.textContent = "Some capacity remained unused because the queue keeps equal-score customers together at the selection boundary.";
  } else {
    elements.capacityFootnote.textContent = "The requested target was filled. Equal-score groups are kept together at the selection boundary.";
  }
}

function getRiskBand(record) {
  const score = record.predicted_default_probability;
  return currentResult.portfolio_summary.risk_bands.find((band) =>
    (band.lower_bound_exclusive === null || score > band.lower_bound_exclusive)
    && (band.upper_bound_inclusive === null || score <= band.upper_bound_inclusive)
  )?.label ?? "Unassigned";
}

function resetExploreFilters() {
  elements.customerIdFilter.value = "";
  elements.scoreMinFilter.value = "0";
  elements.scoreMaxFilter.value = "1";
  elements.riskBandFilter.value = "";
  elements.reviewStatusFilter.value = "";
  elements.featureFilter.value = "";
  elements.featureValueControl.replaceChildren();
  elements.featureValueControl.hidden = true;
  elements.filterMessage.textContent = "";
  currentPage = 0;
}

function initializeExploreFields() {
  const fields = dashboardConfig.required_columns.filter((field) => field !== "ID");
  elements.featureFilter.replaceChildren(new Option("No input filter", ""));
  elements.groupByField.replaceChildren(...fields.map((field) => new Option(field, field)));
  elements.featureFilter.append(...fields.map((field) => new Option(field, field)));
  elements.groupByField.value = "SEX";
}

function renderFeatureValueControl() {
  const field = elements.featureFilter.value;
  elements.featureValueControl.replaceChildren();
  if (!field || !currentPortfolio.length) {
    elements.featureValueControl.hidden = true;
    return;
  }
  elements.featureValueControl.hidden = false;
  if (CATEGORICAL_FIELDS.has(field)) {
    const label = document.createElement("label");
    label.className = "filter-control";
    const title = document.createElement("span");
    title.textContent = `${field} value`;
    const select = document.createElement("select");
    select.id = "feature-filter-value";
    select.append(new Option("All values", ""));
    [...new Set(currentPortfolio.map((row) => row[field]))]
      .sort((left, right) => left - right)
      .forEach((value) => select.append(new Option(String(value), String(value))));
    select.addEventListener("change", () => runExploreFilters(true));
    label.append(title, select);
    elements.featureValueControl.append(label);
    return;
  }

  const values = currentPortfolio.map((row) => row[field]);
  const minimum = Math.min(...values);
  const maximum = Math.max(...values);
  const label = document.createElement("span");
  label.textContent = `${field} range`;
  const inputs = document.createElement("div");
  inputs.className = "feature-range-inputs";
  for (const [caption, id, value] of [["Min", "feature-filter-min", minimum], ["Max", "feature-filter-max", maximum]]) {
    const inputLabel = document.createElement("label");
    inputLabel.className = "visually-hidden";
    inputLabel.htmlFor = id;
    inputLabel.textContent = `${field} ${caption.toLowerCase()}`;
    const input = document.createElement("input");
    input.type = "number";
    input.id = id;
    input.step = "any";
    input.value = String(value);
    input.dataset.bound = caption.toLowerCase();
    input.addEventListener("input", () => runExploreFilters(true));
    inputs.append(inputLabel, input);
  }
  elements.featureValueControl.append(label, inputs);
}

function numericQuantile(values, proportion) {
  const sorted = [...values].sort((left, right) => left - right);
  const position = (sorted.length - 1) * proportion;
  const lower = Math.floor(position);
  const fraction = position - lower;
  return sorted[lower + 1] === undefined
    ? sorted[lower]
    : sorted[lower] + fraction * (sorted[lower + 1] - sorted[lower]);
}

function getQuartileBoundaries(field) {
  if (!quartileBoundaryCache.has(field)) {
    const values = currentPortfolio.map((row) => row[field]);
    quartileBoundaryCache.set(field, [
      numericQuantile(values, 0.25),
      numericQuantile(values, 0.5),
      numericQuantile(values, 0.75),
    ]);
  }
  return quartileBoundaryCache.get(field);
}

function getQuartileIndex(value, field) {
  const [first, second, third] = getQuartileBoundaries(field);
  if (value <= first) return 0;
  if (value <= second) return 1;
  if (value <= third) return 2;
  return 3;
}

function getGroupLabel(value, field, index = null) {
  if (CATEGORICAL_FIELDS.has(field)) return String(value);
  const [first, second, third] = getQuartileBoundaries(field);
  const formatBoundary = (boundary) => boundary.toLocaleString(undefined, { maximumSignificantDigits: 7 });
  if (index === 0) return `≤ ${formatBoundary(first)}`;
  if (index === 1) return `${formatBoundary(first)} – ${formatBoundary(second)}`;
  if (index === 2) return `${formatBoundary(second)} – ${formatBoundary(third)}`;
  return `> ${formatBoundary(third)}`;
}

function applyExploreFilters() {
  const idQuery = elements.customerIdFilter.value.trim();
  const minimumScore = elements.scoreMinFilter.value === "" ? 0 : Number(elements.scoreMinFilter.value);
  const maximumScore = elements.scoreMaxFilter.value === "" ? 1 : Number(elements.scoreMaxFilter.value);
  if (minimumScore > maximumScore) {
    elements.filterMessage.textContent = "Minimum predicted risk must not exceed maximum predicted risk.";
    return null;
  }
  elements.filterMessage.textContent = "";
  const band = elements.riskBandFilter.value;
  const reviewStatus = elements.reviewStatusFilter.value;
  const field = elements.featureFilter.value;
  const categoryValue = document.querySelector("#feature-filter-value")?.value ?? "";
  const featureMinimum = document.querySelector("#feature-filter-min")?.value;
  const featureMaximum = document.querySelector("#feature-filter-max")?.value;

  return currentPortfolio.filter((record) => {
    const score = record.predicted_default_probability;
    if (idQuery && !String(record.customer_id).includes(idQuery)) return false;
    if (score < minimumScore || score > maximumScore) return false;
    if (band && getRiskBand(record) !== band) return false;
    if (reviewStatus === "selected" && !record.selected_for_review) return false;
    if (reviewStatus === "not-selected" && record.selected_for_review) return false;
    if (field && CATEGORICAL_FIELDS.has(field) && categoryValue && String(record[field]) !== categoryValue) return false;
    if (field && !CATEGORICAL_FIELDS.has(field)) {
      if (featureMinimum !== undefined && featureMinimum !== "" && record[field] < Number(featureMinimum)) return false;
      if (featureMaximum !== undefined && featureMaximum !== "" && record[field] > Number(featureMaximum)) return false;
    }
    return true;
  });
}

function renderScoreDistribution(rows) {
  const bins = Array.from({ length: 10 }, (_, index) => ({
    lower: index / 10,
    upper: (index + 1) / 10,
    count: 0,
  }));
  rows.forEach((record) => {
    const index = Math.min(9, Math.floor(record.predicted_default_probability * 10));
    bins[index].count += 1;
  });
  const denominator = rows.length;
  elements.scoreDistribution.replaceChildren(...bins.map((bin) => {
    const row = document.createElement("div");
    row.className = "distribution-row";
    row.setAttribute("role", "listitem");
    const label = document.createElement("span");
    label.className = "distribution-label";
    label.textContent = `${Math.round(bin.lower * 100)}–${Math.round(bin.upper * 100)}%`;
    const track = document.createElement("span");
    track.className = "distribution-track";
    track.setAttribute("aria-hidden", "true");
    const fill = document.createElement("span");
    fill.className = "distribution-fill";
    const share = denominator ? bin.count / denominator : 0;
    fill.style.width = `${share * 100}%`;
    track.append(fill);
    const value = document.createElement("span");
    value.className = "distribution-value";
    value.textContent = `${formatCount(bin.count)} · ${formatPercent(share)}`;
    row.append(label, track, value);
    return row;
  }));
}

function renderGroupSummary(rows) {
  const field = elements.groupByField.value;
  if (!rows.length) {
    const emptyRow = document.createElement("tr");
    const message = document.createElement("td");
    message.colSpan = 5;
    message.textContent = "No customers match the current filters.";
    emptyRow.append(message);
    elements.groupSummaryBody.replaceChildren(emptyRow);
    elements.groupTableNote.textContent = "Adjust or reset the filters to compare groups.";
    return;
  }
  const groups = new Map();
  rows.forEach((record) => {
    const groupKey = CATEGORICAL_FIELDS.has(field)
      ? String(record[field])
      : String(getQuartileIndex(record[field], field));
    if (!groups.has(groupKey)) {
      const groupIndex = CATEGORICAL_FIELDS.has(field) ? null : Number(groupKey);
      groups.set(groupKey, { label: getGroupLabel(record[field], field, groupIndex), records: [] });
    }
    groups.get(groupKey).records.push(record);
  });
  const orderedGroups = [...groups.entries()].sort((left, right) => {
    if (CATEGORICAL_FIELDS.has(field)) return Number(left[0]) - Number(right[0]);
    return Number(left[0]) - Number(right[0]);
  });
  elements.groupSummaryBody.replaceChildren(...orderedGroups.map(([, group]) => {
    const { label, records } = group;
    const row = document.createElement("tr");
    const values = [
      label,
      formatCount(records.length),
      formatPercent(rows.length ? records.length / rows.length : 0),
      formatPercent(records.reduce((sum, item) => sum + item.predicted_default_probability, 0) / records.length),
      formatCount(records.filter((item) => item.selected_for_review).length),
    ];
    values.forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    return row;
  }));
  elements.groupTableNote.textContent = CATEGORICAL_FIELDS.has(field)
    ? `Encoded values for ${field} are shown as supplied; group shares use the filtered cohort.`
    : `Quartile boundaries for ${field} are calculated from the full portfolio; shares use the filtered cohort.`;
}

function renderCustomerTable(rows) {
  const pageCount = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  currentPage = Math.min(currentPage, pageCount - 1);
  const start = currentPage * PAGE_SIZE;
  const visibleRows = rows.slice(start, start + PAGE_SIZE);
  const tableRows = visibleRows.map((record) => {
    const row = document.createElement("tr");
    const values = [
      formatCount(record.risk_rank),
      formatCount(record.customer_id),
      formatPercent(record.predicted_default_probability),
      getRiskBand(record),
      record.selected_for_review ? "Selected" : "Not selected",
    ];
    values.forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    return row;
  });
  if (!rows.length) {
    const emptyRow = document.createElement("tr");
    const message = document.createElement("td");
    message.colSpan = 5;
    message.textContent = "No customers match the current filters.";
    emptyRow.append(message);
    tableRows.push(emptyRow);
  }
  elements.customerResultsBody.replaceChildren(...tableRows);
  const first = rows.length ? start + 1 : 0;
  const last = Math.min(start + PAGE_SIZE, rows.length);
  elements.pageCount.textContent = `${formatCount(first)}–${formatCount(last)} of ${formatCount(rows.length)}`;
  elements.pageStatus.textContent = `Page ${currentPage + 1} of ${pageCount}`;
  elements.previousPage.disabled = currentPage === 0;
  elements.nextPage.disabled = currentPage >= pageCount - 1;
}

function runExploreFilters(resetPage = false) {
  if (resetPage) currentPage = 0;
  const rows = applyExploreFilters();
  if (rows === null) return;
  filteredPortfolio = rows;
  elements.exploreCount.textContent = `${formatCount(rows.length)} of ${formatCount(currentPortfolio.length)} customers`;
  renderScoreDistribution(rows);
  renderGroupSummary(rows);
  renderCustomerTable(rows);
}

function renderQueueView(result) {
  const capacity = result.capacity;
  queuePage = 0;
  elements.queuePopulationCount.textContent = `${formatCount(result.population_count)} customers scored`;
  const utilization = capacity.target_review_count > 0
    ? formatPercent(capacity.selected_count / capacity.target_review_count)
    : "—";
  const metrics = [
    { label: "Requested capacity", value: formatCount(capacity.requested_review_count), help: "Analyst-entered limit" },
    { label: "Target count", value: formatCount(capacity.target_review_count), help: "Capped at portfolio size" },
    { label: "Selected for review", value: formatCount(capacity.selected_count), help: `${utilization} of target filled` },
    { label: "Unused capacity", value: formatCount(capacity.unused_capacity), help: "Target minus selected" },
  ];
  elements.queueMetricGrid.replaceChildren(...metrics.map((metric) => {
    const card = document.createElement("article");
    card.className = "metric-card queue-metric-card";
    const label = document.createElement("span");
    label.className = "metric-label";
    label.textContent = metric.label;
    const value = document.createElement("strong");
    value.className = "metric-value";
    value.textContent = metric.value;
    const help = document.createElement("span");
    help.className = "metric-help";
    help.textContent = metric.help;
    card.append(label, value, help);
    return card;
  }));

  const reasonGroups = new Map();
  result.customers.forEach((record) => {
    if (!reasonGroups.has(record.reason_code)) {
      reasonGroups.set(record.reason_code, { reason: record.reason, count: 0 });
    }
    reasonGroups.get(record.reason_code).count += 1;
  });
  elements.queueReasonsBody.replaceChildren(...[...reasonGroups.values()].map((group) => {
    const row = document.createElement("tr");
    const reason = document.createElement("td");
    reason.textContent = group.reason;
    const count = document.createElement("td");
    count.textContent = formatCount(group.count);
    row.append(reason, count);
    return row;
  }));
  renderSelectedQueue(result.customers.filter((record) => record.selected_for_review));
}

function renderSelectedQueue(selectedCustomers) {
  const pageCount = Math.max(1, Math.ceil(selectedCustomers.length / PAGE_SIZE));
  queuePage = Math.min(queuePage, pageCount - 1);
  const start = queuePage * PAGE_SIZE;
  const currentRows = selectedCustomers.slice(start, start + PAGE_SIZE);
  const rows = currentRows.map((record) => {
    const row = document.createElement("tr");
    [
      formatCount(record.risk_rank),
      formatCount(record.customer_id),
      formatPercent(record.predicted_default_probability),
      record.reason,
    ].forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    return row;
  });
  if (!selectedCustomers.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 4;
    cell.textContent = "No customers were selected under this capacity.";
    row.append(cell);
    rows.push(row);
  }
  elements.selectedQueueBody.replaceChildren(...rows);
  const first = selectedCustomers.length ? start + 1 : 0;
  const last = Math.min(start + PAGE_SIZE, selectedCustomers.length);
  elements.queuePageCount.textContent = `${formatCount(first)}–${formatCount(last)} of ${formatCount(selectedCustomers.length)}`;
  elements.queuePageStatus.textContent = `Page ${queuePage + 1} of ${pageCount}`;
  elements.queuePreviousPage.disabled = queuePage === 0;
  elements.queueNextPage.disabled = queuePage >= pageCount - 1;
}

function setActiveView(view) {
  if (view !== "overview" && !currentResult) return;
  activeView = view;
  elements.results.hidden = view !== "overview" || !currentResult;
  elements.exploreView.hidden = view !== "explore" || !currentResult;
  elements.queueView.hidden = view !== "queue" || !currentResult;
  elements.emptyState.hidden = Boolean(currentResult);
  elements.viewLinks.forEach((link) => {
    const active = link.dataset.view === view;
    link.classList.toggle("is-active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  const viewLabels = { overview: "Overview", explore: "Explore portfolio", queue: "Review queue" };
  document.querySelector(".breadcrumb").lastChild.textContent = ` ${viewLabels[view]}`;
}

function renderOverview(result, inputRows) {
  currentResult = result;
  const inputsById = new Map(inputRows.map((row) => [row.ID, row]));
  currentPortfolio = result.customers.map((scoredRow) => ({
    ...inputsById.get(scoredRow.customer_id),
    ...scoredRow,
  }));
  quartileBoundaryCache.clear();
  initializeExploreFields();
  resetExploreFilters();
  renderQueueView(result);
  renderSelectionProfile(currentPortfolio);
  renderMetricCards(result);
  renderRiskBands(result.portfolio_summary);
  renderCapacity(result);
  elements.portfolioCount.textContent = `${formatCount(result.population_count)} customers`;
  elements.analysisMetaText.textContent = `Scored ${new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}`;
  elements.analysisMeta.hidden = false;
  runExploreFilters();
  setActiveView("overview");
  elements.results.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function readSelectedFile() {
  if (!selectedFile) throw new Error("Choose a CSV file before running the analysis.");
  const text = await selectedFile.text();
  return validateCsvRows(parseCsv(text));
}

async function loadDashboardConfig() {
  const response = await fetch("/v1/dashboard-config");
  if (!response.ok) throw new Error("The dashboard couldn’t load its setup details. Refresh and try again.");
  dashboardConfig = await response.json();
  elements.fileHint.textContent = `ID and all 23 predictors · up to ${formatCount(dashboardConfig.max_customer_rows)} customers`;
  elements.capacity.max = String(dashboardConfig.max_customer_rows);
}

async function checkService() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("Portfolio scoring is temporarily unavailable.");
    const health = await response.json();
    if (!health.model_loaded) throw new Error("Portfolio scoring isn’t ready yet. Try again shortly.");
    setServiceStatus(true, "Ready to score portfolios");
  } catch (error) {
    setServiceStatus(false, "Portfolio scoring is temporarily unavailable.");
  }
}

elements.file.addEventListener("change", () => {
  selectedFile = elements.file.files?.[0] ?? null;
  clearMessage();
  if (selectedFile) {
    elements.fileName.textContent = selectedFile.name;
    elements.fileHint.textContent = `${(selectedFile.size / 1024).toFixed(0)} KB · ready to validate`;
    elements.fileName.title = selectedFile.name;
  } else {
    elements.fileName.textContent = "Choose a CSV file";
  }
});

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearMessage();
  elements.runButton.disabled = true;
  elements.runButton.querySelector("span:first-child").textContent = "Scoring portfolio…";

  try {
    if (!dashboardConfig) await loadDashboardConfig();
    const customers = await readSelectedFile();
    if (elements.capacity.value.trim() === "") {
      throw new Error("Enter a review capacity.");
    }
    const capacity = Number(elements.capacity.value);
    if (!Number.isSafeInteger(capacity) || capacity < 0) {
      throw new Error("Review capacity must be a non-negative whole number.");
    }

    const response = await fetch("/v1/review-queue", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ customers, max_review_count: capacity }),
    });
    const payload = await response.json();
    if (!response.ok) {
      const details = payload?.error?.details?.filter(Boolean).join(" ");
      throw new Error(details || payload?.error?.message || "The scoring request failed.");
    }

    renderOverview(payload, customers);
    setServiceStatus(true, "Ready to score portfolios");
    showMessage(`Analysis complete for ${formatCount(payload.population_count)} customers.`, "success");
  } catch (error) {
    const message = error instanceof TypeError
      ? "Portfolio scoring is temporarily unavailable. Check your connection and try again."
      : error.message || "The portfolio could not be scored.";
    showMessage(message);
  } finally {
    elements.runButton.disabled = false;
    elements.runButton.querySelector("span:first-child").textContent = "Run analysis";
  }
});

elements.healthCheck.addEventListener("click", checkService);

elements.viewLinks.forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    setActiveView(link.dataset.view);
    if (currentResult) window.location.hash = link.dataset.view;
  });
});

[
  elements.customerIdFilter,
  elements.scoreMinFilter,
  elements.scoreMaxFilter,
  elements.riskBandFilter,
  elements.reviewStatusFilter,
].forEach((control) => control.addEventListener("input", () => runExploreFilters(true)));
[
  elements.riskBandFilter,
  elements.reviewStatusFilter,
].forEach((control) => control.addEventListener("change", () => runExploreFilters(true)));
elements.featureFilter.addEventListener("change", () => {
  renderFeatureValueControl();
  runExploreFilters(true);
});
elements.groupByField.addEventListener("change", () => runExploreFilters(true));
elements.resetFilters.addEventListener("click", () => {
  resetExploreFilters();
  runExploreFilters(true);
});
elements.previousPage.addEventListener("click", () => {
  currentPage = Math.max(0, currentPage - 1);
  renderCustomerTable(filteredPortfolio);
});
elements.nextPage.addEventListener("click", () => {
  currentPage += 1;
  renderCustomerTable(filteredPortfolio);
});
elements.queuePreviousPage.addEventListener("click", () => {
  queuePage = Math.max(0, queuePage - 1);
  renderSelectedQueue(currentResult.customers.filter((record) => record.selected_for_review));
});
elements.queueNextPage.addEventListener("click", () => {
  queuePage += 1;
  renderSelectedQueue(currentResult.customers.filter((record) => record.selected_for_review));
});

loadDashboardConfig()
  .then(checkService)
  .catch(() => setServiceStatus(false, "Portfolio scoring is temporarily unavailable."));
```

---

<a id="step-9-9"></a>
## Step 9.9

# Phase 9.9 — Feature and Repayment-Pattern Insights

## Decision

The user chose **Option B: descriptive portfolio patterns plus global model
importance**. The new Feature insights view deliberately separates two sources
of information: what is present in the uploaded portfolio, and what the model
used on its validation cohort. It does not claim that these patterns explain
causes or individual predictions.

## What changed

- Added **Feature insights** as a fourth dashboard view, available after a
  portfolio has been scored.
- Added six monthly repayment-status distributions, showing the share and
  count in every observed input code. Values remain codes; the dashboard does
  not invent “on time” or “late” labels.
- Added separate monthly bill-statement and previous-payment tables showing
  median, 25th–75th percentile interval, range, available count, and missing
  count across the uploaded portfolio.
- Used the month definitions in the project's data dictionary, April through
  September 2005. The UI names each observed amount as a statement or previous
  payment amount, and does not label it as principal or infer a trend.
- Added a top-ten global permutation-importance chart using the Phase 6
  validation reference values. It shows mean Average Precision change and
  across-repeat standard deviation, with method and evaluation reference
  visible beside the chart.
- Added the reviewed importance snapshot to the dashboard configuration
  response. It is served as versioned model metadata and is not recomputed for
  each uploaded portfolio.
- Added nearby notes explaining that observed portfolio values and validation
  importance describe different evidence, that feature importance is not
  causal, and that engineered features can share information with their
  source columns.

## Data definitions and denominators

All observed-pattern counts and numeric summaries use the full uploaded
portfolio. Explore portfolio filters do not change these views. `PAY_6` through
`PAY_0` are mapped chronologically from April through September 2005 using
[`data_dictionary.md`](data_dictionary.md). The omitted `PAY_1` name is part
of the source dataset's column scheme; the project does not create a value for
it. The dashboard displays each raw status code and its count/share without
assigning a category meaning.

`BILL_AMT6` through `BILL_AMT1` are statement amounts from April through
September 2005. `PAY_AMT6` through `PAY_AMT1` are previous payment amounts for
the same months. The summary for each month uses the rows with finite values
in that field. The median, quartiles, minimum, and maximum use the same
linear-interpolated quantile method described in Step 9.8. The count is the
number of usable rows; missing count is the portfolio size minus that number.
CSV validation currently requires these values, so missing counts are
normally zero.

The model reference is the documented Phase 6 global permutation importance
for the locked HistGradientBoosting model. The metric is validation
Average Precision, the results use ten shuffles and random seed 42, and the
chart lists the ten features with the largest documented mean changes. A
positive mean indicates Average Precision fell when that feature was
shuffled. The displayed standard deviation is across those repeated shuffles;
it is not a confidence interval. These values describe the model's validation
performance and do not change with an uploaded portfolio.

## Step-by-step code walkthrough

### 1. Serve the reviewed model reference (`global_importance_reference.py`)

The Phase 6 report contains the full top-ten values used here: feature name,
plain description, mean score change, and standard deviation. The new module
stores these values with their method, metric, validation reference, repeat
count, and random seed. Its comments identify the snapshot as reviewed model
metadata and say to update it only with a reviewed model version and its
validation report. This avoids fitting or evaluating a model each time the
dashboard opens or an analyst uploads data.

### 2. Validate the configuration shape (`schemas.py` and `routes.py`)

The dashboard configuration now contains a typed `ModelFeatureImportanceReference`
with typed feature rows. The existing configuration route returns this
reference alongside the upload row limit and required columns. The model
logic, queue endpoint, and uploaded portfolio response are unchanged.

The browser still calls the same configuration fetch function. The page copy
does not expose route names or API implementation details; it describes the
information as a model validation reference.

### 3. Add the Feature insights view (`index.html`)

The sidebar has a new **Feature insights** item. Its view has two labeled
sections:

1. **Observed in this portfolio** shows the monthly repayment-status code
   distribution and the monthly statement/payment summaries.
2. **Model validation reference** shows global permutation importance.

This separation prevents the analyst from mistaking a portfolio distribution
for a model explanation or assuming that validation results were recomputed
from their uploaded customers. Every chart includes the denominator or method
near the visual.

### 4. Summarize uploaded fields (`MONTHLY_FEATURES` and render helpers in `app.js`)

`MONTHLY_FEATURES` is the single month-to-column mapping, ordered from April
to September 2005 and checked against the data dictionary. The repayment
renderer counts each observed status code for each month, calculates shares
using the available customers in that month, and draws a consistently colored
stacked bar. It also renders the code, count, and share as text, and puts the
full summary into the accessible label for each bar.

The amount renderer reuses Step 9.8's finite-value and quantile calculation
for each monthly field. Each row reports median, interquartile interval,
minimum–maximum range, and available/missing records. It uses only DOM
elements and `textContent`; no input value is executed or inserted as HTML.

### 5. Show global permutation importance (`renderModelImportance` in `app.js`)

`renderOverview` merges the uploaded input rows with their completed score and
selection result, then calls `renderFeatureInsights` with the configuration's
fixed model reference. The importance renderer keeps the documented order,
draws bars around a zero baseline, prints the mean value and the standard
deviation across shuffles, and displays the evaluation cohort, metric, repeat
count, and seed. The chart scale is relative to the largest absolute mean in
the displayed top ten; numeric values remain visible so the bar is not the
only source of information.

The accompanying note explains that shuffling evaluates model performance,
not causal effect. It also warns against adding importances for engineered
features and their source columns, since they may share information.

### 6. Connect navigation and responsive styling (`setActiveView` and `styles.css`)

The new view follows the existing navigation pattern and appears only after a
scored portfolio exists. On smaller screens, the observed-data cards stack;
the monthly tables scroll horizontally; and importance descriptions and
values wrap into a compact layout. The existing calm light palette is reused.

## Interpretation limits

The six-month distribution is historical input data, not a future trajectory.
The status codes are not translated into payment outcomes. The monthly amount
summaries are descriptive and do not show what causes default.

Global permutation importance describes how the locked model's validation
Average Precision changed when features were shuffled. It does not show the
direction of a feature's effect, prove causation, provide an individual
explanation, or predict the effect of an intervention. Correlated raw and
engineered features may divide or share importance. The top-ten snapshot is
specific to the Phase 6 validation reference and should be refreshed only
alongside a reviewed model/version update.

## Complete changed source

The following are the complete contents of all source files changed for this
step, including frontend, response-schema, route, and reference-data code.

### `src/propensity_prediction/explainability/global_importance_reference.py`

```python
"""Versioned Phase 6 global feature-importance reference for the dashboard."""

from __future__ import annotations


# These values are the documented results of the locked Phase 6 model on its
# validation cohort. They are a reference explanation, not recomputed for an
# uploaded portfolio. Update this snapshot only alongside a reviewed model
# version and its validation report.
GLOBAL_FEATURE_IMPORTANCE_REFERENCE = {
    "method": "permutation_importance",
    "scoring_metric": "average_precision",
    "evaluation_reference": (
        "Phase 6 validation cohort · locked HistGradientBoosting model"
    ),
    "repeats": 10,
    "random_state": 42,
    "features": [
        {
            "feature": "PAY_0",
            "description": "Repayment status code, September 2005",
            "importance_mean": 0.087000,
            "importance_std": 0.006401,
        },
        {
            "feature": "PAY_STATUS_MAX",
            "description": "Maximum repayment status code across April–September 2005",
            "importance_mean": 0.084868,
            "importance_std": 0.003954,
        },
        {
            "feature": "BILL_TO_LIMIT_MEAN",
            "description": "Mean bill amount relative to credit limit across six records",
            "importance_mean": 0.007153,
            "importance_std": 0.002057,
        },
        {
            "feature": "BILL_AMT_STD",
            "description": "Variation in bill statement amounts across six records",
            "importance_mean": 0.007094,
            "importance_std": 0.001184,
        },
        {
            "feature": "PAYMENT_TO_BILL_MAX",
            "description": "Maximum payment-to-bill ratio across six records",
            "importance_mean": 0.004540,
            "importance_std": 0.005140,
        },
        {
            "feature": "BILL_AMT1",
            "description": "Bill statement amount, September 2005",
            "importance_mean": 0.004103,
            "importance_std": 0.002471,
        },
        {
            "feature": "PAY_AMT3",
            "description": "Previous payment amount, July 2005",
            "importance_mean": 0.003913,
            "importance_std": 0.001937,
        },
        {
            "feature": "PAY_STATUS_TREND",
            "description": "Linear trend in repayment status codes across six records",
            "importance_mean": 0.003873,
            "importance_std": 0.001802,
        },
        {
            "feature": "PAY_AMT_MEAN",
            "description": "Mean previous payment amount across six records",
            "importance_mean": 0.003148,
            "importance_std": 0.002584,
        },
        {
            "feature": "PAY_3",
            "description": "Repayment status code, July 2005",
            "importance_mean": 0.002465,
            "importance_std": 0.003632,
        },
    ],
}
```

### `src/propensity_prediction/api/schemas.py`

```python
"""Pydantic request and response models for the public API contract."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt

from propensity_prediction.limits import MAX_CUSTOMER_ROWS


class CustomerInput(BaseModel):
    """One customer row: identifier plus the 23 canonical predictors."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        allow_inf_nan=False,
    )

    ID: StrictInt
    LIMIT_BAL: Annotated[float, Field(ge=0)]
    AGE: float
    BILL_AMT1: float
    BILL_AMT2: float
    BILL_AMT3: float
    BILL_AMT4: float
    BILL_AMT5: float
    BILL_AMT6: float
    PAY_AMT1: Annotated[float, Field(ge=0)]
    PAY_AMT2: Annotated[float, Field(ge=0)]
    PAY_AMT3: Annotated[float, Field(ge=0)]
    PAY_AMT4: Annotated[float, Field(ge=0)]
    PAY_AMT5: Annotated[float, Field(ge=0)]
    PAY_AMT6: Annotated[float, Field(ge=0)]
    SEX: Annotated[StrictInt, Field(ge=1, le=2)]
    EDUCATION: Annotated[StrictInt, Field(ge=0, le=4)]
    MARRIAGE: Annotated[StrictInt, Field(ge=0, le=3)]
    PAY_0: StrictInt
    PAY_2: StrictInt
    PAY_3: StrictInt
    PAY_4: StrictInt
    PAY_5: StrictInt
    PAY_6: StrictInt


class ReviewQueueRequest(BaseModel):
    """Batch request to score a portfolio and apply a review-count limit."""

    model_config = ConfigDict(extra="forbid", strict=True)

    customers: Annotated[
        list[CustomerInput], Field(min_length=1, max_length=MAX_CUSTOMER_ROWS)
    ]
    max_review_count: Annotated[StrictInt, Field(ge=0)]


class CapacitySummary(BaseModel):
    requested_review_count: int
    target_review_count: int
    selected_count: int
    unused_capacity: int


class CustomerQueueItem(BaseModel):
    customer_id: int
    predicted_default_probability: float = Field(ge=0, le=1)
    risk_rank: int = Field(ge=1)
    selected_for_review: bool
    reason_code: str
    reason: str


class ProbabilitySummary(BaseModel):
    minimum: float = Field(ge=0, le=1)
    percentile_25: float = Field(ge=0, le=1)
    median: float = Field(ge=0, le=1)
    mean: float = Field(ge=0, le=1)
    percentile_75: float = Field(ge=0, le=1)
    maximum: float = Field(ge=0, le=1)


class RiskBandSummary(BaseModel):
    label: str
    customer_count: int = Field(ge=0)
    portfolio_share: float = Field(ge=0, le=1)
    lower_bound_exclusive: float | None = Field(default=None, ge=0, le=1)
    upper_bound_inclusive: float | None = Field(default=None, ge=0, le=1)


class PortfolioSummary(BaseModel):
    probability_summary: ProbabilitySummary
    risk_band_method: Literal["fixed_validation_cohort_quantiles"]
    risk_band_reference: str
    risk_bands: list[RiskBandSummary]


class ReviewQueueResponse(BaseModel):
    population_count: int
    capacity: CapacitySummary
    portfolio_summary: PortfolioSummary
    customers: list[CustomerQueueItem]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


class ModelFeatureImportanceItem(BaseModel):
    feature: str
    description: str
    importance_mean: float
    importance_std: float = Field(ge=0)


class ModelFeatureImportanceReference(BaseModel):
    method: Literal["permutation_importance"]
    scoring_metric: Literal["average_precision"]
    evaluation_reference: str
    repeats: int = Field(ge=1)
    random_state: int
    features: list[ModelFeatureImportanceItem]


class DashboardConfigResponse(BaseModel):
    max_customer_rows: int = Field(ge=1)
    required_columns: list[str]
    model_feature_importance: ModelFeatureImportanceReference


class APIErrorBody(BaseModel):
    code: str
    message: str
    details: list[str]


class APIErrorResponse(BaseModel):
    error: APIErrorBody
```

### `src/propensity_prediction/api/routes.py`

```python
"""HTTP routes for readiness and review-queue requests."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from propensity_prediction.api.schemas import (
    APIErrorResponse,
    CustomerInput,
    DashboardConfigResponse,
    HealthResponse,
    ReviewQueueRequest,
    ReviewQueueResponse,
)
from propensity_prediction.api.service import ReviewQueueService
from propensity_prediction.explainability.global_importance_reference import (
    GLOBAL_FEATURE_IMPORTANCE_REFERENCE,
)
from propensity_prediction.limits import MAX_CUSTOMER_ROWS


router = APIRouter()


def get_review_queue_service(request: Request) -> ReviewQueueService:
    return request.app.state.review_queue_service


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    repository = request.app.state.model_repository
    return HealthResponse(
        status="ok" if repository.is_loaded else "degraded",
        model_loaded=repository.is_loaded,
    )


@router.get("/v1/dashboard-config", response_model=DashboardConfigResponse)
def dashboard_config() -> DashboardConfigResponse:
    """Expose upload rules so the browser uses the API's schema and row cap."""
    return DashboardConfigResponse(
        max_customer_rows=MAX_CUSTOMER_ROWS,
        required_columns=list(CustomerInput.model_fields),
        model_feature_importance=GLOBAL_FEATURE_IMPORTANCE_REFERENCE,
    )


@router.post(
    "/v1/review-queue",
    response_model=ReviewQueueResponse,
    responses={
        400: {"model": APIErrorResponse},
        422: {"model": APIErrorResponse},
        503: {"model": APIErrorResponse},
    },
)
def create_review_queue(
    payload: ReviewQueueRequest,
    service: ReviewQueueService = Depends(get_review_queue_service),
) -> dict:
    return service.build_queue(payload)
```

### `src/propensity_prediction/dashboard/static/index.html`

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#f4f7f4" />
    <meta
      name="description"
      content="Understand a scored customer portfolio and its review capacity."
    />
    <title>Portfolio overview | Credit risk review</title>
    <link rel="stylesheet" href="/styles.css" />
    <script src="/app.js" defer></script>
  </head>
  <body>
    <div class="app-shell">
      <aside class="sidebar" aria-label="Dashboard navigation">
        <a class="brand" href="/" aria-label="Portfolio review home">
          <span class="brand-mark" aria-hidden="true">P</span>
          <span class="brand-copy">
            <strong>Portfolio</strong>
            <span>Risk review</span>
          </span>
        </a>

        <p class="nav-label">WORKSPACE</p>
        <nav class="primary-nav" aria-label="Primary">
          <a class="nav-link is-active" href="#overview" data-view="overview" aria-current="page">
            <span class="nav-icon" aria-hidden="true">▦</span>
            <span>Overview</span>
          </a>
          <a class="nav-link" href="#explore" data-view="explore">
            <span class="nav-icon" aria-hidden="true">⌕</span>
            <span>Explore portfolio</span>
          </a>
          <a class="nav-link" href="#queue" data-view="queue">
            <span class="nav-icon" aria-hidden="true">≡</span>
            <span>Review queue</span>
          </a>
          <a class="nav-link" href="#feature-insights" data-view="feature-insights">
            <span class="nav-icon" aria-hidden="true">⌁</span>
            <span>Feature insights</span>
          </a>
        </nav>

        <div class="sidebar-bottom">
          <div class="sidebar-note">
            <span class="note-icon" aria-hidden="true">i</span>
            <p>Predicted risk helps prioritize review. It is not an outcome or an action recommendation.</p>
          </div>
          <span class="service-status" id="service-status" role="status">
            <span class="status-dot" aria-hidden="true"></span>
            Checking portfolio scoring
          </span>
        </div>
      </aside>

      <main class="main-content" id="overview">
        <header class="topbar">
          <div class="breadcrumb">Workspace <span aria-hidden="true">/</span> Overview</div>
          <div class="topbar-actions">
            <button class="text-button" id="health-check" type="button">Check status</button>
            <span class="avatar" aria-hidden="true">AR</span>
          </div>
        </header>

        <section class="page-heading" aria-labelledby="page-title">
          <div>
            <p class="eyebrow">PORTFOLIO INSIGHTS</p>
            <h1 id="page-title">Portfolio overview</h1>
            <p class="page-description">A clear view of predicted risk and review capacity for your customer portfolio.</p>
          </div>
          <div class="analysis-meta" id="analysis-meta" hidden>
            <span class="meta-dot" aria-hidden="true"></span>
            <span id="analysis-meta-text">Analysis complete</span>
          </div>
        </section>

        <section class="analysis-panel" aria-labelledby="analysis-title">
          <div class="analysis-panel-copy">
            <span class="step-badge">NEW ANALYSIS</span>
            <h2 id="analysis-title">Start with a customer portfolio</h2>
            <p>Upload a prediction-time CSV, set your review capacity, and score the full portfolio.</p>
          </div>
          <form id="analysis-form" class="analysis-form">
            <label class="file-drop" for="portfolio-file">
              <span class="upload-icon" aria-hidden="true">↑</span>
              <span class="file-drop-copy">
                <strong id="file-name">Choose a CSV file</strong>
                <span id="file-hint">ID and all 23 predictors · up to 30,000 customers</span>
              </span>
              <span class="browse-button">Browse files</span>
            </label>
            <input id="portfolio-file" class="visually-hidden" type="file" accept=".csv,text/csv" />
            <div class="form-actions">
              <label class="capacity-field" for="review-capacity">
                <span>Review capacity</span>
                <span class="capacity-input-wrap">
                  <input id="review-capacity" type="number" min="0" step="1" value="10" inputmode="numeric" />
                  <span>customers</span>
                </span>
              </label>
              <button class="primary-button" id="run-analysis" type="submit">
                <span>Run analysis</span><span aria-hidden="true">→</span>
              </button>
            </div>
            <p class="capacity-refresh-note">Changing capacity takes effect when you run the analysis; the current results stay in place until then.</p>
            <p class="form-message" id="form-message" role="alert" hidden></p>
          </form>
        </section>

        <section class="results-section" id="results-section" aria-labelledby="results-title" hidden>
          <div class="section-heading">
            <div>
              <p class="eyebrow">AT A GLANCE</p>
              <h2 id="results-title">Portfolio snapshot</h2>
              <p class="section-description">Summary of model estimates for the full uploaded portfolio.</p>
            </div>
            <span class="portfolio-count" id="portfolio-count"></span>
          </div>

          <div class="metric-grid" id="metric-grid" aria-label="Portfolio summary metrics"></div>

          <div class="insight-grid">
            <article class="card band-card" aria-labelledby="bands-title">
              <div class="card-heading">
                <div>
                  <h3 id="bands-title">Predicted risk bands</h3>
                  <p>How customers are distributed across the fixed reference bands.</p>
                </div>
                <span class="chart-mark" aria-hidden="true">▥</span>
              </div>
              <div class="band-list" id="risk-band-chart" role="list"></div>
              <details class="chart-note">
                <summary>How to read these bands</summary>
                <p id="risk-band-reference"></p>
                <p>These bands describe relative predicted risk. They are not action thresholds and do not change queue selection.</p>
              </details>
            </article>

            <article class="card capacity-card" aria-labelledby="capacity-title">
              <div class="card-heading">
                <div>
                  <h3 id="capacity-title">Review capacity</h3>
                  <p>How the requested capacity translated into the queue.</p>
                </div>
                <span class="chart-mark capacity-mark" aria-hidden="true">◎</span>
              </div>
              <div class="capacity-visual">
                <div class="capacity-ring" id="capacity-ring" aria-label="Capacity utilization">
                  <div class="ring-center">
                    <strong id="capacity-percent">0%</strong>
                    <span>of target selected</span>
                  </div>
                </div>
                <div class="capacity-legend" id="capacity-legend"></div>
              </div>
              <div class="capacity-footnote" id="capacity-footnote"></div>
            </article>
          </div>

          <div class="interpretation-note">
            <span class="note-icon" aria-hidden="true">i</span>
            <p><strong>Interpretation:</strong> Predicted probabilities summarize model estimates, not observed outcomes or expected losses. Portfolio patterns are descriptive and do not show that an intervention will change outcomes.</p>
          </div>
        </section>

        <section class="explore-view" id="explore-view" aria-labelledby="explore-title" hidden>
          <div class="section-heading explore-heading">
            <div>
              <p class="eyebrow">COHORT EXPLORATION</p>
              <h2 id="explore-title">Explore portfolio</h2>
              <p class="section-description">Filter scored customers and compare descriptive groups.</p>
            </div>
            <span class="portfolio-count" id="explore-count">0 of 0 customers</span>
          </div>

          <section class="card filters-card" aria-labelledby="filters-title">
            <div class="card-heading filter-heading">
              <div>
                <h3 id="filters-title">Find a cohort</h3>
                <p>Every filter applies to the full scored portfolio. Counts below show the filtered denominator.</p>
              </div>
              <button class="text-button" id="reset-filters" type="button">Reset filters</button>
            </div>
            <div class="filter-grid">
              <label class="filter-control">
                <span>Customer ID</span>
                <input id="filter-customer-id" type="search" inputmode="numeric" placeholder="Search ID" />
              </label>
              <label class="filter-control">
                <span>Minimum predicted risk</span>
                <input id="filter-score-min" type="number" min="0" max="1" step="0.01" value="0" />
              </label>
              <label class="filter-control">
                <span>Maximum predicted risk</span>
                <input id="filter-score-max" type="number" min="0" max="1" step="0.01" value="1" />
              </label>
              <label class="filter-control">
                <span>Reference risk band</span>
                <select id="filter-risk-band">
                  <option value="">All bands</option>
                  <option>Lower</option><option>Moderate</option><option>Elevated</option><option>Highest</option>
                </select>
              </label>
              <label class="filter-control">
                <span>Review status</span>
                <select id="filter-review-status">
                  <option value="">All customers</option>
                  <option value="selected">Selected for review</option>
                  <option value="not-selected">Not selected</option>
                </select>
              </label>
              <label class="filter-control">
                <span>Filter by input field</span>
                <select id="filter-feature">
                  <option value="">No input filter</option>
                </select>
              </label>
              <div class="filter-control feature-value-control" id="feature-value-control" hidden></div>
            </div>
            <p class="filter-message" id="filter-message" role="status"></p>
          </section>

          <div class="explore-summary-grid">
            <article class="card distribution-card">
              <div class="card-heading">
                <div><h3>Predicted-risk distribution</h3><p>Fixed 10 percentage-point bins; shares use the filtered cohort.</p></div>
              </div>
              <div class="score-distribution" id="score-distribution" role="list" aria-label="Predicted-risk distribution"></div>
            </article>
            <article class="card group-card">
              <div class="card-heading group-heading">
                <div><h3>Compare groups</h3><p>Descriptive summaries for the filtered cohort.</p></div>
                <label class="group-field"><span>Group by</span><select id="group-by-field"></select></label>
              </div>
              <div class="table-scroll">
                <table class="group-table">
                  <thead><tr><th scope="col">Group</th><th scope="col">Customers</th><th scope="col">Share</th><th scope="col">Mean risk</th><th scope="col">Selected</th></tr></thead>
                  <tbody id="group-summary-body"></tbody>
                </table>
              </div>
              <p class="table-note" id="group-table-note">For numeric fields, groups use quartile boundaries from the full portfolio.</p>
            </article>
          </div>

          <section class="card customer-results-card" aria-labelledby="customer-results-title">
            <div class="card-heading">
              <div><h3 id="customer-results-title">Matching customers</h3><p>Customers are ordered from highest to lowest predicted risk. The table shows a page at a time.</p></div>
              <span class="portfolio-count" id="page-count">0–0 of 0</span>
            </div>
            <div class="table-scroll">
              <table class="customer-table">
                <thead><tr><th scope="col">Rank</th><th scope="col">Customer ID</th><th scope="col">Predicted risk</th><th scope="col">Risk band</th><th scope="col">Review status</th></tr></thead>
                <tbody id="customer-results-body"></tbody>
              </table>
            </div>
            <div class="pagination-controls">
              <span id="page-status">Page 1 of 1</span>
              <div><button class="secondary-button" id="previous-page" type="button" disabled>Previous</button><button class="secondary-button" id="next-page" type="button" disabled>Next</button></div>
            </div>
          </section>

          <div class="interpretation-note">
            <span class="note-icon" aria-hidden="true">i</span>
            <p><strong>Interpretation:</strong> Filtered groups describe this uploaded portfolio. They do not establish causes, treatment effects, or fairness conclusions. Encoded input values are shown as supplied; category codes are not given inferred labels.</p>
          </div>
        </section>

        <section class="queue-view" id="queue-view" aria-labelledby="queue-title" hidden>
          <div class="section-heading queue-heading">
            <div>
              <p class="eyebrow">CAPACITY DECISION</p>
              <h2 id="queue-title">Review queue</h2>
              <p class="section-description">How your review capacity shaped the ranked customer list.</p>
            </div>
            <span class="portfolio-count" id="queue-population-count"></span>
          </div>

          <div class="queue-metric-grid" id="queue-metric-grid" aria-label="Queue capacity summary"></div>

          <div class="queue-explanation-grid">
            <article class="card queue-policy-card">
              <div class="card-heading">
                <div><h3>How selection works</h3><p>A consistent selection rule determines who enters the review list.</p></div>
                <span class="chart-mark capacity-mark" aria-hidden="true">↕</span>
              </div>
              <ol class="queue-policy-list">
                <li><strong>Rank by predicted risk.</strong><span>Customers are ordered from highest to lowest predicted default probability. Equal scores receive the same rank, so later ranks account for all customers ahead.</span></li>
                <li><strong>Keep equal scores together.</strong><span>Customers with the same risk score enter the review list together when the group fits within your capacity.</span></li>
                <li><strong>Stop at a boundary tie.</strong><span>If the next tied group would exceed the remaining target, that whole group and all lower-scoring groups are left out.</span></li>
              </ol>
              <div class="queue-refresh-note"><strong>To change capacity:</strong> edit Review capacity above and click Run analysis. This queue shows the result from the last completed run.</div>
            </article>

            <article class="card queue-outcomes-card">
              <div class="card-heading">
                <div><h3>Why customers were selected or left out</h3><p>These totals explain why customers entered the review list or remained outside it.</p></div>
              </div>
              <div class="table-scroll">
                <table class="group-table">
                  <thead><tr><th scope="col">Queue outcome</th><th scope="col">Customers</th></tr></thead>
                  <tbody id="queue-reasons-body"></tbody>
                </table>
              </div>
              <p class="table-note">Unused capacity can occur when a full tied score group cannot fit. The queue never splits that group or exceeds its target.</p>
            </article>
          </div>

          <section class="card selection-profile-card" aria-labelledby="selection-profile-title">
            <div class="card-heading">
              <div>
                <h3 id="selection-profile-title">Selected and not selected</h3>
                <p>Compare customer profiles under the current review capacity.</p>
              </div>
              <span class="chart-mark" aria-hidden="true">↔</span>
            </div>
            <p class="selection-profile-context">Summaries use the full uploaded portfolio, regardless of filters in Explore portfolio. Each measure shows the median, middle half of values, full range, and available and missing record counts.</p>
            <div class="selection-profile-groups" id="selection-profile-groups" aria-live="polite"></div>
            <p class="table-note">Average bill and payment amounts are calculated per customer across the six supplied monthly fields. Small groups are shown with their exact count; individual records can have more influence in a small group. These descriptive differences do not show causes, outcomes, or intervention effects.</p>
          </section>

          <section class="card selected-queue-card" aria-labelledby="selected-queue-title">
            <div class="card-heading">
              <div><h3 id="selected-queue-title">Selected customers</h3><p>Customers are listed from highest to lowest predicted risk.</p></div>
              <span class="portfolio-count" id="queue-page-count">0–0 of 0</span>
            </div>
            <div class="table-scroll">
              <table class="customer-table">
                <thead><tr><th scope="col">Rank</th><th scope="col">Customer ID</th><th scope="col">Predicted risk</th><th scope="col">Selection reason</th></tr></thead>
                <tbody id="selected-queue-body"></tbody>
              </table>
            </div>
            <div class="pagination-controls">
              <span id="queue-page-status">Page 1 of 1</span>
              <div><button class="secondary-button" id="queue-previous-page" type="button" disabled>Previous</button><button class="secondary-button" id="queue-next-page" type="button" disabled>Next</button></div>
            </div>
          </section>

          <div class="interpretation-note">
            <span class="note-icon" aria-hidden="true">i</span>
            <p><strong>Interpretation:</strong> This view explains a model-ranked review policy under the requested capacity. It does not recommend an intervention or estimate the effect of reviewing a customer.</p>
          </div>
        </section>

        <section class="feature-insights-view" id="feature-insights-view" aria-labelledby="feature-insights-title" hidden>
          <div class="section-heading feature-insights-heading">
            <div>
              <p class="eyebrow">PORTFOLIO PATTERNS</p>
              <h2 id="feature-insights-title">Feature insights</h2>
              <p class="section-description">What appears in this uploaded portfolio, alongside patterns the model used on validation data.</p>
            </div>
            <span class="portfolio-count" id="feature-insights-count"></span>
          </div>

          <section class="feature-insight-section" aria-labelledby="observed-patterns-title">
            <div class="feature-insight-section-heading">
              <span class="insight-source-badge observed-badge">OBSERVED IN THIS PORTFOLIO</span>
              <h3 id="observed-patterns-title">Historical repayment and amount patterns</h3>
              <p>Summaries describe the uploaded rows. They do not represent future behavior or outcomes.</p>
            </div>
            <div class="observed-pattern-grid">
              <article class="card repayment-pattern-card">
                <div class="card-heading">
                  <div><h3>Repayment status codes by month</h3><p>Share of customers in each input code, across the full portfolio.</p></div>
                </div>
                <div class="repayment-status-chart" id="repayment-status-chart" role="list" aria-label="Repayment status code distribution by month"></div>
                <p class="table-note">Codes are shown as supplied. Their integer values are not relabeled as payment outcomes here.</p>
              </article>

              <article class="card monthly-amount-card">
                <div class="card-heading">
                  <div><h3>Bill statement amounts</h3><p>Monthly distribution across all uploaded customers.</p></div>
                </div>
                <div class="table-scroll">
                  <table class="group-table monthly-profile-table">
                    <thead><tr><th scope="col">Month</th><th scope="col">Median</th><th scope="col">Middle half</th><th scope="col">Range</th><th scope="col">Records</th></tr></thead>
                    <tbody id="monthly-bill-summary"></tbody>
                  </table>
                </div>
              </article>

              <article class="card monthly-amount-card">
                <div class="card-heading">
                  <div><h3>Previous payment amounts</h3><p>Monthly distribution across all uploaded customers.</p></div>
                </div>
                <div class="table-scroll">
                  <table class="group-table monthly-profile-table">
                    <thead><tr><th scope="col">Month</th><th scope="col">Median</th><th scope="col">Middle half</th><th scope="col">Range</th><th scope="col">Records</th></tr></thead>
                    <tbody id="monthly-payment-summary"></tbody>
                  </table>
                </div>
              </article>
            </div>
          </section>

          <section class="feature-insight-section model-insight-section" aria-labelledby="model-patterns-title">
            <div class="feature-insight-section-heading">
              <span class="insight-source-badge model-badge">MODEL VALIDATION REFERENCE</span>
              <h3 id="model-patterns-title">Features associated with model performance</h3>
              <p id="importance-method-description">Global permutation importance from the validation cohort.</p>
            </div>
            <article class="card model-importance-card">
              <div class="card-heading">
                <div><h3>Top validation features</h3><p>Mean Average Precision decrease after shuffling each feature.</p></div>
              </div>
              <div class="model-importance-chart" id="model-importance-chart" role="list" aria-label="Global feature importance from model validation"></div>
              <p class="table-note" id="importance-reference-note"></p>
            </article>
            <div class="interpretation-note feature-insight-caveat">
              <span class="note-icon" aria-hidden="true">i</span>
              <p><strong>How to interpret:</strong> These validation results describe how the model performed when a feature was shuffled. They do not show that a feature causes default or explain an individual customer's score. Engineered features can share information with their source fields, so their importance values should not be added together.</p>
            </div>
          </section>
        </section>

        <section class="empty-state" id="empty-state" aria-labelledby="empty-title">
          <div class="empty-illustration" aria-hidden="true">
            <span class="illustration-card card-one"></span>
            <span class="illustration-card card-two"></span>
            <span class="illustration-chart"><i></i><i></i><i></i><i></i></span>
          </div>
          <h2 id="empty-title">Your portfolio overview will appear here</h2>
          <p>Upload a customer file above to see the portfolio summary and review-capacity breakdown.</p>
        </section>

        <footer class="page-footer">
          <span>Credit risk review · Analyst workspace</span>
          <span>Model estimates support review prioritization only</span>
        </footer>
      </main>
    </div>
  </body>
</html>
```

### `src/propensity_prediction/dashboard/static/styles.css`

```css
:root {
  color-scheme: light;
  --canvas: #f4f7f4;
  --surface: #ffffff;
  --surface-muted: #f8faf8;
  --ink: #263a36;
  --ink-strong: #1a302b;
  --ink-muted: #62746f;
  --ink-soft: #7c8b86;
  --line: #e1e9e4;
  --line-strong: #d1ded7;
  --teal: #287c70;
  --teal-dark: #1f685e;
  --teal-soft: #e6f1ed;
  --blue: #6487a2;
  --blue-soft: #eaf0f5;
  --amber: #aa7740;
  --amber-soft: #f5eee3;
  --rose: #a45f62;
  --rose-soft: #f5e9e8;
  --shadow: 0 10px 30px rgb(36 63 53 / 5%);
  --radius: 18px;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
}

* { box-sizing: border-box; }

body {
  min-width: 320px;
  min-height: 100vh;
  margin: 0;
  background: var(--canvas);
  color: var(--ink);
  font-size: 14px;
  line-height: 1.55;
}

button, input { font: inherit; }
button { color: inherit; }
a { color: inherit; }
[hidden] { display: none !important; }

:focus-visible {
  outline: 3px solid #75a99d;
  outline-offset: 3px;
}

.app-shell { min-height: 100vh; }

.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 5;
  display: flex;
  width: 248px;
  flex-direction: column;
  padding: 26px 18px 20px;
  border-right: 1px solid var(--line);
  background: #fbfcfa;
}

.brand {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 2px 8px 28px;
  text-decoration: none;
}

.brand-mark {
  display: grid;
  width: 39px;
  height: 39px;
  place-items: center;
  border-radius: 13px;
  background: var(--teal-dark);
  color: #fff;
  font-family: "Manrope", sans-serif;
  font-size: 19px;
  font-weight: 800;
}

.brand-copy { display: grid; line-height: 1.25; }
.brand-copy strong { color: var(--ink-strong); font-size: 15px; font-weight: 700; }
.brand-copy span { margin-top: 3px; color: var(--ink-muted); font-size: 11px; }

.nav-label, .eyebrow {
  color: var(--ink-soft);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .12em;
}

.nav-label { margin: 0 10px 10px; }
.primary-nav { display: grid; gap: 5px; }

.nav-link {
  display: flex;
  min-height: 44px;
  align-items: center;
  gap: 11px;
  padding: 0 11px;
  border-radius: 10px;
  color: #566963;
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
}

.nav-link.is-active {
  background: var(--teal-soft);
  color: #245f55;
  font-weight: 700;
}

.nav-icon {
  display: inline-grid;
  width: 22px;
  place-items: center;
  color: currentColor;
  font-size: 18px;
  line-height: 1;
}

.nav-link.is-disabled { color: #77857f; cursor: not-allowed; }
.nav-link:not(.is-disabled):hover { background: #f0f5f1; color: var(--teal-dark); }
.nav-soon {
  margin-left: auto;
  color: #77857f;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: .08em;
}

.sidebar-bottom { display: grid; gap: 17px; margin-top: auto; }
.sidebar-note, .interpretation-note {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  border: 1px solid #dfe9e3;
  background: #f1f6f2;
  color: #475d55;
}

.sidebar-note { padding: 12px 11px; border-radius: 12px; }
.sidebar-note p, .interpretation-note p { margin: 0; font-size: 11px; line-height: 1.55; }
.note-icon {
  display: inline-grid;
  width: 18px;
  height: 18px;
  flex: 0 0 auto;
  place-items: center;
  border: 1px solid #9bb5a9;
  border-radius: 50%;
  color: #3f6d5d;
  font-size: 11px;
  font-weight: 700;
}

.service-status { display: flex; align-items: center; gap: 8px; padding: 0 7px; color: var(--ink-muted); font-size: 11px; }
.status-dot, .meta-dot { width: 8px; height: 8px; border-radius: 50%; background: #b3c0b9; }
.service-status.is-ready .status-dot { background: #38876d; box-shadow: 0 0 0 3px #e2f0e8; }
.service-status.is-error .status-dot { background: #a45f62; box-shadow: 0 0 0 3px #f5e9e8; }

.main-content { max-width: 1540px; min-height: 100vh; margin-left: 248px; padding: 0 44px 24px; }
.topbar { display: flex; height: 72px; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--line); }
.breadcrumb { color: var(--ink-muted); font-size: 12px; }
.breadcrumb span { margin: 0 7px; color: #9aa8a2; }
.topbar-actions { display: flex; align-items: center; gap: 16px; }
.text-button { padding: 6px 2px; border: 0; background: transparent; color: #4c665e; cursor: pointer; font-size: 12px; font-weight: 600; }
.text-button:hover { color: var(--teal-dark); }
.avatar { display: grid; width: 31px; height: 31px; place-items: center; border: 1px solid #dce5df; border-radius: 50%; background: #e9f0eb; color: #426257; font-size: 10px; font-weight: 700; }

.page-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; padding: 31px 0 22px; }
.page-heading .eyebrow, .section-heading .eyebrow { margin: 0 0 6px; }
h1, h2, h3, p { margin-top: 0; }
h1, h2, h3 { color: var(--ink-strong); font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
h1 { margin-bottom: 6px; font-size: clamp(24px, 2.4vw, 32px); font-weight: 700; letter-spacing: -.04em; line-height: 1.2; }
.page-description { margin: 0; color: var(--ink-muted); font-size: 13px; }
.analysis-meta { display: inline-flex; align-items: center; gap: 8px; padding: 7px 11px; border: 1px solid var(--line); border-radius: 99px; background: var(--surface); color: #50665e; font-size: 11px; white-space: nowrap; }
.analysis-meta .meta-dot { background: #3c8a6f; }

.analysis-panel {
  display: grid;
  grid-template-columns: minmax(220px, .78fr) minmax(380px, 1.45fr);
  gap: 28px;
  padding: 22px 24px;
  border: 1px solid #dce7e0;
  border-radius: var(--radius);
  background: linear-gradient(116deg, #edf4ef, #f9fbf8 65%);
  box-shadow: var(--shadow);
}

.analysis-panel-copy { align-self: center; }
.step-badge { display: inline-block; margin-bottom: 9px; color: #4e7d6e; font-size: 9px; font-weight: 700; letter-spacing: .13em; }
.analysis-panel h2 { margin: 0 0 6px; font-size: 17px; letter-spacing: -.025em; }
.analysis-panel-copy p { max-width: 330px; margin: 0; color: var(--ink-muted); font-size: 12px; line-height: 1.6; }
.analysis-form { display: grid; align-content: center; gap: 12px; }
.file-drop { display: flex; min-height: 70px; align-items: center; gap: 12px; padding: 10px 12px; border: 1px dashed #aabeb2; border-radius: 12px; background: rgb(255 255 255 / 76%); cursor: pointer; }
.file-drop:hover, .file-drop:focus-within { border-color: var(--teal); background: #fff; }
.upload-icon { display: grid; width: 38px; height: 38px; flex: 0 0 auto; place-items: center; border-radius: 11px; background: #e7f1eb; color: #3d7461; font-size: 22px; font-weight: 500; }
.file-drop-copy { display: grid; min-width: 0; gap: 3px; }
.file-drop-copy strong { overflow: hidden; color: var(--ink-strong); font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }
.file-drop-copy span { color: var(--ink-muted); font-size: 10px; }
.browse-button { margin-left: auto; padding: 7px 10px; border: 1px solid var(--line-strong); border-radius: 8px; background: #fff; color: #395b50; font-size: 10px; font-weight: 700; white-space: nowrap; }
.visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; clip-path: inset(50%); }
.form-actions { display: flex; align-items: flex-end; justify-content: space-between; gap: 14px; }
.capacity-field { display: grid; gap: 5px; color: #536760; font-size: 10px; font-weight: 600; }
.capacity-input-wrap { display: flex; height: 36px; align-items: center; gap: 8px; padding: 0 9px; border: 1px solid var(--line-strong); border-radius: 8px; background: #fff; color: var(--ink-muted); font-size: 10px; }
.capacity-input-wrap input { width: 78px; border: 0; outline: none; background: transparent; color: var(--ink-strong); font-size: 12px; font-weight: 600; }
.capacity-input-wrap input:focus-visible { outline: 2px solid #75a99d; outline-offset: 2px; }
.primary-button { display: inline-flex; min-height: 37px; align-items: center; justify-content: center; gap: 15px; padding: 0 15px; border: 1px solid var(--teal-dark); border-radius: 8px; background: var(--teal-dark); color: #fff; cursor: pointer; font-size: 11px; font-weight: 700; transition: background .15s ease, transform .15s ease; }
.primary-button:hover { transform: translateY(-1px); background: #19584f; }
.primary-button:disabled { cursor: wait; opacity: .72; transform: none; }
.form-message { margin: 0; color: #8b4448; font-size: 11px; line-height: 1.5; }
.form-message.is-success { color: #34735d; }
.capacity-refresh-note { margin: -4px 0 0; color: var(--ink-soft); font-size: 9px; line-height: 1.45; }

.results-section { padding-top: 31px; }
.section-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 18px; margin-bottom: 15px; }
.section-heading h2 { margin: 0 0 5px; font-size: 19px; letter-spacing: -.03em; }
.section-description { margin: 0; color: var(--ink-muted); font-size: 11px; }
.portfolio-count { padding: 6px 10px; border: 1px solid var(--line); border-radius: 99px; background: #fff; color: #587069; font-size: 10px; font-weight: 600; white-space: nowrap; }
.metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 13px; margin-bottom: 15px; }
.metric-card { min-height: 112px; padding: 16px 17px; border: 1px solid var(--line); border-radius: 14px; background: var(--surface); box-shadow: 0 5px 16px rgb(36 63 53 / 3%); }
.metric-card-top { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.metric-label { color: var(--ink-muted); font-size: 10px; font-weight: 600; }
.metric-icon { display: grid; width: 27px; height: 27px; place-items: center; border-radius: 9px; background: var(--teal-soft); color: #397366; font-size: 13px; }
.metric-card:nth-child(2) .metric-icon { background: var(--blue-soft); color: #597b96; }
.metric-card:nth-child(3) .metric-icon { background: var(--amber-soft); color: #8d6639; }
.metric-card:nth-child(4) .metric-icon { background: var(--rose-soft); color: #92575a; }
.metric-value { display: block; margin-top: 9px; color: var(--ink-strong); font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; font-size: 25px; font-weight: 700; letter-spacing: -.04em; line-height: 1.15; }
.metric-help { display: block; margin-top: 5px; color: var(--ink-soft); font-size: 9px; }

.insight-grid { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(300px, .85fr); gap: 15px; }
.card { min-width: 0; padding: 19px 20px 17px; border: 1px solid var(--line); border-radius: 15px; background: var(--surface); box-shadow: 0 5px 16px rgb(36 63 53 / 3%); }
.card-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 15px; margin-bottom: 18px; }
.card-heading h3 { margin: 0 0 4px; font-size: 14px; letter-spacing: -.02em; }
.card-heading p { margin: 0; color: var(--ink-muted); font-size: 10px; }
.chart-mark { display: grid; width: 30px; height: 30px; flex: 0 0 auto; place-items: center; border-radius: 9px; background: #edf4ef; color: #547c69; font-size: 17px; }
.capacity-mark { background: #edf1f5; color: #617b91; }
.band-list { display: grid; gap: 14px; }
.band-row { display: grid; grid-template-columns: 77px minmax(70px, 1fr) 58px; align-items: center; gap: 12px; }
.band-label { color: #4b6058; font-size: 10px; font-weight: 600; }
.band-track { height: 10px; overflow: hidden; border-radius: 99px; background: #edf1ee; }
.band-fill { display: block; height: 100%; min-width: 0; border-radius: inherit; transition: width .45s ease; }
.band-row[data-band="Lower"] .band-fill { background: #76a994; }
.band-row[data-band="Moderate"] .band-fill { background: #7894a8; }
.band-row[data-band="Elevated"] .band-fill { background: #c49a61; }
.band-row[data-band="Highest"] .band-fill { background: #b97778; }
.band-value { color: #3f554c; font-size: 10px; font-variant-numeric: tabular-nums; text-align: right; }
.band-value strong { color: var(--ink-strong); font-weight: 700; }
.band-value span { color: var(--ink-soft); }
.chart-note { margin-top: 17px; padding-top: 12px; border-top: 1px solid #edf1ee; color: var(--ink-muted); }
.chart-note summary { width: fit-content; color: #466e61; cursor: pointer; font-size: 10px; font-weight: 600; }
.chart-note p { max-width: 640px; margin: 9px 0 0; font-size: 10px; line-height: 1.6; }

.capacity-visual { display: flex; min-height: 150px; align-items: center; justify-content: center; gap: clamp(18px, 4vw, 47px); }
.capacity-ring { display: grid; width: 142px; height: 142px; flex: 0 0 auto; place-items: center; border-radius: 50%; background: conic-gradient(#438675 0deg, #438675 0deg, #e8efeb 0deg 360deg); }
.ring-center { display: grid; width: 110px; height: 110px; align-content: center; justify-items: center; border-radius: 50%; background: #fff; }
.ring-center strong { color: var(--ink-strong); font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; font-size: 24px; letter-spacing: -.04em; }
.ring-center span { color: var(--ink-muted); font-size: 9px; }
.capacity-legend { display: grid; gap: 13px; }
.legend-item { display: grid; grid-template-columns: 9px auto; align-items: start; gap: 8px; color: var(--ink-muted); font-size: 10px; }
.legend-dot { width: 8px; height: 8px; margin-top: 4px; border-radius: 50%; background: #438675; }
.legend-item:nth-child(2) .legend-dot { background: #9bb9aa; }
.legend-item:nth-child(3) .legend-dot { background: #d5ded8; }
.legend-copy { display: grid; gap: 1px; }
.legend-copy strong { color: #42574f; font-size: 11px; font-weight: 700; }
.legend-copy span { color: var(--ink-soft); font-size: 9px; }
.capacity-footnote { min-height: 28px; margin-top: 9px; padding-top: 10px; border-top: 1px solid #edf1ee; color: var(--ink-muted); font-size: 9px; line-height: 1.5; }

.interpretation-note { align-items: flex-start; margin-top: 15px; padding: 11px 13px; border-radius: 11px; }
.interpretation-note p { font-size: 10px; }
.interpretation-note strong { color: #38584d; }

.explore-view { padding-top: 31px; }
.explore-heading { margin-bottom: 15px; }
.filters-card { margin-bottom: 15px; }
.filter-heading { align-items: center; margin-bottom: 15px; }
.filter-heading .text-button { flex: 0 0 auto; }
.filter-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.filter-control { display: grid; min-width: 0; gap: 5px; color: #536760; font-size: 10px; font-weight: 600; }
.filter-control input, .filter-control select, .group-field select {
  width: 100%; min-width: 0; height: 36px; padding: 0 9px; border: 1px solid var(--line-strong);
  border-radius: 8px; background: #fff; color: var(--ink-strong); font-size: 11px;
}
.feature-value-control { align-content: end; }
.feature-value-control[hidden] { display: none; }
.feature-value-control > span { color: #536760; font-size: 10px; font-weight: 600; }
.feature-range-inputs { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.filter-message { min-height: 16px; margin: 8px 0 0; color: #8b4448; font-size: 10px; }
.explore-summary-grid { display: grid; grid-template-columns: minmax(0, .85fr) minmax(0, 1.15fr); gap: 15px; margin-bottom: 15px; }
.distribution-card, .group-card { min-width: 0; }
.score-distribution { display: grid; gap: 8px; }
.distribution-row { display: grid; grid-template-columns: 48px minmax(40px, 1fr) 77px; align-items: center; gap: 9px; }
.distribution-label { color: #4b6058; font-size: 9px; font-variant-numeric: tabular-nums; }
.distribution-track { display: block; height: 9px; overflow: hidden; border-radius: 99px; background: #edf1ee; }
.distribution-fill { display: block; height: 100%; border-radius: inherit; background: #6b9b87; transition: width .25s ease; }
.distribution-value { color: var(--ink-muted); font-size: 9px; font-variant-numeric: tabular-nums; text-align: right; white-space: nowrap; }
.group-heading { align-items: center; }
.group-field { display: grid; min-width: 110px; gap: 3px; color: var(--ink-muted); font-size: 9px; }
.group-field select { height: 31px; }
.table-scroll { width: 100%; overflow: auto; }
.group-table, .customer-table { width: 100%; border-collapse: collapse; font-size: 10px; text-align: left; }
.group-table th, .customer-table th { padding: 9px 8px; border-bottom: 1px solid var(--line-strong); color: var(--ink-muted); font-size: 9px; font-weight: 700; white-space: nowrap; }
.group-table td, .customer-table td { padding: 9px 8px; border-bottom: 1px solid #edf1ee; color: #40564d; font-variant-numeric: tabular-nums; white-space: nowrap; }
.group-table tbody tr:last-child td, .customer-table tbody tr:last-child td { border-bottom: 0; }
.table-note { margin: 10px 0 0; color: var(--ink-soft); font-size: 9px; line-height: 1.5; }
.customer-results-card { margin-bottom: 15px; }
.customer-results-card .card-heading { align-items: center; margin-bottom: 9px; }
.pagination-controls { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-top: 12px; padding-top: 12px; border-top: 1px solid #edf1ee; color: var(--ink-muted); font-size: 10px; }
.pagination-controls > div { display: flex; gap: 7px; }
.secondary-button { min-height: 30px; padding: 0 10px; border: 1px solid var(--line-strong); border-radius: 7px; background: #fff; color: #456258; cursor: pointer; font-size: 10px; font-weight: 600; }
.secondary-button:disabled { cursor: default; color: #9aa8a2; background: #f7f9f7; }

.queue-view { padding-top: 31px; }
.queue-heading { margin-bottom: 15px; }
.queue-metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 13px; margin-bottom: 15px; }
.queue-metric-card { display: grid; min-height: 105px; align-content: start; gap: 2px; }
.queue-metric-card .metric-value { margin-top: 6px; }
.queue-explanation-grid { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(300px, .9fr); gap: 15px; margin-bottom: 15px; }
.queue-policy-list { display: grid; gap: 14px; margin: 0; padding: 0; list-style: none; counter-reset: queue-step; }
.queue-policy-list li { display: grid; grid-template-columns: 25px minmax(0, 1fr); column-gap: 10px; counter-increment: queue-step; }
.queue-policy-list li::before { content: counter(queue-step); display: grid; width: 24px; height: 24px; grid-row: span 2; place-items: center; border-radius: 8px; background: var(--teal-soft); color: #397366; font-size: 10px; font-weight: 700; }
.queue-policy-list strong { color: #38584d; font-size: 11px; }
.queue-policy-list span { margin-top: 2px; color: var(--ink-muted); font-size: 10px; line-height: 1.5; }
.queue-refresh-note { margin-top: 18px; padding: 11px 12px; border: 1px solid #e2eae4; border-radius: 9px; background: var(--surface-muted); color: var(--ink-muted); font-size: 10px; line-height: 1.5; }
.queue-refresh-note strong { color: #3c6558; }
.queue-outcomes-card .group-table td:first-child { min-width: 180px; white-space: normal; line-height: 1.45; }
.selection-profile-card { margin-bottom: 15px; }
.selection-profile-context { margin: -7px 0 14px; color: var(--ink-muted); font-size: 10px; line-height: 1.5; }
.selection-profile-groups { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.selection-profile-group { min-width: 0; padding: 14px; border: 1px solid var(--line); border-radius: 12px; background: var(--surface-muted); }
.selection-profile-group.is-selected { border-color: #d2e5dc; background: #f5faf6; }
.selection-profile-group-heading { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; padding-bottom: 10px; border-bottom: 1px solid var(--line); }
.selection-profile-group-heading h4 { margin: 0; color: var(--ink-strong); font-size: 11px; }
.selection-profile-group-heading span { color: var(--ink-muted); font-size: 9px; text-align: right; }
.selection-profile-measures { display: grid; margin: 0; }
.selection-profile-measure { display: grid; grid-template-columns: minmax(105px, .8fr) minmax(0, 1.2fr); gap: 10px; padding: 10px 0; border-bottom: 1px solid var(--line); }
.selection-profile-measure:last-child { border-bottom: 0; padding-bottom: 0; }
.selection-profile-measure dt { color: #4b6058; font-size: 10px; font-weight: 600; }
.selection-profile-measure dd { display: grid; gap: 2px; margin: 0; color: var(--ink-muted); font-size: 9px; font-variant-numeric: tabular-nums; }
.selection-profile-measure dd strong { color: var(--ink-strong); font-size: 10px; }
.selection-profile-empty { margin: 14px 0 2px; color: var(--ink-muted); font-size: 10px; }
.feature-insights-view { padding-top: 31px; }
.feature-insights-heading { margin-bottom: 23px; }
.feature-insight-section { margin-bottom: 25px; }
.feature-insight-section-heading { margin-bottom: 12px; }
.feature-insight-section-heading h3 { margin: 7px 0 4px; font-size: 16px; letter-spacing: -.02em; }
.feature-insight-section-heading p { margin: 0; color: var(--ink-muted); font-size: 10px; }
.insight-source-badge { display: inline-flex; padding: 5px 8px; border-radius: 99px; font-size: 8px; font-weight: 700; letter-spacing: .1em; }
.observed-badge { background: #eaf2ed; color: #3e725f; }
.model-badge { background: #edf0f5; color: #5c718e; }
.observed-pattern-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.repayment-pattern-card { grid-column: 1 / -1; }
.repayment-status-chart { display: grid; gap: 12px; }
.repayment-month-row { display: grid; gap: 6px; padding-bottom: 10px; border-bottom: 1px solid #edf1ee; }
.repayment-month-row:last-child { padding-bottom: 0; border-bottom: 0; }
.repayment-month-heading { display: flex; justify-content: space-between; gap: 10px; color: var(--ink-muted); font-size: 9px; }
.repayment-month-heading strong { color: #40564d; font-size: 10px; }
.repayment-status-track { display: flex; height: 12px; overflow: hidden; border-radius: 99px; background: #edf1ee; }
.repayment-status-segment { min-width: 1px; height: 100%; }
.repayment-status-legend { display: flex; flex-wrap: wrap; gap: 5px 12px; }
.repayment-status-key { display: inline-flex; align-items: center; gap: 5px; color: var(--ink-muted); font-size: 8px; font-variant-numeric: tabular-nums; }
.repayment-status-key i { width: 7px; height: 7px; flex: 0 0 auto; border-radius: 2px; }
.monthly-amount-card .card-heading { margin-bottom: 10px; }
.monthly-profile-table { min-width: 500px; }
.monthly-profile-table td:first-child { color: #40564d; font-weight: 600; }
.monthly-profile-table td { font-size: 9px; }
.model-insight-section { margin-top: 29px; }
.model-importance-card .card-heading { margin-bottom: 10px; }
.model-importance-chart { display: grid; gap: 4px; }
.model-importance-row { display: grid; grid-template-columns: minmax(190px, 1.15fr) minmax(100px, 1fr) minmax(145px, .9fr); align-items: center; gap: 13px; padding: 9px 0; border-bottom: 1px solid #edf1ee; }
.model-importance-row:last-child { border-bottom: 0; }
.model-importance-feature, .model-importance-score { display: grid; gap: 2px; }
.model-importance-feature strong, .model-importance-score strong { color: var(--ink-strong); font-size: 10px; font-variant-numeric: tabular-nums; }
.model-importance-feature span, .model-importance-score span { color: var(--ink-muted); font-size: 9px; line-height: 1.4; }
.importance-score-track { position: relative; height: 12px; overflow: hidden; border-radius: 99px; background: #edf1ee; }
.importance-score-track::after { position: absolute; top: 0; bottom: 0; left: 50%; width: 1px; background: #82948c; content: ""; }
.importance-score-bar { position: absolute; top: 0; left: 50%; height: 100%; border-radius: 0 99px 99px 0; background: #6b9b87; }
.importance-score-bar.is-negative { right: 50%; left: auto; border-radius: 99px 0 0 99px; background: #bd8583; }
.feature-insight-caveat { margin-top: 13px; }
.selected-queue-card { margin-bottom: 15px; }
.selected-queue-card .customer-table td:last-child { min-width: 300px; white-space: normal; line-height: 1.45; }

.empty-state { display: grid; justify-items: center; padding: 34px 20px 30px; color: var(--ink-muted); text-align: center; }
.empty-illustration { position: relative; width: 126px; height: 91px; margin-bottom: 13px; }
.illustration-card { position: absolute; width: 80px; height: 56px; border: 1px solid #dce7e0; border-radius: 10px; background: #fff; box-shadow: var(--shadow); }
.card-one { top: 7px; left: 16px; transform: rotate(-8deg); }
.card-two { top: 5px; left: 35px; transform: rotate(7deg); }
.illustration-chart { position: absolute; right: 9px; bottom: 8px; display: flex; width: 57px; height: 41px; align-items: flex-end; gap: 5px; padding: 6px; border: 1px solid #dce7e0; border-radius: 9px; background: #f8fbf8; }
.illustration-chart i { flex: 1; border-radius: 3px 3px 1px 1px; background: #8bb7a4; }
.illustration-chart i:nth-child(1) { height: 36%; }
.illustration-chart i:nth-child(2) { height: 58%; background: #9bb1bb; }
.illustration-chart i:nth-child(3) { height: 45%; background: #cfb082; }
.illustration-chart i:nth-child(4) { height: 78%; background: #c18787; }
.empty-state h2 { margin: 0 0 5px; font-size: 15px; letter-spacing: -.02em; }
.empty-state p { max-width: 410px; margin: 0; color: var(--ink-muted); font-size: 11px; }
.page-footer { display: flex; justify-content: space-between; gap: 15px; margin-top: 12px; padding: 14px 0 3px; border-top: 1px solid var(--line); color: var(--ink-soft); font-size: 9px; }

@media (max-width: 1120px) {
  .main-content { padding-right: 28px; padding-left: 28px; }
  .sidebar { width: 220px; }
  .main-content { margin-left: 220px; }
  .analysis-panel { grid-template-columns: 1fr; gap: 16px; }
  .analysis-panel-copy p { max-width: 520px; }
  .filter-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .queue-explanation-grid { grid-template-columns: 1fr; }
}

@media (max-width: 820px) {
  .sidebar { position: static; width: auto; height: auto; padding: 13px 18px; border-right: 0; border-bottom: 1px solid var(--line); }
  .brand { padding: 0; }
  .nav-label, .sidebar-bottom { display: none; }
  .primary-nav { display: flex; overflow-x: auto; gap: 4px; margin-top: 13px; }
  .nav-link { min-height: 38px; flex: 0 0 auto; padding: 0 10px; font-size: 11px; }
  .nav-icon { width: 16px; font-size: 15px; }
  .nav-soon { display: none; }
  .main-content { margin-left: 0; padding: 0 20px 20px; }
  .topbar { height: 55px; }
  .insight-grid { grid-template-columns: 1fr; }
  .explore-summary-grid { grid-template-columns: 1fr; }
  .queue-metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; }
  .selection-profile-groups { grid-template-columns: 1fr; }
  .observed-pattern-grid { grid-template-columns: 1fr; }
  .repayment-pattern-card { grid-column: auto; }
}

@media (max-width: 980px) {
  .model-importance-row { grid-template-columns: minmax(160px, 1fr) minmax(80px, .7fr); }
  .model-importance-score { grid-column: 1 / -1; }
}

@media (max-width: 560px) {
  .main-content { padding-right: 14px; padding-left: 14px; }
  .page-heading { align-items: flex-start; flex-direction: column; gap: 10px; padding: 23px 0 17px; }
  .analysis-panel { padding: 17px 14px; }
  .file-drop { gap: 9px; }
  .browse-button { padding: 7px; font-size: 9px; }
  .file-drop-copy span { max-width: 180px; font-size: 9px; }
  .form-actions { align-items: stretch; flex-direction: column; }
  .capacity-field { align-items: flex-start; }
  .primary-button { width: 100%; }
  .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; }
  .metric-card { min-height: 104px; padding: 13px; }
  .metric-value { font-size: 22px; }
  .card { padding: 16px 14px; }
  .band-row { grid-template-columns: 68px minmax(45px, 1fr) 52px; gap: 8px; }
  .capacity-visual { gap: 17px; }
  .capacity-ring { width: 120px; height: 120px; }
  .ring-center { width: 94px; height: 94px; }
  .ring-center strong { font-size: 21px; }
  .section-heading { align-items: flex-start; flex-direction: column; }
  .filter-grid { grid-template-columns: 1fr 1fr; }
  .group-heading { align-items: flex-start; flex-direction: column; }
  .page-footer { flex-direction: column; gap: 4px; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; }
}
```

### `src/propensity_prediction/dashboard/static/app.js`

```javascript
"use strict";

const INTEGER_FIELDS = new Set([
  "ID", "SEX", "EDUCATION", "MARRIAGE",
  "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
]);
const NON_NEGATIVE_FIELDS = new Set([
  "LIMIT_BAL", "PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6",
]);
const INTEGER_RANGES = {
  SEX: [1, 2],
  EDUCATION: [0, 4],
  MARRIAGE: [0, 3],
};
const CATEGORICAL_FIELDS = new Set([
  "SEX", "EDUCATION", "MARRIAGE", "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
]);
const PAGE_SIZE = 50;

const elements = {
  form: document.querySelector("#analysis-form"),
  file: document.querySelector("#portfolio-file"),
  fileName: document.querySelector("#file-name"),
  fileHint: document.querySelector("#file-hint"),
  capacity: document.querySelector("#review-capacity"),
  runButton: document.querySelector("#run-analysis"),
  formMessage: document.querySelector("#form-message"),
  status: document.querySelector("#service-status"),
  healthCheck: document.querySelector("#health-check"),
  emptyState: document.querySelector("#empty-state"),
  results: document.querySelector("#results-section"),
  metrics: document.querySelector("#metric-grid"),
  riskBands: document.querySelector("#risk-band-chart"),
  riskReference: document.querySelector("#risk-band-reference"),
  capacityRing: document.querySelector("#capacity-ring"),
  capacityPercent: document.querySelector("#capacity-percent"),
  capacityLegend: document.querySelector("#capacity-legend"),
  capacityFootnote: document.querySelector("#capacity-footnote"),
  portfolioCount: document.querySelector("#portfolio-count"),
  analysisMeta: document.querySelector("#analysis-meta"),
  analysisMetaText: document.querySelector("#analysis-meta-text"),
  exploreView: document.querySelector("#explore-view"),
  queueView: document.querySelector("#queue-view"),
  viewLinks: [...document.querySelectorAll("[data-view]")],
  exploreCount: document.querySelector("#explore-count"),
  customerIdFilter: document.querySelector("#filter-customer-id"),
  scoreMinFilter: document.querySelector("#filter-score-min"),
  scoreMaxFilter: document.querySelector("#filter-score-max"),
  riskBandFilter: document.querySelector("#filter-risk-band"),
  reviewStatusFilter: document.querySelector("#filter-review-status"),
  featureFilter: document.querySelector("#filter-feature"),
  featureValueControl: document.querySelector("#feature-value-control"),
  resetFilters: document.querySelector("#reset-filters"),
  filterMessage: document.querySelector("#filter-message"),
  groupByField: document.querySelector("#group-by-field"),
  scoreDistribution: document.querySelector("#score-distribution"),
  groupSummaryBody: document.querySelector("#group-summary-body"),
  groupTableNote: document.querySelector("#group-table-note"),
  customerResultsBody: document.querySelector("#customer-results-body"),
  pageCount: document.querySelector("#page-count"),
  pageStatus: document.querySelector("#page-status"),
  previousPage: document.querySelector("#previous-page"),
  nextPage: document.querySelector("#next-page"),
  queuePopulationCount: document.querySelector("#queue-population-count"),
  queueMetricGrid: document.querySelector("#queue-metric-grid"),
  queueReasonsBody: document.querySelector("#queue-reasons-body"),
  selectedQueueBody: document.querySelector("#selected-queue-body"),
  queuePageCount: document.querySelector("#queue-page-count"),
  queuePageStatus: document.querySelector("#queue-page-status"),
  queuePreviousPage: document.querySelector("#queue-previous-page"),
  queueNextPage: document.querySelector("#queue-next-page"),
  selectionProfileGroups: document.querySelector("#selection-profile-groups"),
  featureInsightsView: document.querySelector("#feature-insights-view"),
  featureInsightsCount: document.querySelector("#feature-insights-count"),
  repaymentStatusChart: document.querySelector("#repayment-status-chart"),
  monthlyBillSummary: document.querySelector("#monthly-bill-summary"),
  monthlyPaymentSummary: document.querySelector("#monthly-payment-summary"),
  importanceMethodDescription: document.querySelector("#importance-method-description"),
  modelImportanceChart: document.querySelector("#model-importance-chart"),
  importanceReferenceNote: document.querySelector("#importance-reference-note"),
};

let dashboardConfig = null;
let selectedFile = null;
let currentPortfolio = [];
let currentResult = null;
let filteredPortfolio = [];
let currentPage = 0;
let queuePage = 0;
let activeView = "overview";
const quartileBoundaryCache = new Map();

const percentFormatter = new Intl.NumberFormat(undefined, {
  style: "percent",
  maximumFractionDigits: 1,
});
const numberFormatter = new Intl.NumberFormat(undefined, {
  maximumFractionDigits: 0,
});

function showMessage(message, kind = "error") {
  elements.formMessage.textContent = message;
  elements.formMessage.hidden = false;
  elements.formMessage.classList.toggle("is-success", kind === "success");
}

function clearMessage() {
  elements.formMessage.textContent = "";
  elements.formMessage.hidden = true;
  elements.formMessage.classList.remove("is-success");
}

function setServiceStatus(ready, message) {
  elements.status.classList.toggle("is-ready", ready);
  elements.status.classList.toggle("is-error", !ready);
  elements.status.lastChild.textContent = ` ${message}`;
}

function parseCsv(text) {
  const source = text.replace(/^\uFEFF/, "");
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;
  let afterQuote = false;

  for (let index = 0; index < source.length; index += 1) {
    const character = source[index];
    const next = source[index + 1];

    if (inQuotes) {
      if (character === '"' && next === '"') {
        field += '"';
        index += 1;
      } else if (character === '"') {
        inQuotes = false;
        afterQuote = true;
      } else {
        field += character;
      }
      continue;
    }

    if (afterQuote) {
      if (character === ",") {
        row.push(field);
        field = "";
        afterQuote = false;
      } else if (character === "\n" || character === "\r") {
        row.push(field);
        appendCsvRow(rows, row);
        row = [];
        field = "";
        afterQuote = false;
        if (character === "\r" && next === "\n") index += 1;
      } else if (character === " " || character === "\t") {
        // Ignore whitespace between a closing quote and its delimiter.
      } else {
        throw new Error("The CSV has invalid characters after a quoted value.");
      }
      continue;
    }

    if (character === '"') {
      if (field.length > 0) {
        throw new Error("The CSV contains a quote inside an unquoted value.");
      }
      inQuotes = true;
    } else if (character === ",") {
      row.push(field);
      field = "";
    } else if (character === "\n" || character === "\r") {
      row.push(field);
      appendCsvRow(rows, row);
      row = [];
      field = "";
      if (character === "\r" && next === "\n") index += 1;
    } else {
      field += character;
    }
  }

  if (inQuotes) throw new Error("The CSV contains an unclosed quoted value.");
  if (field.length > 0 || row.length > 0 || afterQuote) {
    row.push(field);
    appendCsvRow(rows, row);
  }
  return rows;
}

function appendCsvRow(rows, row) {
  if (row.length === 1 && row[0] === "") return;
  rows.push(row);
}

function parseNumeric(value, column, csvRowNumber) {
  const trimmed = value.trim();
  const decimalPattern = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/;
  if (!decimalPattern.test(trimmed)) {
    throw new Error(`${column} must contain numeric values. Check CSV row ${csvRowNumber}.`);
  }
  const number = Number(trimmed);
  if (!Number.isFinite(number)) {
    throw new Error(`${column} must contain finite numeric values. Check CSV row ${csvRowNumber}.`);
  }
  if (INTEGER_FIELDS.has(column) && !Number.isInteger(number)) {
    throw new Error(`${column} must contain integer values. Check CSV row ${csvRowNumber}.`);
  }
  if (column === "ID" && !Number.isSafeInteger(number)) {
    throw new Error(`ID must be a safely representable integer. Check CSV row ${csvRowNumber}.`);
  }
  if (NON_NEGATIVE_FIELDS.has(column) && number < 0) {
    throw new Error(`${column} must be non-negative. Check CSV row ${csvRowNumber}.`);
  }
  if (Object.hasOwn(INTEGER_RANGES, column)) {
    const [minimum, maximum] = INTEGER_RANGES[column];
    if (number < minimum || number > maximum) {
      throw new Error(`${column} must use values from ${minimum} through ${maximum}. Check CSV row ${csvRowNumber}.`);
    }
  }
  return number;
}

function validateCsvRows(rows) {
  if (!rows.length) throw new Error("The CSV is empty.");
  const [headers, ...dataRows] = rows;
  if (!headers.length || headers.every((header) => header === "")) {
    throw new Error("The CSV must include a header row.");
  }
  if (new Set(headers).size !== headers.length) {
    throw new Error("The CSV contains duplicate column names.");
  }
  if (headers.includes("DEFAULT")) {
    throw new Error("DEFAULT is a historical outcome, not an input for prediction. Upload a prediction-time file without this column.");
  }

  const required = dashboardConfig.required_columns;
  const missing = required.filter((column) => !headers.includes(column));
  const extra = headers.filter((column) => !required.includes(column));
  if (missing.length || extra.length) {
    const problems = [];
    if (missing.length) problems.push(`Missing required columns: ${missing.join(", ")}.`);
    if (extra.length) problems.push(`Unrecognized columns: ${extra.join(", ")}.`);
    throw new Error(problems.join(" "));
  }
  if (!dataRows.length) throw new Error("The CSV must contain at least one customer row.");
  if (dataRows.length > dashboardConfig.max_customer_rows) {
    throw new Error(`The CSV contains ${numberFormatter.format(dataRows.length)} customer rows; the maximum is ${numberFormatter.format(dashboardConfig.max_customer_rows)}. Split the portfolio into smaller files.`);
  }

  const seenIds = new Set();
  return dataRows.map((values, rowIndex) => {
    const csvRowNumber = rowIndex + 2;
    if (values.length !== headers.length) {
      throw new Error(`CSV row ${csvRowNumber} has ${values.length} values; expected ${headers.length}.`);
    }
    const sourceRow = Object.fromEntries(headers.map((header, index) => [header, values[index]]));
    const customer = {};
    for (const column of required) {
      const value = sourceRow[column];
      if (value === undefined || value.trim() === "") {
        throw new Error(`${column} cannot be blank. Check CSV row ${csvRowNumber}.`);
      }
      customer[column] = parseNumeric(value, column, csvRowNumber);
    }
    if (seenIds.has(customer.ID)) {
      throw new Error(`ID values must be unique. Duplicate ID ${customer.ID} appears in CSV row ${csvRowNumber}.`);
    }
    seenIds.add(customer.ID);
    return customer;
  });
}

function formatCount(value) {
  return numberFormatter.format(value);
}

function formatPercent(value) {
  return percentFormatter.format(value);
}

function formatProfileNumber(value) {
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 1 }).format(value);
}

const PROFILE_MEASURES = [
  { label: "Predicted risk", read: (row) => row.predicted_default_probability, format: formatPercent },
  { label: "Credit limit", read: (row) => row.LIMIT_BAL, format: formatProfileNumber },
  { label: "Age (years)", read: (row) => row.AGE, format: formatProfileNumber },
  {
    label: "Average bill amount",
    read: (row) => meanOfFields(row, ["BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "BILL_AMT4", "BILL_AMT5", "BILL_AMT6"]),
    format: formatProfileNumber,
  },
  {
    label: "Average payment amount",
    read: (row) => meanOfFields(row, ["PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6"]),
    format: formatProfileNumber,
  },
];

const MONTHLY_FEATURES = [
  { month: "April 2005", status: "PAY_6", bill: "BILL_AMT6", payment: "PAY_AMT6" },
  { month: "May 2005", status: "PAY_5", bill: "BILL_AMT5", payment: "PAY_AMT5" },
  { month: "June 2005", status: "PAY_4", bill: "BILL_AMT4", payment: "PAY_AMT4" },
  { month: "July 2005", status: "PAY_3", bill: "BILL_AMT3", payment: "PAY_AMT3" },
  { month: "August 2005", status: "PAY_2", bill: "BILL_AMT2", payment: "PAY_AMT2" },
  { month: "September 2005", status: "PAY_0", bill: "BILL_AMT1", payment: "PAY_AMT1" },
];

const STATUS_COLORS = [
  "#718b9a", "#91a7a8", "#7fae9b", "#aac49a", "#d0bf84", "#d8a96f",
  "#c98773", "#b87479", "#947b9c", "#7894bd", "#7d9b82", "#a78868",
];

function meanOfFields(row, fields) {
  const values = fields.map((field) => row[field]).filter(Number.isFinite);
  if (values.length !== fields.length) return null;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function quantile(sortedValues, fraction) {
  if (!sortedValues.length) return null;
  const position = (sortedValues.length - 1) * fraction;
  const lowerIndex = Math.floor(position);
  const upperIndex = Math.ceil(position);
  const weight = position - lowerIndex;
  return sortedValues[lowerIndex] * (1 - weight) + sortedValues[upperIndex] * weight;
}

function summarizeMeasure(rows, read) {
  const values = rows.map(read).filter(Number.isFinite).sort((left, right) => left - right);
  if (!values.length) return { count: 0, missing: rows.length };
  return {
    count: values.length,
    missing: rows.length - values.length,
    minimum: values[0],
    percentile25: quantile(values, 0.25),
    median: quantile(values, 0.5),
    percentile75: quantile(values, 0.75),
    maximum: values[values.length - 1],
  };
}

function renderSelectionProfile(rows) {
  const groupDefinitions = [
    { label: "Selected for review", selected: true },
    { label: "Not selected", selected: false },
  ];
  const groups = groupDefinitions.map((definition) => {
    const members = rows.filter((row) => row.selected_for_review === definition.selected);
    const group = document.createElement("article");
    group.className = `selection-profile-group${definition.selected ? " is-selected" : ""}`;

    const heading = document.createElement("div");
    heading.className = "selection-profile-group-heading";
    const title = document.createElement("h4");
    title.textContent = definition.label;
    const size = document.createElement("span");
    const share = rows.length ? formatPercent(members.length / rows.length) : "—";
    size.textContent = `${formatCount(members.length)} customers · ${share} of portfolio`;
    heading.append(title, size);
    group.append(heading);

    if (!members.length) {
      const empty = document.createElement("p");
      empty.className = "selection-profile-empty";
      empty.textContent = "No customers fall into this group under the current capacity.";
      group.append(empty);
      return group;
    }

    const list = document.createElement("dl");
    list.className = "selection-profile-measures";
    PROFILE_MEASURES.forEach((measure) => {
      const summary = summarizeMeasure(members, measure.read);
      const item = document.createElement("div");
      item.className = "selection-profile-measure";
      const label = document.createElement("dt");
      label.textContent = measure.label;
      const values = document.createElement("dd");
      if (!summary.count) {
        values.textContent = "No available values";
      } else {
        const median = document.createElement("strong");
        median.textContent = `Median ${measure.format(summary.median)}`;
        const middle = document.createElement("span");
        middle.textContent = `Middle half: ${measure.format(summary.percentile25)}–${measure.format(summary.percentile75)}`;
        const range = document.createElement("span");
        range.textContent = `Range: ${measure.format(summary.minimum)}–${measure.format(summary.maximum)}`;
        const records = document.createElement("span");
        records.textContent = `${formatCount(summary.count)} available · ${formatCount(summary.missing)} missing`;
        values.append(median, middle, range, records);
      }
      item.append(label, values);
      list.append(item);
    });
    group.append(list);
    return group;
  });
  elements.selectionProfileGroups.replaceChildren(...groups);
}

function renderRepaymentStatusDistribution(rows) {
  const codeSet = new Set();
  MONTHLY_FEATURES.forEach(({ status }) => {
    rows.forEach((record) => {
      if (Number.isFinite(record[status])) codeSet.add(record[status]);
    });
  });
  const codes = [...codeSet].sort((left, right) => left - right);
  const colorByCode = new Map(codes.map((code, index) => [code, STATUS_COLORS[index % STATUS_COLORS.length]]));

  const months = MONTHLY_FEATURES.map(({ month, status }) => {
    const counts = new Map(codes.map((code) => [code, 0]));
    let available = 0;
    rows.forEach((record) => {
      const code = record[status];
      if (!Number.isFinite(code)) return;
      counts.set(code, (counts.get(code) ?? 0) + 1);
      available += 1;
    });

    const row = document.createElement("div");
    row.className = "repayment-month-row";
    row.setAttribute("role", "listitem");
    const heading = document.createElement("div");
    heading.className = "repayment-month-heading";
    const label = document.createElement("strong");
    label.textContent = month;
    const recordCount = document.createElement("span");
    recordCount.textContent = `${formatCount(available)} records`;
    heading.append(label, recordCount);

    const track = document.createElement("div");
    track.className = "repayment-status-track";
    const breakdown = [];
    codes.forEach((code) => {
      const count = counts.get(code) ?? 0;
      if (!count || !available) return;
      const share = count / available;
      const segment = document.createElement("span");
      const description = `Code ${code}: ${formatCount(count)} customers (${formatPercent(share)})`;
      segment.className = "repayment-status-segment";
      segment.style.flexBasis = `${share * 100}%`;
      segment.style.backgroundColor = colorByCode.get(code);
      segment.title = description;
      track.append(segment);
      breakdown.push({ code, count, share, description });
    });
    track.setAttribute("role", "img");
    track.setAttribute("aria-label", `${month} repayment status distribution: ${breakdown.map((item) => item.description).join("; ") || "no available records"}`);

    const legend = document.createElement("div");
    legend.className = "repayment-status-legend";
    breakdown.forEach(({ code, description }) => {
      const item = document.createElement("span");
      item.className = "repayment-status-key";
      const swatch = document.createElement("i");
      swatch.setAttribute("aria-hidden", "true");
      swatch.style.backgroundColor = colorByCode.get(code);
      const text = document.createElement("span");
      text.textContent = description;
      item.append(swatch, text);
      legend.append(item);
    });
    row.append(heading, track, legend);
    return row;
  });
  elements.repaymentStatusChart.replaceChildren(...months);
}

function renderMonthlyAmountSummary(rows, fieldName, target) {
  const tableRows = MONTHLY_FEATURES.map(({ month, [fieldName]: field }) => {
    const summary = summarizeMeasure(rows, (record) => record[field]);
    const row = document.createElement("tr");
    const values = [
      month,
      summary.count ? formatProfileNumber(summary.median) : "—",
      summary.count ? `${formatProfileNumber(summary.percentile25)}–${formatProfileNumber(summary.percentile75)}` : "—",
      summary.count ? `${formatProfileNumber(summary.minimum)}–${formatProfileNumber(summary.maximum)}` : "—",
      `${formatCount(summary.count)} available · ${formatCount(summary.missing)} missing`,
    ];
    values.forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    return row;
  });
  target.replaceChildren(...tableRows);
}

function formatImportanceScore(value) {
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 6 }).format(value);
}

function renderModelImportance(reference) {
  if (!reference?.features?.length) {
    elements.modelImportanceChart.textContent = "Model reference results are unavailable.";
    return;
  }
  elements.importanceMethodDescription.textContent =
    `Permutation importance · ${reference.scoring_metric.replaceAll("_", " ")} · ${reference.evaluation_reference}.`;
  const maximumAbsoluteImportance = Math.max(
    ...reference.features.map((item) => Math.abs(item.importance_mean)),
    Number.EPSILON,
  );
  const rows = reference.features.map((item) => {
    const row = document.createElement("div");
    row.className = "model-importance-row";
    row.setAttribute("role", "listitem");
    const feature = document.createElement("div");
    feature.className = "model-importance-feature";
    const name = document.createElement("strong");
    name.textContent = item.feature;
    const description = document.createElement("span");
    description.textContent = item.description;
    feature.append(name, description);

    const track = document.createElement("div");
    track.className = "importance-score-track";
    track.setAttribute("role", "img");
    track.setAttribute("aria-label", `${item.feature}: mean Average Precision change ${formatImportanceScore(item.importance_mean)} after shuffling`);
    const bar = document.createElement("span");
    const width = Math.abs(item.importance_mean) / maximumAbsoluteImportance * 50;
    bar.className = `importance-score-bar${item.importance_mean < 0 ? " is-negative" : ""}`;
    bar.style.width = `${width}%`;
    if (item.importance_mean < 0) bar.style.right = "50%";
    track.append(bar);

    const score = document.createElement("div");
    score.className = "model-importance-score";
    const mean = document.createElement("strong");
    mean.textContent = formatImportanceScore(item.importance_mean);
    const spread = document.createElement("span");
    spread.textContent = `SD ${formatImportanceScore(item.importance_std)} across ${formatCount(reference.repeats)} shuffles`;
    score.append(mean, spread);
    row.append(feature, track, score);
    return row;
  });
  elements.modelImportanceChart.replaceChildren(...rows);
  elements.importanceReferenceNote.textContent =
    `Reference: ${reference.evaluation_reference}. Scores are mean Average Precision change across ${formatCount(reference.repeats)} shuffles (random seed ${reference.random_state}); the SD describes variation across those repeats, not a confidence interval. Bar lengths are relative to the largest absolute mean in this top-ten view. This fixed reference is not recalculated from the uploaded portfolio.`;
}

function renderFeatureInsights(rows, importanceReference) {
  elements.featureInsightsCount.textContent = `${formatCount(rows.length)} customers`;
  renderRepaymentStatusDistribution(rows);
  renderMonthlyAmountSummary(rows, "bill", elements.monthlyBillSummary);
  renderMonthlyAmountSummary(rows, "payment", elements.monthlyPaymentSummary);
  renderModelImportance(importanceReference);
}

function renderMetricCards(result) {
  const capacity = result.capacity;
  const summary = result.portfolio_summary.probability_summary;
  const metrics = [
    { label: "Customers scored", value: formatCount(result.population_count), help: "Full uploaded portfolio", icon: "▦" },
    { label: "Mean predicted risk", value: formatPercent(summary.mean), help: "Average model estimate", icon: "⌁" },
    { label: "Selected for review", value: formatCount(capacity.selected_count), help: "Under the supplied capacity", icon: "✓" },
    { label: "Unused capacity", value: formatCount(capacity.unused_capacity), help: "After tie-aware selection", icon: "↗" },
  ];

  elements.metrics.replaceChildren(...metrics.map((metric) => {
    const card = document.createElement("article");
    card.className = "metric-card";
    card.innerHTML = `
      <div class="metric-card-top">
        <span class="metric-label">${metric.label}</span>
        <span class="metric-icon" aria-hidden="true">${metric.icon}</span>
      </div>
      <strong class="metric-value">${metric.value}</strong>
      <span class="metric-help">${metric.help}</span>
    `;
    return card;
  }));
}

function renderRiskBands(summary) {
  const bands = summary.risk_bands;
  elements.riskBands.replaceChildren(...bands.map((band) => {
    const row = document.createElement("div");
    row.className = "band-row";
    row.dataset.band = band.label;
    row.setAttribute("role", "listitem");

    const label = document.createElement("span");
    label.className = "band-label";
    label.textContent = band.label;

    const track = document.createElement("span");
    track.className = "band-track";
    track.setAttribute("aria-hidden", "true");
    const fill = document.createElement("span");
    fill.className = "band-fill";
    fill.style.width = `${Math.max(0, Math.min(1, band.portfolio_share)) * 100}%`;
    track.append(fill);

    const value = document.createElement("span");
    value.className = "band-value";
    value.innerHTML = `<strong>${formatCount(band.customer_count)}</strong> <span>· ${formatPercent(band.portfolio_share)}</span>`;
    row.append(label, track, value);
    return row;
  }));
  elements.riskReference.textContent = `${summary.risk_band_reference}. The fixed validation-cohort method is descriptive; these bands are not action thresholds.`;
}

function renderCapacity(result) {
  const capacity = result.capacity;
  const denominator = capacity.target_review_count;
  const utilization = denominator > 0 ? capacity.selected_count / denominator : 0;
  const safeUtilization = Math.max(0, Math.min(1, utilization));
  const percentage = denominator > 0 ? Math.round(safeUtilization * 100) : null;
  const degrees = safeUtilization * 360;

  elements.capacityRing.style.background = `conic-gradient(#438675 0deg ${degrees}deg, #e8efeb ${degrees}deg 360deg)`;
  elements.capacityPercent.textContent = percentage === null ? "—" : `${percentage}%`;

  const items = [
    { label: "Requested", count: capacity.requested_review_count, note: "Analyst capacity" },
    { label: "Selected", count: capacity.selected_count, note: "Entered the queue" },
    { label: "Unused", count: capacity.unused_capacity, note: "Tie-aware remainder" },
  ];
  elements.capacityLegend.replaceChildren(...items.map((item) => {
    const entry = document.createElement("div");
    entry.className = "legend-item";
    const dot = document.createElement("span");
    dot.className = "legend-dot";
    dot.setAttribute("aria-hidden", "true");
    const copy = document.createElement("span");
    copy.className = "legend-copy";
    const strong = document.createElement("strong");
    strong.textContent = `${item.label}: ${formatCount(item.count)}`;
    const note = document.createElement("span");
    note.textContent = item.note;
    copy.append(strong, note);
    entry.append(dot, copy);
    return entry;
  }));

  if (denominator === 0) {
    elements.capacityFootnote.textContent = "No review capacity was requested; no customers were selected.";
  } else if (capacity.unused_capacity > 0) {
    elements.capacityFootnote.textContent = "Some capacity remained unused because the queue keeps equal-score customers together at the selection boundary.";
  } else {
    elements.capacityFootnote.textContent = "The requested target was filled. Equal-score groups are kept together at the selection boundary.";
  }
}

function getRiskBand(record) {
  const score = record.predicted_default_probability;
  return currentResult.portfolio_summary.risk_bands.find((band) =>
    (band.lower_bound_exclusive === null || score > band.lower_bound_exclusive)
    && (band.upper_bound_inclusive === null || score <= band.upper_bound_inclusive)
  )?.label ?? "Unassigned";
}

function resetExploreFilters() {
  elements.customerIdFilter.value = "";
  elements.scoreMinFilter.value = "0";
  elements.scoreMaxFilter.value = "1";
  elements.riskBandFilter.value = "";
  elements.reviewStatusFilter.value = "";
  elements.featureFilter.value = "";
  elements.featureValueControl.replaceChildren();
  elements.featureValueControl.hidden = true;
  elements.filterMessage.textContent = "";
  currentPage = 0;
}

function initializeExploreFields() {
  const fields = dashboardConfig.required_columns.filter((field) => field !== "ID");
  elements.featureFilter.replaceChildren(new Option("No input filter", ""));
  elements.groupByField.replaceChildren(...fields.map((field) => new Option(field, field)));
  elements.featureFilter.append(...fields.map((field) => new Option(field, field)));
  elements.groupByField.value = "SEX";
}

function renderFeatureValueControl() {
  const field = elements.featureFilter.value;
  elements.featureValueControl.replaceChildren();
  if (!field || !currentPortfolio.length) {
    elements.featureValueControl.hidden = true;
    return;
  }
  elements.featureValueControl.hidden = false;
  if (CATEGORICAL_FIELDS.has(field)) {
    const label = document.createElement("label");
    label.className = "filter-control";
    const title = document.createElement("span");
    title.textContent = `${field} value`;
    const select = document.createElement("select");
    select.id = "feature-filter-value";
    select.append(new Option("All values", ""));
    [...new Set(currentPortfolio.map((row) => row[field]))]
      .sort((left, right) => left - right)
      .forEach((value) => select.append(new Option(String(value), String(value))));
    select.addEventListener("change", () => runExploreFilters(true));
    label.append(title, select);
    elements.featureValueControl.append(label);
    return;
  }

  const values = currentPortfolio.map((row) => row[field]);
  const minimum = Math.min(...values);
  const maximum = Math.max(...values);
  const label = document.createElement("span");
  label.textContent = `${field} range`;
  const inputs = document.createElement("div");
  inputs.className = "feature-range-inputs";
  for (const [caption, id, value] of [["Min", "feature-filter-min", minimum], ["Max", "feature-filter-max", maximum]]) {
    const inputLabel = document.createElement("label");
    inputLabel.className = "visually-hidden";
    inputLabel.htmlFor = id;
    inputLabel.textContent = `${field} ${caption.toLowerCase()}`;
    const input = document.createElement("input");
    input.type = "number";
    input.id = id;
    input.step = "any";
    input.value = String(value);
    input.dataset.bound = caption.toLowerCase();
    input.addEventListener("input", () => runExploreFilters(true));
    inputs.append(inputLabel, input);
  }
  elements.featureValueControl.append(label, inputs);
}

function numericQuantile(values, proportion) {
  const sorted = [...values].sort((left, right) => left - right);
  const position = (sorted.length - 1) * proportion;
  const lower = Math.floor(position);
  const fraction = position - lower;
  return sorted[lower + 1] === undefined
    ? sorted[lower]
    : sorted[lower] + fraction * (sorted[lower + 1] - sorted[lower]);
}

function getQuartileBoundaries(field) {
  if (!quartileBoundaryCache.has(field)) {
    const values = currentPortfolio.map((row) => row[field]);
    quartileBoundaryCache.set(field, [
      numericQuantile(values, 0.25),
      numericQuantile(values, 0.5),
      numericQuantile(values, 0.75),
    ]);
  }
  return quartileBoundaryCache.get(field);
}

function getQuartileIndex(value, field) {
  const [first, second, third] = getQuartileBoundaries(field);
  if (value <= first) return 0;
  if (value <= second) return 1;
  if (value <= third) return 2;
  return 3;
}

function getGroupLabel(value, field, index = null) {
  if (CATEGORICAL_FIELDS.has(field)) return String(value);
  const [first, second, third] = getQuartileBoundaries(field);
  const formatBoundary = (boundary) => boundary.toLocaleString(undefined, { maximumSignificantDigits: 7 });
  if (index === 0) return `≤ ${formatBoundary(first)}`;
  if (index === 1) return `${formatBoundary(first)} – ${formatBoundary(second)}`;
  if (index === 2) return `${formatBoundary(second)} – ${formatBoundary(third)}`;
  return `> ${formatBoundary(third)}`;
}

function applyExploreFilters() {
  const idQuery = elements.customerIdFilter.value.trim();
  const minimumScore = elements.scoreMinFilter.value === "" ? 0 : Number(elements.scoreMinFilter.value);
  const maximumScore = elements.scoreMaxFilter.value === "" ? 1 : Number(elements.scoreMaxFilter.value);
  if (minimumScore > maximumScore) {
    elements.filterMessage.textContent = "Minimum predicted risk must not exceed maximum predicted risk.";
    return null;
  }
  elements.filterMessage.textContent = "";
  const band = elements.riskBandFilter.value;
  const reviewStatus = elements.reviewStatusFilter.value;
  const field = elements.featureFilter.value;
  const categoryValue = document.querySelector("#feature-filter-value")?.value ?? "";
  const featureMinimum = document.querySelector("#feature-filter-min")?.value;
  const featureMaximum = document.querySelector("#feature-filter-max")?.value;

  return currentPortfolio.filter((record) => {
    const score = record.predicted_default_probability;
    if (idQuery && !String(record.customer_id).includes(idQuery)) return false;
    if (score < minimumScore || score > maximumScore) return false;
    if (band && getRiskBand(record) !== band) return false;
    if (reviewStatus === "selected" && !record.selected_for_review) return false;
    if (reviewStatus === "not-selected" && record.selected_for_review) return false;
    if (field && CATEGORICAL_FIELDS.has(field) && categoryValue && String(record[field]) !== categoryValue) return false;
    if (field && !CATEGORICAL_FIELDS.has(field)) {
      if (featureMinimum !== undefined && featureMinimum !== "" && record[field] < Number(featureMinimum)) return false;
      if (featureMaximum !== undefined && featureMaximum !== "" && record[field] > Number(featureMaximum)) return false;
    }
    return true;
  });
}

function renderScoreDistribution(rows) {
  const bins = Array.from({ length: 10 }, (_, index) => ({
    lower: index / 10,
    upper: (index + 1) / 10,
    count: 0,
  }));
  rows.forEach((record) => {
    const index = Math.min(9, Math.floor(record.predicted_default_probability * 10));
    bins[index].count += 1;
  });
  const denominator = rows.length;
  elements.scoreDistribution.replaceChildren(...bins.map((bin) => {
    const row = document.createElement("div");
    row.className = "distribution-row";
    row.setAttribute("role", "listitem");
    const label = document.createElement("span");
    label.className = "distribution-label";
    label.textContent = `${Math.round(bin.lower * 100)}–${Math.round(bin.upper * 100)}%`;
    const track = document.createElement("span");
    track.className = "distribution-track";
    track.setAttribute("aria-hidden", "true");
    const fill = document.createElement("span");
    fill.className = "distribution-fill";
    const share = denominator ? bin.count / denominator : 0;
    fill.style.width = `${share * 100}%`;
    track.append(fill);
    const value = document.createElement("span");
    value.className = "distribution-value";
    value.textContent = `${formatCount(bin.count)} · ${formatPercent(share)}`;
    row.append(label, track, value);
    return row;
  }));
}

function renderGroupSummary(rows) {
  const field = elements.groupByField.value;
  if (!rows.length) {
    const emptyRow = document.createElement("tr");
    const message = document.createElement("td");
    message.colSpan = 5;
    message.textContent = "No customers match the current filters.";
    emptyRow.append(message);
    elements.groupSummaryBody.replaceChildren(emptyRow);
    elements.groupTableNote.textContent = "Adjust or reset the filters to compare groups.";
    return;
  }
  const groups = new Map();
  rows.forEach((record) => {
    const groupKey = CATEGORICAL_FIELDS.has(field)
      ? String(record[field])
      : String(getQuartileIndex(record[field], field));
    if (!groups.has(groupKey)) {
      const groupIndex = CATEGORICAL_FIELDS.has(field) ? null : Number(groupKey);
      groups.set(groupKey, { label: getGroupLabel(record[field], field, groupIndex), records: [] });
    }
    groups.get(groupKey).records.push(record);
  });
  const orderedGroups = [...groups.entries()].sort((left, right) => {
    if (CATEGORICAL_FIELDS.has(field)) return Number(left[0]) - Number(right[0]);
    return Number(left[0]) - Number(right[0]);
  });
  elements.groupSummaryBody.replaceChildren(...orderedGroups.map(([, group]) => {
    const { label, records } = group;
    const row = document.createElement("tr");
    const values = [
      label,
      formatCount(records.length),
      formatPercent(rows.length ? records.length / rows.length : 0),
      formatPercent(records.reduce((sum, item) => sum + item.predicted_default_probability, 0) / records.length),
      formatCount(records.filter((item) => item.selected_for_review).length),
    ];
    values.forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    return row;
  }));
  elements.groupTableNote.textContent = CATEGORICAL_FIELDS.has(field)
    ? `Encoded values for ${field} are shown as supplied; group shares use the filtered cohort.`
    : `Quartile boundaries for ${field} are calculated from the full portfolio; shares use the filtered cohort.`;
}

function renderCustomerTable(rows) {
  const pageCount = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  currentPage = Math.min(currentPage, pageCount - 1);
  const start = currentPage * PAGE_SIZE;
  const visibleRows = rows.slice(start, start + PAGE_SIZE);
  const tableRows = visibleRows.map((record) => {
    const row = document.createElement("tr");
    const values = [
      formatCount(record.risk_rank),
      formatCount(record.customer_id),
      formatPercent(record.predicted_default_probability),
      getRiskBand(record),
      record.selected_for_review ? "Selected" : "Not selected",
    ];
    values.forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    return row;
  });
  if (!rows.length) {
    const emptyRow = document.createElement("tr");
    const message = document.createElement("td");
    message.colSpan = 5;
    message.textContent = "No customers match the current filters.";
    emptyRow.append(message);
    tableRows.push(emptyRow);
  }
  elements.customerResultsBody.replaceChildren(...tableRows);
  const first = rows.length ? start + 1 : 0;
  const last = Math.min(start + PAGE_SIZE, rows.length);
  elements.pageCount.textContent = `${formatCount(first)}–${formatCount(last)} of ${formatCount(rows.length)}`;
  elements.pageStatus.textContent = `Page ${currentPage + 1} of ${pageCount}`;
  elements.previousPage.disabled = currentPage === 0;
  elements.nextPage.disabled = currentPage >= pageCount - 1;
}

function runExploreFilters(resetPage = false) {
  if (resetPage) currentPage = 0;
  const rows = applyExploreFilters();
  if (rows === null) return;
  filteredPortfolio = rows;
  elements.exploreCount.textContent = `${formatCount(rows.length)} of ${formatCount(currentPortfolio.length)} customers`;
  renderScoreDistribution(rows);
  renderGroupSummary(rows);
  renderCustomerTable(rows);
}

function renderQueueView(result) {
  const capacity = result.capacity;
  queuePage = 0;
  elements.queuePopulationCount.textContent = `${formatCount(result.population_count)} customers scored`;
  const utilization = capacity.target_review_count > 0
    ? formatPercent(capacity.selected_count / capacity.target_review_count)
    : "—";
  const metrics = [
    { label: "Requested capacity", value: formatCount(capacity.requested_review_count), help: "Analyst-entered limit" },
    { label: "Target count", value: formatCount(capacity.target_review_count), help: "Capped at portfolio size" },
    { label: "Selected for review", value: formatCount(capacity.selected_count), help: `${utilization} of target filled` },
    { label: "Unused capacity", value: formatCount(capacity.unused_capacity), help: "Target minus selected" },
  ];
  elements.queueMetricGrid.replaceChildren(...metrics.map((metric) => {
    const card = document.createElement("article");
    card.className = "metric-card queue-metric-card";
    const label = document.createElement("span");
    label.className = "metric-label";
    label.textContent = metric.label;
    const value = document.createElement("strong");
    value.className = "metric-value";
    value.textContent = metric.value;
    const help = document.createElement("span");
    help.className = "metric-help";
    help.textContent = metric.help;
    card.append(label, value, help);
    return card;
  }));

  const reasonGroups = new Map();
  result.customers.forEach((record) => {
    if (!reasonGroups.has(record.reason_code)) {
      reasonGroups.set(record.reason_code, { reason: record.reason, count: 0 });
    }
    reasonGroups.get(record.reason_code).count += 1;
  });
  elements.queueReasonsBody.replaceChildren(...[...reasonGroups.values()].map((group) => {
    const row = document.createElement("tr");
    const reason = document.createElement("td");
    reason.textContent = group.reason;
    const count = document.createElement("td");
    count.textContent = formatCount(group.count);
    row.append(reason, count);
    return row;
  }));
  renderSelectedQueue(result.customers.filter((record) => record.selected_for_review));
}

function renderSelectedQueue(selectedCustomers) {
  const pageCount = Math.max(1, Math.ceil(selectedCustomers.length / PAGE_SIZE));
  queuePage = Math.min(queuePage, pageCount - 1);
  const start = queuePage * PAGE_SIZE;
  const currentRows = selectedCustomers.slice(start, start + PAGE_SIZE);
  const rows = currentRows.map((record) => {
    const row = document.createElement("tr");
    [
      formatCount(record.risk_rank),
      formatCount(record.customer_id),
      formatPercent(record.predicted_default_probability),
      record.reason,
    ].forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    });
    return row;
  });
  if (!selectedCustomers.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 4;
    cell.textContent = "No customers were selected under this capacity.";
    row.append(cell);
    rows.push(row);
  }
  elements.selectedQueueBody.replaceChildren(...rows);
  const first = selectedCustomers.length ? start + 1 : 0;
  const last = Math.min(start + PAGE_SIZE, selectedCustomers.length);
  elements.queuePageCount.textContent = `${formatCount(first)}–${formatCount(last)} of ${formatCount(selectedCustomers.length)}`;
  elements.queuePageStatus.textContent = `Page ${queuePage + 1} of ${pageCount}`;
  elements.queuePreviousPage.disabled = queuePage === 0;
  elements.queueNextPage.disabled = queuePage >= pageCount - 1;
}

function setActiveView(view) {
  if (view !== "overview" && !currentResult) return;
  activeView = view;
  elements.results.hidden = view !== "overview" || !currentResult;
  elements.exploreView.hidden = view !== "explore" || !currentResult;
  elements.queueView.hidden = view !== "queue" || !currentResult;
  elements.featureInsightsView.hidden = view !== "feature-insights" || !currentResult;
  elements.emptyState.hidden = Boolean(currentResult);
  elements.viewLinks.forEach((link) => {
    const active = link.dataset.view === view;
    link.classList.toggle("is-active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  const viewLabels = {
    overview: "Overview",
    explore: "Explore portfolio",
    queue: "Review queue",
    "feature-insights": "Feature insights",
  };
  document.querySelector(".breadcrumb").lastChild.textContent = ` ${viewLabels[view]}`;
}

function renderOverview(result, inputRows) {
  currentResult = result;
  const inputsById = new Map(inputRows.map((row) => [row.ID, row]));
  currentPortfolio = result.customers.map((scoredRow) => ({
    ...inputsById.get(scoredRow.customer_id),
    ...scoredRow,
  }));
  quartileBoundaryCache.clear();
  initializeExploreFields();
  resetExploreFilters();
  renderQueueView(result);
  renderSelectionProfile(currentPortfolio);
  renderFeatureInsights(currentPortfolio, dashboardConfig?.model_feature_importance);
  renderMetricCards(result);
  renderRiskBands(result.portfolio_summary);
  renderCapacity(result);
  elements.portfolioCount.textContent = `${formatCount(result.population_count)} customers`;
  elements.analysisMetaText.textContent = `Scored ${new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}`;
  elements.analysisMeta.hidden = false;
  runExploreFilters();
  setActiveView("overview");
  elements.results.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function readSelectedFile() {
  if (!selectedFile) throw new Error("Choose a CSV file before running the analysis.");
  const text = await selectedFile.text();
  return validateCsvRows(parseCsv(text));
}

async function loadDashboardConfig() {
  const response = await fetch("/v1/dashboard-config");
  if (!response.ok) throw new Error("The dashboard couldn’t load its setup details. Refresh and try again.");
  dashboardConfig = await response.json();
  elements.fileHint.textContent = `ID and all 23 predictors · up to ${formatCount(dashboardConfig.max_customer_rows)} customers`;
  elements.capacity.max = String(dashboardConfig.max_customer_rows);
}

async function checkService() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("Portfolio scoring is temporarily unavailable.");
    const health = await response.json();
    if (!health.model_loaded) throw new Error("Portfolio scoring isn’t ready yet. Try again shortly.");
    setServiceStatus(true, "Ready to score portfolios");
  } catch (error) {
    setServiceStatus(false, "Portfolio scoring is temporarily unavailable.");
  }
}

elements.file.addEventListener("change", () => {
  selectedFile = elements.file.files?.[0] ?? null;
  clearMessage();
  if (selectedFile) {
    elements.fileName.textContent = selectedFile.name;
    elements.fileHint.textContent = `${(selectedFile.size / 1024).toFixed(0)} KB · ready to validate`;
    elements.fileName.title = selectedFile.name;
  } else {
    elements.fileName.textContent = "Choose a CSV file";
  }
});

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearMessage();
  elements.runButton.disabled = true;
  elements.runButton.querySelector("span:first-child").textContent = "Scoring portfolio…";

  try {
    if (!dashboardConfig) await loadDashboardConfig();
    const customers = await readSelectedFile();
    if (elements.capacity.value.trim() === "") {
      throw new Error("Enter a review capacity.");
    }
    const capacity = Number(elements.capacity.value);
    if (!Number.isSafeInteger(capacity) || capacity < 0) {
      throw new Error("Review capacity must be a non-negative whole number.");
    }

    const response = await fetch("/v1/review-queue", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ customers, max_review_count: capacity }),
    });
    const payload = await response.json();
    if (!response.ok) {
      const details = payload?.error?.details?.filter(Boolean).join(" ");
      throw new Error(details || payload?.error?.message || "The scoring request failed.");
    }

    renderOverview(payload, customers);
    setServiceStatus(true, "Ready to score portfolios");
    showMessage(`Analysis complete for ${formatCount(payload.population_count)} customers.`, "success");
  } catch (error) {
    const message = error instanceof TypeError
      ? "Portfolio scoring is temporarily unavailable. Check your connection and try again."
      : error.message || "The portfolio could not be scored.";
    showMessage(message);
  } finally {
    elements.runButton.disabled = false;
    elements.runButton.querySelector("span:first-child").textContent = "Run analysis";
  }
});

elements.healthCheck.addEventListener("click", checkService);

elements.viewLinks.forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    setActiveView(link.dataset.view);
    if (currentResult) window.location.hash = link.dataset.view;
  });
});

[
  elements.customerIdFilter,
  elements.scoreMinFilter,
  elements.scoreMaxFilter,
  elements.riskBandFilter,
  elements.reviewStatusFilter,
].forEach((control) => control.addEventListener("input", () => runExploreFilters(true)));
[
  elements.riskBandFilter,
  elements.reviewStatusFilter,
].forEach((control) => control.addEventListener("change", () => runExploreFilters(true)));
elements.featureFilter.addEventListener("change", () => {
  renderFeatureValueControl();
  runExploreFilters(true);
});
elements.groupByField.addEventListener("change", () => runExploreFilters(true));
elements.resetFilters.addEventListener("click", () => {
  resetExploreFilters();
  runExploreFilters(true);
});
elements.previousPage.addEventListener("click", () => {
  currentPage = Math.max(0, currentPage - 1);
  renderCustomerTable(filteredPortfolio);
});
elements.nextPage.addEventListener("click", () => {
  currentPage += 1;
  renderCustomerTable(filteredPortfolio);
});
elements.queuePreviousPage.addEventListener("click", () => {
  queuePage = Math.max(0, queuePage - 1);
  renderSelectedQueue(currentResult.customers.filter((record) => record.selected_for_review));
});
elements.queueNextPage.addEventListener("click", () => {
  queuePage += 1;
  renderSelectedQueue(currentResult.customers.filter((record) => record.selected_for_review));
});

loadDashboardConfig()
  .then(checkService)
  .catch(() => setServiceStatus(false, "Portfolio scoring is temporarily unavailable."));
```

---

<a id="step-9-10"></a>
## Step 9.10

# Phase 9 · Step 9.10: Customer drilldown and local explanation

## Decision

Use the existing Phase 6 grouped interventional Shapley implementation, paired with the prediction-time profile. The API reuses the fitted estimator and a fixed sample from the established training partition. It does not fit a model or use the uploaded portfolio as its comparison baseline for each click. The explanation stays descriptive: attribution describes the model's behavior under constructed feature substitutions, not a cause or an intervention effect.

## What the analyst sees

The Explore table and selected queue each have an **Inspect** action. The detail dialog shows the supplied input values, model estimate, training-reference mean, contribution by each of the four pre-existing feature groups, queue rank, selection status/reason, method, reference sample size, and limitations. Encoded values remain codes as supplied.

## Request flow

1. `CustomerInput` validates the same one-row input schema used for scoring; extra fields such as `DEFAULT` are rejected.
2. `ReviewQueueService.explain_customer` passes the row, preloaded estimator, and repository's cached training split to `explain_customer_prediction`.
3. The existing explainer computes grouped attributions and returns the model probability difference from the reference mean.
4. The browser constructs the dialog with text nodes, avoiding HTML injection, and reports an API error within the dialog.

## Code walkthrough

`ModelArtifactRepository.get_explanation_background` loads the processed dataset when available (or builds it from the project's source data), applies the same deterministic split function, and caches `X_train`. The cache keeps repeated inspections from repeating data preparation. `ReviewQueueService.explain_customer` calls the already fitted estimator in the artifact. `POST /v1/customer-explanation` exposes only the one-row explanation result. The frontend's `showCustomerDetail` sends only contract input columns and displays profile and explanation separately.

The `CustomerExplanationResponse` and `LocalContribution` Pydantic models define response types. The complete changed implementation is in:

- `src/propensity_prediction/api/repository.py`
- `src/propensity_prediction/api/schemas.py`
- `src/propensity_prediction/api/service.py`
- `src/propensity_prediction/api/routes.py`
- `src/propensity_prediction/dashboard/static/app.js`
- `src/propensity_prediction/dashboard/static/index.html`

### Core service code

```python
def explain_customer(self, customer: CustomerInput) -> dict:
    artifact = self.model_repository.get_model_artifact()
    row = pd.DataFrame([customer.model_dump()])
    explanation = explain_customer_prediction(
        model=artifact["estimator"],
        customer=row,
        background=self.model_repository.get_explanation_background(),
    )
    return {
        "customer_id": customer.ID,
        "estimated_default_probability": explanation.predicted_probability,
        "reference_probability": explanation.baseline_probability,
        "difference_from_reference": (
            explanation.predicted_probability - explanation.baseline_probability
        ),
        "method": explanation.method,
        "background_size": explanation.background_size,
        "contributions": explanation.contributions.to_dict(orient="records"),
        "limitations": (
            "Grouped model attributions compare this record with a fixed sample "
            "from the training partition. They describe model behavior, not "
            "causes, outcomes, or intervention effects."
        ),
    }
```

The route binds this method to `POST /v1/customer-explanation`; the response
schema validates the probability, background size, and each group contribution.
Repository background loading is cached:

```python
def get_explanation_background(self) -> pd.DataFrame:
    if self._explanation_background is None:
        dataset = (
            pd.read_csv(PROCESSED_DATA_PATH)
            if PROCESSED_DATA_PATH.is_file()
            else build_processed_dataset()
        )
        split = split_dataset(dataset)
        self._explanation_background = split.X_train.reset_index(drop=True)
    return self._explanation_background
```

The frontend action sends `dashboardConfig.required_columns` only and builds
the profile from text nodes. The complete helper, dialog markup, and event
handlers are in the linked source files above; those files are the full
authoritative listings, including existing dashboard code surrounding this
addition.

## Limits and validation

The score remains an estimate of next-month default probability. Local attribution does not establish why a real customer will default, causal effect, fairness, or an intervention recommendation. The app uses the model artifact's fitted estimator; startup explanation-reference preparation depends on the original processed/raw project dataset being available. Python compilation and the project suite were run as part of Step 9.14.

---

<a id="step-9-11"></a>
## Step 9.11

# Phase 9 · Step 9.11: Segment policy and responsible-use safeguards

## Decision

Keep `SEX`, `EDUCATION`, and `MARRIAGE` in the scoring input contract because the selected model requires them. Do not expose those attributes as dashboard cohort filters or group-by comparisons in this phase. They are not needed to understand the operational queue, and simple score comparisons would not be a fairness evaluation. No fairness claim or certification is made.

## What changed

The dashboard's field picker omits those three sensitive/demographic fields, while the model input validation remains unchanged. Repayment-status codes remain available for descriptive analysis and are displayed as supplied, without inventing category labels. Existing responsible-use notes clarify that descriptive group differences do not establish causes, outcomes, intervention effects, or fairness conclusions.

## Code walkthrough

`DASHBOARD_FIELDS` contains the three fields intentionally withheld from analysis controls. `initializeExploreFields()` filters the API-required input list against both `ID` and that set. The list of all required columns still feeds CSV validation and prediction payloads, so removing a field from the view cannot silently remove a model predictor. The categorical chart set retains only repayment status values. The field allowlist is applied to both the filter picker and the group-by selector.

```javascript
const CATEGORICAL_FIELDS = new Set([
  "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
]);
const DASHBOARD_FIELDS = new Set(["SEX", "EDUCATION", "MARRIAGE"]);

function initializeExploreFields() {
  const fields = dashboardConfig.required_columns.filter(
    (field) => field !== "ID" && !DASHBOARD_FIELDS.has(field),
  );
  elements.featureFilter.replaceChildren(new Option("No input filter", ""));
  elements.groupByField.replaceChildren(...fields.map((field) => new Option(field, field)));
  elements.featureFilter.append(...fields.map((field) => new Option(field, field)));
  elements.groupByField.value = "PAY_0";
}
```

## Complete implementation locations

- `src/propensity_prediction/dashboard/static/app.js`: `DASHBOARD_FIELDS`, `CATEGORICAL_FIELDS`, and `initializeExploreFields()`.
- `src/propensity_prediction/dashboard/static/index.html`: interpretation note.
- `Phase 9 Plan` (included in the combined document above): chosen policy and rationale.

## Interpretation boundary

This is a conservative dashboard presentation policy, not a legal determination and not proof the model is fair. A later fairness study needs an explicit objective, suitable outcome labels, an approved methodology, sample-size handling, and review before conclusions are drawn.

---

<a id="step-9-12"></a>
## Step 9.12

# Phase 9 · Step 9.12: Analyst exports

## Decision

Provide three downloads: the currently filtered cohort, the full scored ranking, and the selected review queue. Defer saved views because there is no user identity or persistence layer. Keep exports local to the browser and scoped to the most recent completed run.

## Export contents

Each CSV contains the 23 prediction-time predictors and customer ID, predicted default probability, risk rank, reference risk band, selection flag, reason code, and reason. Metadata rows record scope, generated time, portfolio size, requested review capacity, and explicitly state that historical outcomes are excluded. `DEFAULT` is never added. The filtered export reflects current Explore filters; ranking and queue exports use the entire last run.

## Code walkthrough

`csvCell()` quotes every value, doubles embedded quotes, and prefixes spreadsheet formula-leading text. `exportRows()` constructs a fixed-schema record from allowed predictor columns plus the scoring/decision outputs; it does not serialize arbitrary object properties. `downloadCsv()` creates a UTF-8 CSV with a byte-order mark for common spreadsheet compatibility, triggers a browser download, and releases its object URL. The three buttons call the same serializer with distinct row sets and filenames. They are disabled until a completed portfolio exists.

```javascript
function exportRows(rows, filename, scope) {
  const fields = [...dashboardConfig.required_columns];
  const exports = rows.map((record) => ({
    ...Object.fromEntries(fields.map((field) => [field, record[field]])),
    predicted_default_probability: record.predicted_default_probability,
    risk_rank: record.risk_rank,
    risk_band: getRiskBand(record),
    selected_for_review: record.selected_for_review,
    reason_code: record.reason_code,
    reason: record.reason,
  }));
  downloadCsv(filename, exports, [
    ["Export scope", scope], ["Generated at", new Date().toISOString()],
    ["Portfolio size", currentPortfolio.length],
    ["Review capacity", currentResult.capacity.requested_review_count],
    ["Historical outcome fields included", "No"],
  ]);
}
```

The serializer creates a single rectangular CSV: metadata is represented as
columns, including for an empty filtered selection. Numeric values remain
numeric (including negative statement amounts), while formula-like text is
escaped. The button handlers select `filteredPortfolio`, `currentPortfolio`,
or the selected subset from that same scored run.

## Complete implementation locations

- `src/propensity_prediction/dashboard/static/app.js`: `csvCell`, `downloadCsv`, `exportRows`, and export listeners.
- `src/propensity_prediction/dashboard/static/index.html`: download controls.
- `src/propensity_prediction/dashboard/static/styles.css`: responsive workflow controls.

## Data boundary

The user-supplied input schema already rejects extra columns, including `DEFAULT`; exports use only contract columns and generated outputs. No outcome label, actual performance, or unsupported intervention field is exported.

---

<a id="step-9-13"></a>
## Step 9.13

# Phase 9 · Step 9.13: Accessibility and responsive polish

## Decision

Continue the dashboard's existing small custom visual system instead of adding a component dependency. Apply consistent keyboard focus, disabled control behavior, responsive detail layouts, and semantic dialog behavior across the new customer inspection and export controls.

## What changed

- Customer detail opens in a native modal dialog with a labelled title, close button, and polite loading/result region.
- Each row action has a customer-specific accessible name; the dialog is keyboard-operable and can be dismissed with standard dialog keyboard behavior.
- Focus receives a visible high-contrast outline; disabled controls communicate their state.
- Detail input values reflow from four columns to two on small screens.
- New workflow action groups wrap/stack on narrow screens; the dialog has a viewport-constrained height and scrolls internally.
- Generated profile and attribution content is inserted as text, not HTML.

## Code walkthrough

The semantic `<dialog>` keeps the detail panel in the browser's modal interaction model. `showCustomerDetail()` creates `dt`, `dd`, headings, list items, and caveat paragraphs with DOM APIs. `aria-live` communicates asynchronous updates; `role="alert"` announces a failed explanation request. CSS `:focus-visible`, the backdrop, and breakpoints add visible focus and smaller-screen behavior.

```css
:focus-visible { outline: 3px solid #438675; outline-offset: 3px; }
.customer-dialog {
  width: min(760px, calc(100vw - 28px));
  max-height: min(88vh, 900px);
  overflow: auto;
  padding: 24px;
  border: 1px solid var(--line);
  border-radius: 18px;
}
.detail-profile { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); }
@media (max-width: 560px) {
  .detail-profile { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .workflow-actions { align-items: flex-start; flex-direction: column; }
}
```

The markup's `aria-labelledby` connects the dialog to its title; detail action
buttons name the inspected customer; and the result region uses `aria-live`
for asynchronous status. The complete HTML/CSS/JavaScript source is linked
below, including context needed to understand how these additions fit each
view.

## Complete implementation locations

- `src/propensity_prediction/dashboard/static/index.html`: dialog markup and table action headers.
- `src/propensity_prediction/dashboard/static/app.js`: accessible action labels, modal lifecycle, loading/error states.
- `src/propensity_prediction/dashboard/static/styles.css`: focus, dialog, and responsive rules.

## Review boundary

Automated syntax and project tests do not replace a screen-reader audit. The modal uses native `<dialog>` support in current desktop browsers; assistive technology and small-screen manual walkthroughs are included in Step 9.14 where a live browser is available.

---

<a id="step-9-14"></a>
## Step 9.14

# Phase 9 · Step 9.14: Integration, validation, and closeout

## Approach

Combine focused checks with the complete project test suite, following the agreed recommendation. The work verifies contracts and syntax as well as the existing data, model, decision, and dashboard behavior.

## Automated checks

- JavaScript parser check: `node --check src/propensity_prediction/dashboard/static/app.js`.
- Python compilation for the API modules changed for customer explanations.
- Complete project test suite: `venv/bin/python -m pytest -q`.
- `git diff --check` for whitespace and patch hygiene.
- Review of API response model and browser request fields: detail requests contain only the existing required input schema; exports construct fixed output columns and no `DEFAULT`.

The final complete run passed **210 tests** in 216.43 seconds. The API and
dashboard focused subset also passed **16 tests**. JavaScript syntax checking,
Python module compilation, and `git diff --check` passed.

## Manual review scenarios

The code paths support full ranking, current filtered rows, selected queue,
empty filter matches, zero-capacity queues, queue ties, and customer detail
from both tables. A local browser could not connect to the development server
in this execution environment, so no manual modal/download or narrow-screen
interaction is claimed. The existing suite covers the dashboard contracts
and CSV validation boundaries, including the 30,000-row API limit. No
30,000-row render-time benchmark was measured. Before production use, the
browser workflow can be exercised with
`data/sample_customer_portfolio_10.csv`; Droplet performance belongs to Phase
11.

## What the dashboard establishes

It summarizes model-estimated probabilities, fixed reference risk bands, uploaded-portfolio distributions, the deterministic capacity queue, descriptive input summaries, reference model importance, and grouped local model attributions.

It does not establish actual default outcomes in a new portfolio, individual certainty, causal explanations, intervention impact, fairness, or recommended customer action. Feature importance is model-relative; local Shapley contributions depend on the selected training background and constructed comparisons.

## Phase boundary

Phase 9's implementation and automated validation are complete. Phase 10
adds the GenAI layer. Phase 11 remains the final deployment phase for the
DigitalOcean Droplet; this closeout does not deploy the application.
