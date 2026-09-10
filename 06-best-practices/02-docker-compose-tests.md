---
video_url: "https://www.youtube.com/watch?v=lBX0Gl7Z1ck&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK"
code:
  - label: "Docker integration test"
    path: code/integration-test/test_docker.py
  - label: "Integration test Compose file"
    path: code/integration-test/docker-compose.yaml
---

# Integration Tests with docker-compose

Unit tests check Python functions in isolation. An integration test starts the service in Docker, sends an HTTP request, and verifies the response across the actual process boundary.

## Start the service under test

The Compose file supplies the container and its environment. The test client sends a representative event to the running service and compares the returned prediction with the expected value.

![The integration test code and service response](images/02-docker-compose-tests-01-refactor.jpg)

Keep the test data deterministic. A small checked-in event fixture makes failures reproducible and avoids coupling the test to a live stream or database.

![A Docker-based integration test run](images/02-docker-compose-tests-02-integration.jpg)

Use the same image that will run in the target environment. A passing unit test doesn't prove that the image starts, its dependencies are installed, or its HTTP API works.
