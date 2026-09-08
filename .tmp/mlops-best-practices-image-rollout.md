# MLOps current lesson visual audit — 2026-09-08

## Scope and method

This is the pixel-level re-audit of the 38 active image references reported by
the operations scanner at MLOps commit `e68ba45e215e8ebada38614444b05098fc933d9f`
(37 local references and one official remote badge). The two regenerated
Best Practices references were published in `21edb0034cb1b2c02f4472dd1ff540fed071042e`.

Every local target was inspected as pixels at its native resolution and in a
lesson-size render. Existing imagegen-looking files were not accepted from
their names, dimensions, or interpolation metadata. The 31 conceptual
illustrations and the shared homework visual were checked for clean artwork,
caption/alt-text relationships, legibility, and absence of browser/editor/
webcam/cursor/selection artifacts. No active target was a table-only or
code-only screenshot that should be replaced by native Markdown/code.

The exact AWS walkthrough screenshots in
`02-experiment-tracking/mlflow_on_aws.md` are outside the scanner's 38-row
root-README selection, but were audited as a supplementary set because they
are source-of-truth UI screenshots. They were compared with their original
source files, which all trace to `21ff63f`; their original pixels already
have bounded content and no capture artifacts, so no redraw was applied.

Evidence keys:

- **E1** — direct native and lesson-size pixel review of a 1672x941 conceptual
  illustration; clean diagram, relationships match the surrounding alt text
  and lesson section, and no capture artifacts.
- **E2** — the shared 1672x941 homework-support illustration; native and
  lesson-size review found a clean, text-light checklist flow, not a
  redundant code/table screenshot.
- **E3** — exact-source comparison for a Best Practices diagram, including
  native and lesson-size review after redraw; labels, arrows, boundaries, and
  relationships were manually checked against the bounded source crop.
- **E4** — official Streamlit SVG fetched from the referenced URL, rendered
  and inspected at its native 135x20 pixels; visible text is exactly
  `Open in Streamlit`.
- **E5** — exact AWS screenshot source/target comparison; native/source
  pixels and the lesson-size AWS composite were inspected. UI text, values,
  controls, and the redacted password field remain exact; no chrome, cursor,
  webcam tile, or selection overlay is present.

Imagegen IDs:

- **G-AWS** — generation `01a08204-88b7-7273-aeca-f0bcd488e09e`,
  output `exec-5a46c572-ca52-48ca-a30a-3a748496ef03`.
- **G-CICD** — generation `01a08204-88b7-7273-aeca-f0bcd488e09e`,
  output `exec-7892cd37-5e32-49f9-ac62-e02a1897f9c9`.

The redraw inputs were deterministic bounded crops of the untouched originals:
`AWS-stream-pipeline.png` crop `1360x862+140+138`, and
`ci_cd_zoomcamp.png` crop `1711x1280+40+20`. The original files remain
unchanged for provenance. The generated outputs were viewed at native size
and at 1000-pixel lesson renders before publication. A duplicate AWS
candidate was left outside the repository and is not referenced; no rejected
candidate is published.

## Scanner ledger — all 38 active references

