# Knowledge Base Title

## W7-Base OmG Command-Flow Method for Building and Evolving the Platform

### 1. Scope

This KB covers only the **OmG-based command-flow method** used in this conversation to plan, execute, verify, stabilize, and close work on the W7-Base project.

Included:

* The staged OmG workflow model
* How commands were sequenced
* How controlled YOLO/autopilot was used
* How slices/phases were advanced safely
* How Git/state hygiene was maintained between slices
* The reusable prompting style used to drive OmG

Excluded:

* Detailed W7-Base architecture itself except where needed to explain workflow
* Linux support topics like keyboard layout or Flatpak/Input Leap
* The full platform implementation history except as workflow examples
* General chat content unrelated to OmG execution method

---

### 2. Purpose for Future LLM Use

Another LLM should use this KB as the **execution playbook** for continuing repository work in the same style as this conversation.

It provides:

* The preferred staged workflow for repo development using OmG
* The rules for when to use `status`, `plan`, `execute`, `loop`, or `autopilot`
* The safe sequencing model for multi-slice work
* The Git/state sync discipline used before and after implementation
* Prompt patterns that reliably produce controlled, high-signal execution

This KB is useful when a future LLM needs to:

* resume work on W7-Base or a similar repo
* continue structured implementation without losing state discipline
* drive OmG in a controlled YOLO mode
* convert vague goals into executable slices and command flows

---

### 3. Core Context

The conversation repeatedly used **OmG** as a command-first orchestration layer for project work. Instead of freeform coding, work was pushed through staged commands such as:

* `/omg:status`
* `/omg:plan`
* `/omg:taskboard`
* `/omg:execute`
* `/omg:loop`
* `/omg:autopilot`

The dominant pattern was:

1. reconstruct state
2. stabilize Git/workspace if needed
3. plan the next slice
4. execute one slice or a small batch of slices
5. verify outcomes
6. sync taskboard/checkpoint/workflow state
7. commit cleanly
8. only then continue

A major theme was **controlled YOLO**:

* allow autonomy within a clearly bounded slice
* enforce sequential progression
* stop on safety/trust-boundary issues
* keep Git clean
* update state files after meaningful milestones

The workflow treated slices as **operational units** that should be:

* scoped
* verified
* committed
* state-synced
  before moving on.

---

### 4. Key Concepts and Definitions

**OmG**
A command-driven workflow system used to coordinate planning, execution, verification, and state tracking.

**Slice**
A bounded implementation unit inside a broader phase. Slices were the main scope container for execution.

**Controlled YOLO / autopilot**
A mode where OmG is allowed to plan, execute, verify, and fix automatically within a limited scope, while preserving stop conditions around safety, trust boundaries, and architecture risk.

**State files**
Project coordination files such as:

* `taskboard.md`
* `checkpoint.md`
* `workflow.md`

These were treated as authoritative synchronization artifacts.

**Git stabilization**
The rule that verified work should be committed before new slices begin, especially after infrastructure or cross-lane changes.

**Lane health / clean handoff**
A discipline for avoiding dirty worktrees and overlapping work in sensitive areas like `@ops` or `.shared`.

**Sequential slice execution**
A rule that later slices should only start when the current slice is:

* implemented
* verified
* state-synced
* optionally committed

**Planning-only autopilot**
Using `/omg:autopilot` to plan a phase without implementing it yet.

---

### 5. Structured Knowledge Extraction

## 5.1. Base OmG Execution Pattern

The most reusable command-flow from the chat was:

**state reconstruction -> planning -> execution -> verification -> closure**

Typical sequence:

```text
/omg:status
/omg:plan
/omg:execute --task <task-id>
/omg:loop
```

For more autonomous work:

```text
/omg:autopilot
```

Use cases:

* `/omg:status` when the user does not know where the project stands
* `/omg:plan` when choosing the next phase/slice
* `/omg:execute` for focused, task-specific work
* `/omg:loop` to resume an active slice after a pause
* `/omg:autopilot` for bounded sequential work with explicit rules

---

## 5.2. Preferred Slice Lifecycle

The conversation converged on this slice lifecycle:

### Stage 1 — Reconstruct state

Ask OmG to summarize:

* what the project is
* current phase/slice
* what is complete
* what is verified
* what remains
* blockers/risks
* next command

### Stage 2 — Stabilize Git and lane health

