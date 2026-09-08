# MLOps best-practices image rollout

This report covers the two image references owned by this worker in
`06-best-practices/README.md`. The `imagegen` skill was available, so both
bounded architecture diagrams used the imagegen path after deterministic
content crops. The original source files remain unchanged.

## Decisions

| Source | Teaching point | Score | Decision | Final asset |
| --- | --- | ---: | --- | --- |
| `AWS-stream-pipeline.png` (1760x1144) | The AWS stream-based ride-prediction flow: input Kinesis, CloudWatch trigger, Lambda, model artifacts in S3, container image in ECR, and output Kinesis. | 12/12 | `crop/replace` | `AWS-stream-pipeline-imagegen.png` |

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

## Validation

- Every owned Markdown image reference resolves.
- `git diff --check` passes.
- No disposable crop or rejected generation is referenced by the lesson.
