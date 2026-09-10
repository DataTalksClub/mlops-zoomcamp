---
video_url: "https://www.youtube.com/watch?v=xkTWF9c33mU&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK&index=53"
code:
  - label: "Project quality commands"
    path: code/Makefile
  - label: "Project configuration"
    path: code/pyproject.toml
---

# Continuous Integration

Continuous integration runs the project checks for every proposed change. It should reproduce the local quality gate on a clean GitHub Actions runner.

## Define the CI workflow

Create `.github/workflows/ci-tests.yml` with jobs for environment setup, unit tests, integration tests, and Terraform plan. Trigger it for pull requests to the development branch so reviewers can see the result before merging.

![The GitHub Actions workflow files](images/12-continuous-integration-01-workflows.jpg)

Use the Makefile targets or equivalent commands in the workflow. Keep secrets out of the repository and use a local service such as LocalStack for integration tests that don't need real AWS resources.

![The CI test steps in the repository](images/12-continuous-integration-02-tests.jpg)

A failed check should leave enough logs to identify whether the problem came from Python dependencies, tests, Docker, or Terraform configuration.