Before new implementation:

* inspect Git state
* commit verified work
* resolve dirty lanes
* avoid carrying unstaged state into the next slice

### Stage 3 — Plan the next slice

Use `/omg:plan` when:

* the next slice is not yet well defined
* the phase contains multiple possible directions
* safety or sequencing needs thought first

### Stage 4 — Execute the slice

Use either:

* `/omg:execute --task <task-id>` for a narrow, explicit task
* `/omg:autopilot` for a bounded multi-step slice

### Stage 5 — Verify

Verification was often implicit inside autopilot, but the operating assumption was:

* verify implementation against acceptance criteria
* verify Git cleanliness
* verify state file sync

### Stage 6 — Close and sync

At slice closure:

* update taskboard/checkpoint/workflow
* commit if the slice produced meaningful changes
* only then move to the next slice

---

## 5.3. When to Use `execute` vs `loop` vs `autopilot`

### Use `/omg:execute`

When:

* one task remains
* scope is explicit
* the user wants a narrow execution target
* the remaining work is mostly documentation or a single implementation item

Observed pattern:

* once a slice had only one task left, `execute --task ...` was preferred over a general loop

### Use `/omg:loop`

When:

* a slice is already in progress
* the prior steps are complete
* OmG only needs to continue from the current slice state

Observed pattern:

* used after committing a blocking change to resume controlled progress

### Use `/omg:autopilot`

When:

* a whole slice or phase can proceed sequentially
* rules can be defined clearly
* the LLM should carry planning/execution/verification itself

Observed pattern:

* best for multi-slice bounded work such as:

  * Slice 13, 14, 15 sequentially
  * full Phase 8 sequentially
* always better with explicit scope and stop conditions

---

## 5.4. Controlled YOLO Rules That Recurred

The strongest recurring autopilot design pattern was:

* target a specific slice or phase
* define exact scope
* force sequential progression
* only continue if the previous slice is verified and state-synced
* stop if safety, trust-boundary, resource, or architecture issues appear
* preserve Git cleanliness
* update taskboard/checkpoint/workflow after each slice
* summarize first in Hungarian, then continue in English

This was the standard “controlled YOLO” contract.

---

## 5.5. Multi-Slice Sequential Autopilot Pattern

When the user wanted several slices completed in one run, the conversation established this correct pattern:

1. list slices in exact order
2. state that slice N+1 may begin only if slice N is:

   * implemented
   * verified
   * committed or state-synced
3. require stop-on-risk behavior
4. forbid scope expansion beyond the target phase
5. preserve current architecture and security boundaries

This prevented autopilot from blurring slice boundaries.

---

## 5.6. Git Stabilization as a Mandatory Workflow Gate

A repeated lesson:

**Do not continue implementation when verified work is still uncommitted.**

This was treated as a hard workflow rule in many places:

* before Phase 3 continuation
* before Slice 10 continuation
* before Phase expansion
* before state handoff

The workflow preference was:

* commit stabilizing changes first
* then resume `loop` or `autopilot`

This also applied to:

* dirty `@ops` lane
* dirty `.shared`
* dirty slice closure after successful validation

---

## 5.7. State Reconstruction Prompts Were Essential

When the user lost track of the project, the recommended recovery pattern was:

```text
/omg:status
Reconstruct the project state for me:
- what this project is
- what phase it is in
- what has already been implemented
- what has been verified
- what remains
- biggest risks
- best next step
- exact next command to continue
```

This became the standard “resume” pattern.

---

## 5.8. Planning Prompts Were Better Than Vague Continuations

The conversation repeatedly improved outcomes by using planning prompts with:

* phase number
* goal
* focused areas
* desired slice breakdown
* risks
* dependencies
* exact next command

The preferred plan prompt shape was:

```text
/omg:plan
First, briefly summarize in Hungarian, then continue in English.

Plan Phase X for W7-Base.

Focus areas:
- ...
- ...

Return:
- recommended Slice A, B, C structure
- why this order is best
- risks
- dependencies
- exact next command to begin execution
```

This was more effective than asking OmG to “just continue.”

---

## 5.9. Closure Discipline Was Important

The conversation treated closure as real work, not as an afterthought.

Good closure meant:

* docs updated if needed
* taskboard synced
* checkpoint/workflow synced
* Git committed
* workspace clean
* explicit statement that the slice or phase is closed

