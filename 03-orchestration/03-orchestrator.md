---
code:
  - label: "Pipeline commands"
    path: code/commands.md
  - label: "Duration prediction script"
    path: code/duration-prediction.py
---

# Using an Orchestrator

The Python script from the previous unit is a repeatable task. An orchestrator turns the task into a managed workflow with scheduling, parameters, retries, and a history of executions.

## Choose and run a tool

Common choices include Airflow and Prefect, while other options are Dagster, Kestra, and Mage. Start with the tool that fits the team's deployment environment and learning goals. Run it locally first, then create a minimal "hello world" workflow so you understand how the tool represents tasks, dependencies, and runs.

## Orchestrate the training workflow

Use the code from this module and map its steps to tasks. Keep the data flow explicit.

- download the selected data period.
- transform and prepare the features.
- train and evaluate the model.
- log the run and save the artifact.

The orchestrator should pass the period into the script rather than changing the script's source code. A monthly schedule might train on data from two months ago and validate on data from the previous month. Make the dates part of the workflow parameters so the run history shows them.

## Backfill and deploy

Backfilling means running the same workflow for historical periods. It helps when a pipeline is introduced after data has accumulated or when an upstream correction requires recomputing a range of months. Test a small range locally before launching a large backfill.

Deployment is optional for this unit. If the orchestrator will run in the cloud, keep the local workflow definition portable and document its dependencies. The previous cohorts contain examples using Prefect and Mage. Use them as references rather than assuming that one orchestrator is required.

## Optional MLflow service

For a shared local MLflow service, the original module includes a Docker example in [the MLflow resource section](README.md#mlflow). Use the same MLflow version in the image and in the training environment. Mount the backend database directory so the tracking state survives container restarts.
