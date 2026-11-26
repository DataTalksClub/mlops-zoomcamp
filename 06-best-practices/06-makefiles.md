---
video_url: "https://www.youtube.com/watch?v=F6DZdvbRZQQ&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK"
video_duration_seconds: 936
code:
  - label: "Project Makefile"
    path: code/Makefile
prev_url: 05-pre-commit.md
next_url: 07-terraform-introduction.md
---

# Makefiles and make

The project has separate commands for tests and quality checks. It also has commands for image builds, integration tests, and setup. A Makefile gives each command a stable, discoverable name.

## Targets and dependencies

The example defines these targets:

- `test` and `quality_checks`
- `build` and `integration_test`
- `publish` and `setup`

A target can depend on another target, so `build` runs quality checks and tests before building the Docker image.

![A Makefile with targets and dependencies](images/06-makefiles-01-makefile.jpg)

Run `make test` or `make quality_checks` while developing, and use `make build` when you want the same prerequisites before creating the image.

![Running a Makefile target](images/06-makefiles-02-targets.jpg)

Keep target names and environment variables documented. A short command should still make it clear which external services, credentials, or Docker resources it needs.

<!-- nav:start -->
[← Previous: Git Pre-commit Hooks](05-pre-commit.md) · [Next: Terraform: Introduction →](07-terraform-introduction.md)
<!-- nav:end -->
