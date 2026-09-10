# Cohorts

Each `cohorts/<year>/` directory here is a frozen, self-contained copy of one
past live delivery of the course: `2022`, `2023`, `2024`, `2025`. Every one of
them has a `cohort.yaml` (`curriculum: github_archive`) recording its dates
and pointing at a notice file — added after the fact, since none of these
years originally shipped with any manifest at all. Their interior (module
directories, differing content per year) is untouched pre-migration content,
not reshaped to match any newer convention.

`cohorts/2022/` has no `README.md` — its `cohort.yaml` points its
`archive.notice_path` at `leaderboard.md` instead, the closest thing it has
to a cohort-identifying document. That's a gap worth a human decision on
whether to add a real README there; it hasn't been treated as blocking.

## The current cohort is `self-paced`, not a year

There is no live cohort scheduled for this course — see the root
[`README.md`](../README.md): *"We don't plan to run a live cohort in
2026... fully available for self-paced study now."* Root
([`01-intro/`](../01-intro/) through [`07-project/`](../07-project/)) holds
that actively-maintained self-paced material, and is what `content: root`
means in `course.yaml`.

`cohorts/self-paced/cohort.yaml` represents that: `identifier: "self-paced"`,
`delivery: self_paced`, `curriculum: current`, `start_date`/`end_date: null`
(a self-paced delivery has no cohort-wide deadline), `homework: []` (nothing
is currently graded or tracked). `course.yaml:current_cohort` names it the
same way a year would for a live delivery.

**What's still deferred**: each root module is presently a single long-form
`README.md`, not the `module.yaml` + numbered `NN-kebab.md` lesson files the
shared-root v2 contract expects. The checker (`scripts/check-zoomcamp`) knows
about this and reports it (`numbered_module_required`,
`current_module_missing`) — those are expected, not a sign something broke.
Restructuring each module's content into that shape is separate, real
editorial work, not done here.

## The conventions themselves

`DataTalksClub/zoomcamp-ops` is the authority: `STRUCTURE.md` for the
repository layout and `docs/shared-curriculum-v2.md` for the shared-root
schema this repository's `course.yaml` now follows, plus the curriculum
contract documented beside it for the YAML schemas and the unit page rules.

The website's ingestion parser is the final authority and fails loudly on
push.
