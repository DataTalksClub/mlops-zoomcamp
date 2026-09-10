---
code:
  - label: "Batch scoring implementation"
    path: batch/score.py
---

# Batch Scoring with Mage

The same batch workflow can run in Mage blocks, where a transformation block receives the batch data. It loads the selected model, applies it, and returns a prediction dataset.

## Build the block

Connect the block to the data input and to the model registry. The block should use the same feature preparation code as the standalone scoring script. Keep the model name or version in configuration so changing the model doesn't require editing the block.

The result should include the original identifiers, the prediction, and enough metadata to trace the run. Run the block locally with a small partition before scheduling it for regular batch execution.

## Operational checklist

Use this checklist before scheduling the block.

- Confirm that the block can reach MLflow and download the model.
- Verify that the input schema matches the training feature schema.
- Store the output in a location that downstream users can query.
- Record the model version and batch period with the result.
- Test a backfill before enabling a recurring schedule.

Mage is one possible orchestrator and batch runner, and its design matches the standalone script. The block receives data, applies a known model, and returns a traceable prediction dataset.
