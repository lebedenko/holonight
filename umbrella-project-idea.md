# HoloNight Umbrella Repository Proposal

An umbrella repository would improve cross-project development for HoloNight, provided it remains a thin coordination layer rather than becoming a monorepo disguised with submodules.

The main benefit is not the submodules themselves. It is having one canonical place for:

- the HoloNight-wide roadmap;
- cross-project architecture decisions;
- dependency and version relationships;
- integration verification;
- instructions for coordinating changes across repositories.

Submodules make a particular integrated state reproducible: an umbrella commit records exactly which revisions of `holonight-qt`, `holonight-shell`, `holonight-ai`, and other projects belong together.

## Recommended Model

Use an umbrella repository with submodules while keeping every subproject independently buildable and releasable:

```text
holonight/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── Taskfile.yml
├── docs/
│   ├── architecture/
│   ├── decisions/
│   ├── roadmap.md
│   └── initiatives/
│       └── shared-frame-system/
│           ├── OVERVIEW.md
│           ├── ROADMAP.md
│           ├── INTEGRATION.md
│           └── STATUS.md
├── .codex/
│   └── skills/
├── projects/
│   ├── holonight-qt/       # submodule
│   ├── holonight-shell/    # submodule
│   ├── holonight-ai/       # submodule
│   ├── holonight-icons/    # submodule
│   └── holonight-daemon/   # future submodule
└── scripts/
    └── integration checks
```

Using `projects/` or `components/` keeps umbrella-level coordination material visibly separate from product source code.

## SDD Ownership

Use two levels of specification.

### Umbrella-Level Initiative

The umbrella repository owns the cross-project initiative:

```text
docs/initiatives/shared-frame-system/
├── OVERVIEW.md
├── ROADMAP.md
├── INTEGRATION.md
└── STATUS.md
```

It should define:

- the user-facing objective;
- participating repositories;
- ownership boundaries;
- implementation order;
- compatibility constraints;
- integration acceptance criteria;
- links to each repository's SDD cycle;
- currently compatible submodule commits.

### Subproject-Level SDD

Each subproject owns its local implementation specification:

```text
holonight-qt/docs/sdd/control-completeness/
├── SPEC.md
├── DESIGN.md
└── TASKS.md
```

The local SDD contains concrete APIs, files, tests, and implementation decisions. The umbrella specification should link to these documents rather than duplicate their details.

For example:

```text
Shared frame initiative
  1. holonight-qt
     Semantic shapes and reusable frame primitives
  2. holonight-shell
     BarFrame and popup adoption
  3. holonight-ai
     ApplicationWindow and workspace adoption
  4. umbrella integration
     Pin compatible revisions and run visual smoke checks
```

This gives a new session enough context to work in one repository without losing the overall implementation sequence.

## Agent Instructions

Agent infrastructure should exist at both umbrella and subproject levels, with different responsibilities.

### Umbrella `AGENTS.md`

The umbrella instructions should contain only project-wide coordination rules:

- repository map and ownership boundaries;
- how to identify the appropriate repository for a change;
- cross-repository SDD workflow;
- dependency direction;
- commit and submodule update procedure;
- integration commands;
- a rule against mixing unrelated repositories in one commit;
- a requirement to update initiative status after completing a project cycle.

For example:

```text
holonight-qt owns visual primitives and reusable Qt controls.
holonight-shell owns desktop-shell composition and system surfaces.
holonight-ai owns AI application layout and product behavior.
The umbrella repository owns integration state and cross-project planning.
```

### Subproject `AGENTS.md`

Each subproject should retain its own instructions:

- build and test commands;
- coding conventions;
- local architecture;
- component ownership;
- local SDD conventions;
- project-specific skills;
- release rules.

A session opened inside an umbrella submodule may receive both umbrella and local instructions when the agent supports hierarchical instruction discovery. Because behavior can differ between tools, each subproject should also include a short, stable reference to the umbrella coordination model.

Do not copy the full umbrella instructions into every repository. Duplication will eventually drift. A concise subproject section is sufficient:

```markdown
## HoloNight Ecosystem

This repository is independently usable but participates in the HoloNight
umbrella project. Cross-project initiatives are tracked in the umbrella
repository under `docs/initiatives/`.

This repository owns reusable Qt theme primitives. Consumer-specific shell
or application layouts must remain in their respective repositories.
```

## Skills and Agent Definitions

Use the same layered ownership for `.codex/`, `.claude/`, skills, and agent definitions:

- umbrella skills coordinate cross-repository SDD, integration releases, compatibility audits, and submodule synchronization;
- subproject skills cover project-specific implementation, such as QML practices, Qt testing, shell architecture, provider integration, or daemon IPC;
- generic personal skills should remain globally installed instead of being copied into every repository.

A useful rule is:

> Put a skill at the narrowest level where all of its assumptions remain true.

For example, a Qt/QML implementation skill belongs in `holonight-qt` or in a global skill installation. A skill for coordinating a HoloNight cross-repository feature belongs in the umbrella repository.

Root-level definitions coordinate; subproject definitions implement.

## Cross-Repository Commit Flow

A cross-project initiative should proceed in dependency order:

1. Create the umbrella initiative and roadmap.
2. Implement and commit the provider repository first, such as `holonight-qt`.
3. Update and commit each consumer repository in dependency order.
4. Run integration checks from the umbrella checkout.
5. Update the submodule pointers.
6. Commit the umbrella integration state.

The umbrella commit becomes the integration commit:

```text
feat: integrate shared frame system across HoloNight
```

It points to the exact compatible commit from every participating repository.

This allows a later session to answer immediately:

- What are we implementing?
- Which project is next?
- Which changes are complete?
- Which revisions work together?
- What integration verification remains?

## Costs of Submodules

Submodules introduce some operational friction:

- cloning normally requires `--recurse-submodules`;
- switching umbrella branches can leave submodules at detached `HEAD`s;
- changes must be committed inside a subproject before its umbrella pointer is updated;
- pull requests can require coordinated merge ordering;
- automation must initialize and update submodules explicitly.

These costs are manageable for a mostly single-maintainer ecosystem, especially because exact revision pinning is valuable for HoloNight.

An umbrella commit does not automatically include uncommitted or newly committed work inside a submodule. Cross-project integration normally produces two kinds of commits:

1. implementation commits in the affected subprojects;
2. an umbrella commit that updates their submodule pointers and integration status.

## Recommended Workflow

Create the umbrella repository, add the projects as submodules, and use it as the default entry point for cross-project work. Continue opening individual repositories directly for isolated work.

- For a single-project bug, open that subproject directly.
- For a cross-project feature or refactoring, start in the umbrella repository.
- Let the umbrella SDD determine ownership and dependency order.
- Give each implementation phase its own local SDD and commit.
- Finish with an umbrella integration commit that pins and documents the verified revisions.

The largest workflow improvement comes from the shared roadmap, ownership boundaries, and explicit progress tracking. Submodules complement that structure by providing a reproducible integration state without sacrificing the independent lifecycle of each HoloNight project.
