# Cohorts

Each `cohorts/<year>/` directory here is a frozen, self-contained copy of one
past live delivery of the course: `2022`, `2023`, `2024`, `2025`. Every one of
them now has a `cohort.yaml` (`schema_version: 2`, `curriculum:
github_archive`) recording its dates and pointing at a notice file — added
after the fact, since none of these years originally shipped with any
manifest at all. Their interior (module directories, differing content per
year) is untouched pre-migration content, not reshaped to match any newer
convention.

`cohorts/2022/` has no `README.md` — its `cohort.yaml` points its
`archive.notice_path` at `leaderboard.md` instead, the closest thing it has
to a cohort-identifying document. That's a gap worth a human decision on
whether to add a real README there; it hasn't been treated as blocking.

## No current cohort, on purpose

**This repository does not have a `current_cohort` or a schema v2
`course.yaml` yet, and that is deliberate, not an oversight.**

Root ([`01-intro/`](../01-intro/) through [`07-project/`](../07-project/))
holds the actively-maintained self-paced material — see the root
[`README.md`](../README.md): *"We don't plan to run a live cohort in
2026... fully available for self-paced study now."* The shared-root v2
contract used by [other DataTalks.Club course
repos](https://github.com/DataTalksClub/zoomcamp-ops/blob/main/docs/shared-curriculum-v2.md)
requires exactly one `cohorts[]` entry declaring `content: root`, tied to a
`current_cohort` identifier — a shape built for a course with a live intake.
This course doesn't have one right now, and root's modules don't yet follow
the numbered-lesson-file convention that schema expects either (each module
here is presently a single long-form `README.md`, not `NN-kebab.md` unit
files).

Wiring root into schema v2 — including deciding what "current" even means for
a self-paced-only course, and restructuring each module's content into
numbered lesson files — is deferred, not abandoned. This directory documents
what's done (the four archives) and what isn't (everything about root and
`course.yaml`), so the gap is visible rather than silently inconsistent.

## The conventions themselves

`DataTalksClub/zoomcamp-ops` is the authority for the shared-root v2 schema
these archive manifests follow: `STRUCTURE.md` for the repository layout and
`docs/shared-curriculum-v2.md` for the YAML schemas. This repository's
`course.yaml` has not opted into that contract yet, so the website's
ingestion parser continues to treat this whole repository as schema v1 for
now — these `cohort.yaml` files are not read by anything until it does.
