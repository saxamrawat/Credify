# Phase Document Template

Use this structure for future phase records. It gives each phase a brief overview and contents list before the detailed implementation record. Keep the step walkthroughs thorough; keep the overview concise.

```markdown
# Phase N — Phase name

## Phase overview

- **Status:** Planned, in progress, or complete.
- **Objective:** The user or analytical problem this phase addresses.
- **Scope:** The work included and the boundaries agreed for the phase.
- **Outcome and evidence:** What the phase delivered and where verification is recorded.
- **Limitations:** Evidence gaps, assumptions, and claims the work does not support.

## Contents

- [Step N.1 — Name](#step-n1--name)
- [Step N.2 — Name](#step-n2--name)

## Step N.1 — Name

### Goal
What this step is intended to accomplish.

### Decision and scope
The selected approach, options considered, tradeoffs, and agreed boundaries.

### What changed
Explain the user-visible or analytical change, why it was needed, and how it works.
Walk through the code in implementation order. Include complete changed code where
needed to support the detailed explanation.

### Verification
Record the checks performed and what they establish. State clearly when a check
was not run.

### Files changed
List the important files and their responsibilities.

### Limitations and handoff
Record remaining constraints or decisions for a later step or phase.

## Phase closeout

Summarize delivered outcomes, verification, remaining work, limitations, and the
handoff to the next phase.
```

## Documentation workflow

- Keep one detailed Markdown walkthrough for each active step.
- Use the same phase overview fields and step headings in every new phase record.
- At phase closeout, combine the step walkthroughs into one document in step order.
- Preserve all explanations and code when combining documents; update the contents list and internal links.
- Remove separate step files only after the combined document is complete and verified.

## Existing phase records

The completed Phase 4–9 records now use a common phase overview and contents entry point. Phase 10's active step walkthroughs use a consistent goal, change, rationale, files, and verification structure. Phases 0–3 remain summarized in the project README and are not represented by separate phase documents.
