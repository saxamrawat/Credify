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