This applied both to infrastructure slices and documentation slices.

---

### 6. Decisions, Constraints, and Preferences

## Confirmed decisions

* OmG should be driven in a **workflow-first** way, not through vague conversation.
* Slice-based progression is preferred over broad, unsliced execution.
* Controlled YOLO is acceptable only with explicit scope and stop conditions.
* Git stabilization should happen before new work when verified changes are pending.
* Dirty lane health is a legitimate blocker for continuation.
* State files (`taskboard`, `checkpoint`, `workflow`) should be synchronized at each meaningful milestone.
* Multi-slice autopilot is acceptable if sequential gating is explicit.
* `execute --task` is preferred when only one explicit task remains.
* `loop` is preferred to resume an active slice after a pause/blocker resolution.
* Responses/prompts for OmG should begin with a short Hungarian summary, then continue in English.

## Preferences inferred from the conversation

* Strong preference for operational clarity over vague summaries
* Strong preference for exact next commands
* Strong preference for safe sequencing over improvisation
* Preference for additive transitions instead of destructive redesigns
* Preference for committing finished slice work before architectural expansion

## Non-negotiables

* Do not expand beyond the requested slice/phase in autopilot
* Do not weaken security or trust boundaries for convenience
* Do not continue blindly when the repo is dirty in a way that affects clean handoff
* Do not merge planning and implementation implicitly when the user asked for planning only

---

### 7. Reusable Workflows

## Workflow 1 — Resume a lost project state

1. Run `/omg:status`
2. Ask it to reconstruct:

   * project purpose
   * current phase/slice
   * completed work
   * verified work
   * remaining backlog
   * blockers/risks
   * exact next command
3. Use the result to decide whether Git stabilization is needed before continuation

## Workflow 2 — Start the next slice safely

1. Check current state with `/omg:status`
2. If Git or lane health is dirty, stabilize first
3. Use `/omg:plan` if the next slice is not fully shaped
4. Use `/omg:execute --task ...` for a narrow task
5. Use `/omg:autopilot` for a bounded slice with explicit rules
6. Verify and sync state files after completion
7. Commit verified work
8. Only then continue

## Workflow 3 — Run a whole phase in controlled YOLO

1. Define target phase and slice order
2. State exact scope per slice
3. Require sequential progression:

   * Slice N must be implemented, verified, and state-synced before Slice N+1
4. Define stop conditions:

   * safety
   * trust-boundary
   * architecture
   * resource/networking issues
5. Require Git cleanliness and state sync after each slice
6. Start with `/omg:autopilot`

## Workflow 4 — Close a slice cleanly

1. Verify that the implementation is complete
2. Update taskboard
3. Update checkpoint/workflow
4. Commit intended changes
5. Confirm workspace cleanliness
6. Mark the slice as closed before planning the next one

## Workflow 5 — Use OmG for planning only

1. Run `/omg:plan`
2. Request:

   * slice structure
   * ordering
   * risks
   * dependencies
   * exact next command
3. Explicitly say “planning only”
4. Do not begin execution until the plan is accepted

---

### 8. Reusable Assets

## Asset 1 — Resume prompt

```text
/omg:status
First, briefly summarize in Hungarian, then continue in English.

Reconstruct the project state for me:
- what this project is
- what phase it is in
- what has already been implemented
- what has been verified
- what remains
- biggest risks
- best next step
- exact next command to continue
```

## Asset 2 — Planning prompt template

```text
/omg:plan
First, briefly summarize in Hungarian, then continue in English.

Plan Phase X for <project>.

Focus areas:
- ...
- ...

Return:
- recommended slice structure
- why this order is best
- risks
- dependencies
- exact next command to begin execution
```

## Asset 3 — Single-task execution prompt

```text
/omg:execute --task <TASK-ID>

First, briefly summarize in Hungarian, then continue in English.

Complete this task within its defined slice only.
Keep Git state clean.
Update taskboard, checkpoint, and workflow state if this closes the task or slice.
```

## Asset 4 — Controlled YOLO multi-slice prompt

```text
/omg:autopilot
Continue <project> in controlled YOLO mode.

Target:
Phase X

Primary execution order:
- Slice A
- Slice B
- Slice C

Mission:
Implement the phase in a controlled sequential flow.

Execution policy:
- execute Slice A first
- only continue to Slice B if Slice A is implemented, verified, and state-synced
- only continue to Slice C if Slice B is implemented, verified, and state-synced
- stop between slices if a safety, trust-boundary, or architecture issue appears
- keep Git state clean at all times
- update taskboard, checkpoint, and workflow after each slice
- summarize first in Hungarian, then continue in English
```