| # | Reference | Status | Imagegen ID | Publication commit | Evidence |
|---:|---|---|---|---|---|
| 1 | `01-intro/README.md:10` → `images/illustrations/01-01-mlops-lifecycle.png` | ACCEPTED | — | `e68ba45` | E1 |
| 2 | `01-intro/README.md:22` → `images/illustrations/01-02-01-cloud-workspace.png` | ACCEPTED | — | `e68ba45` | E1 |
| 3 | `01-intro/README.md:37` → `images/illustrations/01-02-02-aws-vm-setup.png` | ACCEPTED | — | `e68ba45` | E1 |
| 4 | `01-intro/README.md:112` → `images/illustrations/01-03-ride-duration-training.png` | ACCEPTED | — | `e68ba45` | E1 |
| 5 | `01-intro/README.md:126` → `images/illustrations/01-04-course-overview.png` | ACCEPTED | — | `e68ba45` | E1 |
| 6 | `01-intro/README.md:137` → `images/illustrations/01-05-mlops-maturity-model.png` | ACCEPTED | — | `e68ba45` | E1 |
| 7 | `01-intro/README.md:152` → `../images/homework-checklist.png` | ACCEPTED | — | `e68ba45` | E2 |
| 8 | `02-experiment-tracking/README.md:14` → `images/illustrations/02-01-experiment-tracking.png` | ACCEPTED | — | `e68ba45` | E1 |
| 9 | `02-experiment-tracking/README.md:25` → `images/illustrations/02-02-mlflow-getting-started.png` | ACCEPTED | — | `e68ba45` | E1 |
| 10 | `02-experiment-tracking/README.md:41` → `images/illustrations/02-03-mlflow-experiment-tracking.png` | ACCEPTED | — | `e68ba45` | E1 |
| 11 | `02-experiment-tracking/README.md:52` → `images/illustrations/02-04-model-management.png` | ACCEPTED | — | `e68ba45` | E1 |
| 12 | `02-experiment-tracking/README.md:63` → `images/illustrations/02-05-model-registry.png` | ACCEPTED | — | `e68ba45` | E1 |
| 13 | `02-experiment-tracking/README.md:75` → `images/illustrations/02-06-mlflow-in-practice.png` | ACCEPTED | — | `e68ba45` | E1 |
| 14 | `02-experiment-tracking/README.md:85` → `images/illustrations/02-07-benefits-limitations-alternatives.png` | ACCEPTED | — | `e68ba45` | E1 |
| 15 | `02-experiment-tracking/README.md:95` → `../images/homework-checklist.png` | ACCEPTED | — | `e68ba45` | E2 |
| 16 | `03-orchestration/README.md:8` → `images/illustrations/03-01-ml-pipeline.png` | ACCEPTED | — | `e68ba45` | E1 |
| 17 | `03-orchestration/README.md:17` → `images/illustrations/03-02-notebook-to-script.png` | ACCEPTED | — | `e68ba45` | E1 |
| 18 | `03-orchestration/README.md:30` → `images/illustrations/03-03-orchestrated-workflow.png` | ACCEPTED | — | `e68ba45` | E1 |
| 19 | `03-orchestration/README.md:83` → `../images/homework-checklist.png` | ACCEPTED | — | `e68ba45` | E2 |
| 20 | `04-deployment/README.md:8` → `images/illustrations/04-01-three-deployment-modes.png` | ACCEPTED | — | `e68ba45` | E1 |
| 21 | `04-deployment/README.md:19` → `images/illustrations/04-02-flask-docker-service.png` | ACCEPTED | — | `e68ba45` | E1 |
| 22 | `04-deployment/README.md:32` → `images/illustrations/04-03-registry-model-serving.png` | ACCEPTED | — | `e68ba45` | E1 |
| 23 | `04-deployment/README.md:45` → `images/illustrations/04-04-streaming-kinesis-lambda.png` | ACCEPTED | — | `e68ba45` | E1 |
| 24 | `04-deployment/README.md:59` → `images/illustrations/04-05-batch-scoring-script.png` | ACCEPTED | — | `e68ba45` | E1 |
| 25 | `04-deployment/README.md:76` → `images/illustrations/04-06-mage-batch-workflow.png` | ACCEPTED | — | `e68ba45` | E1 |
| 26 | `04-deployment/README.md:86` → `../images/homework-checklist.png` | ACCEPTED | — | `e68ba45` | E2 |
| 27 | `05-monitoring/README.md:8` → `images/illustrations/05-01-ml-monitoring-loop.png` | ACCEPTED | — | `e68ba45` | E1 |
| 28 | `05-monitoring/README.md:19` → `images/illustrations/05-02-monitoring-environment.png` | ACCEPTED | — | `e68ba45` | E1 |
| 29 | `05-monitoring/README.md:30` → `images/illustrations/05-03-reference-model-preparation.png` | ACCEPTED | — | `e68ba45` | E1 |
| 30 | `05-monitoring/README.md:41` → `images/illustrations/05-04-evidently-metrics.png` | ACCEPTED | — | `e68ba45` | E1 |
| 31 | `05-monitoring/README.md:51` → `images/illustrations/05-05-monitoring-dashboard.png` | ACCEPTED | — | `e68ba45` | E1 |
| 32 | `05-monitoring/README.md:61` → `images/illustrations/05-06-dummy-monitoring.png` | ACCEPTED | — | `e68ba45` | E1 |
| 33 | `05-monitoring/README.md:72` → `images/illustrations/05-07-data-quality-monitoring.png` | ACCEPTED | — | `e68ba45` | E1 |
| 34 | `05-monitoring/README.md:85` → `images/illustrations/05-08-save-dashboard.png` | ACCEPTED | — | `e68ba45` | E1 |
| 35 | `05-monitoring/README.md:96` → `images/illustrations/05-09-debugging-tests-reports.png` | ACCEPTED | — | `e68ba45` | E1 |
| 36 | `06-best-practices/README.md:48` → `AWS-stream-pipeline-redrawn.png` | REGENERATED | G-AWS | `21edb00` | E3 |
| 37 | `06-best-practices/README.md:93` → `ci_cd_zoomcamp-redrawn.png` | REGENERATED | G-CICD | `21edb00` | E3 |
| 38 | `07-project/README.md:104` → official remote Streamlit badge | ACCEPTED | — | `e68ba45` | E4 |

