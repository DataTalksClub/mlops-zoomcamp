## 3.5 Homework

Previous homeworks:

**Week 1:**
* https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/01-intro/homework.md

**Week 2:**
* https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/02-experiment-tracking/homework.md

## Q1. Installing Prefect. What is the default profile name?

The goal of this homework is to familiarize users with Prefect and workflow orchestration. We start from the solution of homework 1. The notebook can be found below:

https://github.com/DataTalksClub/mlops-zoomcamp/blob/main/01-intro/homework.ipynb

We will take this notebook and bring this in a flow. 

Q1. Install Prefect. What is the name of the default profile?

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

## Q1. Installing Prefect. What is the default profile name?

Create a python file with 5 tasks and add them to a flow called main:

* read_dataframe
* prepare_features
* search_best_model
* train_final_model
* test_final_model

(Maybe we can also prepare some starter code like Cristian did in Homework 2 - e.g. take care of the main method)

Q2. Write the code for read_dataframe

???


Q3. Write the code for prepare_features

???


Q4. Write the code for search_best_model

Return the best parameters - it’ll be used for the next step 

What’s the best RSME?


Q5. Write code for train_final_model 

Get the params from the previous step and train the model. Save it. 
What’s the size of the model file? 

// Prefect saves the artifacts somewhere, right? We can ask them to look in that folder 


Q6. Write code for test_final_model

Evaluate the model from the previous step on March 2021 data. What’s the RMSE? 

—-----------------------------------------------------------------------
Kevin’s notes

We can take the notebook from homework 1 and turn it into a workflow 

Q1. Install Prefect version 2.0b5. Run `prefect config view`. What is the name of the PREFECT_PROFILE?

There is a default profile so the name will be “default”. This also verifies they were able to install correctly.

Create a python file with 5 tasks and add them to a flow called main:

read_dataframe
prepare_features
search_best_model
train_final_model
test_final_model

Spin up the UI locally with `prefect orion start`

Look at the logs when spinning up Orion. 

Q2: What is the default address to view the local UI?

It should be: http://127.0.0.1:4200

You should be able to see previous Flow runs and the most recent successful runs. Navigate to any of them.

Q3a. What is the first log message of the flow run?

It should list what the task runner is.



Create the storage. You can use any storage that you want to experiment with. If you don’t have access to Cloud, feel free to use Local Storage.

Q3b. How many different storage options are there? Note the count starts at 0.

There are 6 options when you do `prefect storage create`.

Create the deployment with `prefect deployment create`. This should generate a deployment similar to “flow_name/deployment_name”. Set the schedule to run every 24 hours.

Run `prefect deployment inspect ‘flow_name/deployment_name’` to see the metadata of the Flow 

Q4. What is the schedule of the deployment? (Or we could ask for that number in interval. It should be 86400.0 for them if they set to run every 24 hours)




View the deployment in the UI. When first loading, we may not see that many flows because the default filter is 1 day back and 1 day forward. Remove the filter for 1 day forward to see the scheduled runs.

Q5. How many flow runs are there in the flow runs tab?

Prefect schedules the next 100 runs so they should be above 100. These scheduled runs won’t be picked up without an agent yet.

We can also do a multiple choice of how many future runs Prefect schedules for them (20,40,60,80,100).

Create a work queue and agent. 

Q6. What is the work-queue id of the work-queue you created?

We can check if the one they give is a valid UUID.