## Asset 5 — Slice closure prompt

```text
/omg:status
First, briefly summarize in Hungarian, then continue in English.

Seal the current slice.
Summarize:
- what was fixed or implemented
- what was verified
- whether the slice is ready to be treated as completed
- what state files should be updated
- exact next command
```

## Asset 6 — Git stabilization rule fragment

```text
Mandatory first step:
- inspect Git status
- if verified work is still untracked or uncommitted, stage it and create a safe baseline commit
- confirm exactly what was committed
```

---

### 9. Prompt Pack for Future LLM Sessions

## Bootstrap prompt

```text
Use the attached KB as the execution playbook for OmG-driven repository work.
Preserve the workflow-first style:
- reconstruct state first
- stabilize Git if needed
- plan before broad execution
- use bounded slices
- prefer controlled YOLO with explicit stop conditions
- keep state files and Git synchronized
- summarize first in Hungarian, then continue in English
```

## Task continuation prompt

```text
Resume this repo using the OmG command-flow method from the KB.

First:
- reconstruct current state
- identify dirty Git or lane issues
- determine the current phase/slice
- recommend the exact next command

Then:
- continue only within the current slice unless a new plan is explicitly needed
```

## Refinement prompt

```text
Refine the current slice execution plan.
Keep the same phase and target.
Reduce ambiguity, sharpen acceptance criteria, and make the next command operationally exact.
```

## Gap-finding prompt

```text
Inspect the current OmG state and identify gaps before continuation:
- missing verification
- dirty Git state
- unsynced taskboard/checkpoint/workflow
- unclear slice boundaries
- hidden safety or trust-boundary risks
Return the minimum corrective steps before execution continues.
```

## Topic-specific prompt: planning a new phase

```text
/omg:plan
First, briefly summarize in Hungarian, then continue in English.

Plan the next phase for this project using the same workflow method as previous phases.

Return:
- recommended slices
- execution order
- why this order is best
- risks
- dependencies
- exact next command
```

## Topic-specific prompt: controlled YOLO phase execution

```text
/omg:autopilot
Continue this project in controlled YOLO mode.

Target:
<Phase and slices>

Execution policy:
- run slices sequentially
- only continue when the prior slice is implemented, verified, and state-synced
- stop on safety, trust-boundary, architecture, or resource issues
- keep Git clean
- sync taskboard, checkpoint, and workflow after each slice
- summarize first in Hungarian, then continue in English
```

---

### 10. Open Questions and Gaps

* The KB captures the command-flow method, but not the full exact semantics of every OmG command implementation.
* Some behavior was inferred operationally from repeated usage rather than from formal OmG docs.
* The KB does not catalog every individual prompt used in the conversation, only the durable high-signal patterns.
* It does not specify whether OmG itself enforces taskboard/workflow updates automatically or whether this is purely prompt-driven discipline.
* It does not distinguish which commands are repo-native versus OmG framework-native beyond conversational evidence.

---

### 11. Suggested Extensions

Most valuable follow-up KBs:

1. **W7-Base architecture and operating model KB**
   Capture the system itself rather than just the OmG workflow used to build it.

2. **W7 CLI behavior contract KB**
   Focus on `w7` command semantics, safety rules, and operator model.

3. **GitOps + CI/CD model KB**
   Extract the webhook/runner hybrid deployment model and trust boundaries.

4. **Production hardening and policy enforcement KB**
   Preserve the prod guardrails and compliance logic as a standalone enforcement reference.

5. **Prompt asset library KB**
   Collect and normalize all reusable prompts generated in the conversation.

---

### 12. Source Coverage

This KB draws from the parts of the conversation where:

* OmG workflows were designed or refined
* status/plan/execute/loop/autopilot usage was discussed
* Git stabilization and slice closure were enforced
* multi-slice sequential YOLO prompts were created
* continuation and resume prompts were standardized

Intentionally omitted:

* deep details of W7-Base implementation except where needed to illustrate workflow
* unrelated Linux troubleshooting topics
* full narrative history of every slice
* general discussion not directly useful for OmG workflow reuse