### Scanner outcome

The 38-row result is **36 ACCEPTED, 2 REGENERATED, 0 REMOVED, 0 REJECTED,
0 UNRESOLVED**. The four homework rows intentionally reuse one shared
support asset; they are separate active references in the scanner ledger.

## Supplementary exact AWS screenshots — 11 references

All 11 are unchanged source-backed screenshots from `21ff63f`. Each was
inspected at the native dimensions below and in the lesson-size AWS composite
(`native/aws.png` and `lesson/aws.png` review renders). The published target
is the original source file, so the target/source comparison is exact and no
crop or imagegen redraw is appropriate.

| Reference | Native size | Status | Imagegen ID | Source/publication evidence |
|---|---:|---|---|---|
| `mlflow_on_aws.md:12` → `images/ec2_os.png` | 779x724 | ACCEPTED | — | E5; source `21ff63f` |
| `mlflow_on_aws.md:14` → `images/ec2_instance_type.png` | 777x205 | ACCEPTED | — | E5; source `21ff63f` |
| `mlflow_on_aws.md:18` → `images/key_pair.png` | 597x630 | ACCEPTED | — | E5; source `21ff63f` |
| `mlflow_on_aws.md:22` → `images/select_key_pair.png` | 775x186 | ACCEPTED | — | E5; source `21ff63f` |
| `mlflow_on_aws.md:26` → `images/security_group.png` | 1827x537 | ACCEPTED | — | E5; source `21ff63f` |
| `mlflow_on_aws.md:32` → `images/s3_bucket.png` | 799x344 | ACCEPTED | — | E5; source `21ff63f` |
| `mlflow_on_aws.md:40` → `images/postgresql.png` | 760x737 | ACCEPTED | — | E5; source `21ff63f` |
| `mlflow_on_aws.md:44` → `images/db_settings.png` | 759x416 | ACCEPTED | — | E5; source `21ff63f` |
| `mlflow_on_aws.md:48` → `images/db_configuration.png` | 759x499 | ACCEPTED | — | E5; source `21ff63f` |
| `mlflow_on_aws.md:52` → `images/db_password.png` | 599x320 | ACCEPTED | — | E5; source `21ff63f` |
| `mlflow_on_aws.md:66` → `images/postgresql_inbound_rule.png` | 1798x327 | ACCEPTED | — | E5; source `21ff63f` |

No AWS screenshot contained a table/code-only surface that should be moved to
native lesson content. The password screenshot contains only the existing
redacted password field; no secret was exposed.

## Validation

- The active scanner refs resolve after the two README path updates.
- `git diff --check` passes before the audit report commit.
- Original Best Practices diagrams remain present and unchanged.
- Only the two accepted redraws are referenced by the changed lesson README.
- Unpublished imagegen candidates remain outside the repository.
