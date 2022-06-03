## 3.6 Homework

Previous homeworks:

**Week 1:**
* https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/01-intro/homework.md

**Week 2:**
* https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/02-experiment-tracking/homework.md

## Q1. Installing Prefect. What is the default profile name?

The goal of this homework is to familiarize users with Prefect and workflow orchestration. We start from the solution of homework 1. The notebook can be found below:

https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/01-intro/homework.ipynb

We will take this notebook and bring this in a flow. 

If you want to follow the videos exactly, do:

```
pip install prefect==2.0b5
```

If you need Windows support, you will need to install 2.0b6 (to be released Monday June 7). 2.0b6 will officially support Windows.

```
pip install prefect==2.0b6
```

Note that 2.0b5 and 2.0b6 are not compatible because 2.0b6 contains breaking changes. If you run into issues, you can reset the Prefect database by doing:

```
prefect orion database reset
```

This command will clear the data held by Orion.

After installation, you should be able to run the following command:

```
prefect config view
```

What is the name of the current profile?

Prefect lets you have multiple profiles to easily switch between Cloud, local, or even multiple Orion instances. For more information, you can check the following [link](https://orion-docs.prefect.io/concepts/settings/#configuration-profiles)

## Q2. Share a screen shot of the radar plot you made

Create a python file with 5 tasks and add them to a flow called main:

* read_dataframe
* prepare_features
* search_best_model
* train_final_model
* test_final_model

Take time as well to parameterize `main` to specify the path of the training and test data.

You can use the local Orion instance for testing. You can also SSH to a VM if you prefer After creating this code, you can run:

```
prefect orion start
```

You should be able to see previous Flow runs and the most recent successful runs. Navigate to any of them. Take time to explore the UI.

Share a screen shot of the radar plot. There should be 5 tasks there. You can upload this to Github and submit a URL of an image. We will view the links.

## Q3. How many different storage options are there?

When the code is already working, we'll create a deployment and register it with Orion. In order to do this, we need to create storage. This was covered in the videos.

How many different storage options are there? (Note the count starts from 0)

## Q4. What is the default anchor_date for a deployment?

Create a deployment with `prefect deployment create`. This should generate a deployment similar to “flow_name/deployment_name”. Set the schedule to run at some interval and use the `SubprocessFlowRunner`. These are also seen in the video tutorials.

Run `prefect deployment inspect ‘flow_name/deployment_name’` to see the metadata of the Flow.

What is the anchor_date listed under the schedule?

- 1970-01-01T00:00:00+00:00
- 2019-01-01T00:00:00+00:00
- 2020-01-01T00:00:00+00:00
- 2022-01-01T00:00:00+00:00


## Q5. How many flow runs does Prefect schedule in advanced?

View the deployment in the UI. When first loading, we may not see that many flows because the default filter is 1 day back and 1 day forward. Remove the filter for 1 day forward to see the scheduled runs.

How many flow runs are scheduled by Prefect in advanced? You should not be counting manually. There is a number of upcoming runs on the top right of the dashboard.

- 10
- 20
- 50
- 75
- 100

## Q6.Find the right command to view all work-queues

For all CLI commands with Prefect, you can use `--help` to get more information.

For example,
* prefect --help
* prefect work-queue --help

* prefect work-queue inspect
* prefect work-queue ls
* prefect work-queue preview
* prefect work-queue list
