---
video_url: "https://www.youtube.com/watch?v=YWao0rnqVoI&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK&index=51"
code:
  - label: "Cloud end-to-end test"
    path: code/scripts/test_cloud_e2e.sh
  - label: "Kinesis integration test"
    path: code/integration-test/test_kinesis.py
---

# Test the Pipeline End to End

After Terraform has deployed the resources, test the complete path with one ride event. The event should enter the input Kinesis stream, trigger Lambda, load a model artifact from S3, and produce a record in the output stream.

![The deployed pipeline ready for an end-to-end test](images/10-terraform-testing-01-pipeline.jpg)

## Run and review the test

Set the run ID and stream names, insert a known event, and look at the Lambda and CloudWatch output. The test should identify which input produced which prediction and should fail when the response doesn't match the expected structure.

![Invoking the deployed pipeline](images/10-terraform-testing-02-invoke.jpg)

Terraform, the application image, model artifact, and test event are separate dependencies. Record their versions so a failed end-to-end run can be reproduced.
