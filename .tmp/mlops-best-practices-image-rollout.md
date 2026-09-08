# MLOps best-practices image rollout

This report covers the two image references owned by this worker in
`06-best-practices/README.md`. The `imagegen` skill was available, so both
bounded architecture diagrams used the imagegen path after deterministic
content crops. The original source files remain unchanged.

## Decisions

| Source | Teaching point | Score | Decision | Final asset |
| --- | --- | ---: | --- | --- |
| `AWS-stream-pipeline.png` (1760x1144) | The AWS stream-based ride-prediction flow: input Kinesis, CloudWatch trigger, Lambda, model artifacts in S3, container image in ECR, and output Kinesis. | 12/12 | `crop/replace` | `AWS-stream-pipeline-imagegen.png` |
| `ci_cd_zoomcamp.png` (1870x1322) | The CI/CD relationship from a GitHub commit through tests and Terraform to AWS build, registry, Lambda, and deployment updates. | 12/12 | `crop/replace` | `ci_cd_zoomcamp-imagegen.png` |

Scores are the six rubric criteria in order: instructional contribution,
relevance, readability/focus, complementarity, durability, and caption/accessibility.
Both images have a specific teaching point, directly support the surrounding
lesson sections, add architecture relationships that prose does not show as
well, and are durable conceptual diagrams. Their generic `image` alt text was
also replaced with meaningful descriptions.

## AWS stream pipeline

- Source inspection: clean architecture diagram; no face, webcam tile,
  browser/Zoom chrome, cursor, watermark, or other capture overlay.
- Preparation crop: deterministic `-trim` crop from the source to 1360x862,
  preserving the AWS boundary and the unlabeled input/output arrow stubs.
- Generation: rebuilt as a crisp flat technical diagram from the crop.
- Checked invariants: `AWS Cloud`; S3 model artifacts and `Get Model`; input
  Kinesis; `CW event: Kinesis-Lambda trigger`; AWS Lambda; `Get Image` from
  ECR; `Publish prediction events`; output Kinesis; all arrow directions and
  service relationships.
- Original retained at `06-best-practices/AWS-stream-pipeline.png`.

## CI/CD workflow

- Source inspection: clean CI/CD architecture diagram; no face, webcam tile,
  browser/Zoom chrome, cursor, watermark, or other capture overlay.
- Preparation crop: deterministic `-trim` crop from the source to 1711x1280,
  preserving the CI/CD sections, panel boundaries, and arrows.
- First generated candidate was rejected because the bottom
  `CI (Continuous Integration)` and `CD (Continuous Delivery)` labels were
  clipped. A single targeted framing correction added bottom white margin;
  the corrected candidate was accepted.
- Checked invariants: GitHub commit trigger; Test Application; Define
  Infrastructure; Build and Push, Deploy; unit/integration tests; Terraform;
  `.tfstate`; AWS/Kinesis/CloudWatch/IAM/Lambda/S3/ECR components; AWS CLI;
  Docker; all solid/dashed arrow relationships; complete bottom labels.
- Original retained at `06-best-practices/ci_cd_zoomcamp.png`.

## Validation

- Every owned Markdown image reference resolves.
- `git diff --check` passes.
- No disposable crop or rejected generation is referenced by the lesson.
- Final generated assets are `AWS-stream-pipeline-imagegen.png` (1575x998)
  and `ci_cd_zoomcamp-imagegen.png` (1533x1026).
- Both original source assets remain in place for rollback and provenance.
- Disposable source crops and rejected generations were kept under `.tmp`
  during review and are removed after this report is committed.
