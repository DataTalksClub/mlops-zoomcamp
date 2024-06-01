# MLOps Zoomcamp Ch3 Orchestration
[Chapter 3](https://github.com/mleiwe/mlops-zoomcamp/tree/main/03-orchestration) of the 2024 MLOps Zoomcamp.

Orchestration is essentially the organising and management of a pipeline that develops, deploys, and maintains a machine learning solution. A pretty good summary can be seen in this [medium article](https://towardsdatascience.com/machine-learning-orchestration-vs-mlops-d4cfe3b7bec) although their focus is more on Airflow than Mage which is what this course covers

![Orchestration covers the entire realm of MLOps](Images/MLOps.webp)

Image created by [Jeff Fletcher](https://towardsdatascience.com/machine-learning-orchestration-vs-mlops-d4cfe3b7bec)

In order to build an efficient and reliable pipeline/workflow, one must have structured/organised thoughts and plans that are well documented and factor in use cases. So for this aspect of the course we have to work in a structured manner.

## 3.0 Introduction ML pipelines and Mage
### What is MLOps?
MLOps is essentially moving ML models from deployment and into production in order to drive business value.

There are several steps to this
1. **Preparing the model for deployment**
This involves optimizing performance, ensuring it handles real-world data, and packaging it for integration into existing systems.
2. **Deploying the model**
This involves moving it from development to production, making it accessible to users and applications.
3. **Monitoring the model**
Once deployed, models must be continuously monitored for accuracy and reliability, and may need retraining on new data and updates to maintain effectiveness.
4. **Integrate the model into existing workflows**
The operationalized model must be integrated into existing workflows, applications, and decision-making processes to drive business impact.
*"Effective operationalization enables organizations to move beyond experimentation and drive tangible value from ML at scale, powering intelligent applications that personalize the customer experience and creates real business value."*

![A simplistic MLOps Pipeline](Images/SimplisticMLOpsPipeline.png)
*NB This is a simplistic version that will get updated as the course goes on.*

### Why do we need to operationalise ML?
**MLOps increases productivity**
MLOps helps data scientists, ML engineers, and DevOps specialists work effectively with each other. This is done by **providing/creating a unified environment** for features such as: experiment tracking, feature engineering, model management, and deployment. 

The end result is that cross-functional teams are able to work together throughout the entire machine learning lifecycle.

**MLOps ensures reliability**
By creating a standard workflow/pipeline MLOps ensures high quality reliable models. This is **achieved through clean datasets, proper testing, validation, CI/CD practices, monitoring, and governance**.

**MLOps ensures reproducibility**
The standard workflow/pipeline that MLOps produces should also produce reliable results and ensure compliance. This is **achieved by versioning datasets, codes, and models**. This helps with transparency and auditability to ensure adherence to policies and regulations.

**Time-to-value**
This standard pipeline streamlines the ML lifecycle, enabling organisations to successfully deploy more projects to production and derive tangible business value and ROI from AI/ML investments at scale.

### Why Mage?
There are other management solutions out there which are nicely summarised in this [blog post](https://neptune.ai/blog/mlops-tools-platforms-landscape) (Honestly well worth a careful read). In practice your decisions will be based on your situation in terms of cloud infrastructure, etc.

**So what does Mage offer?**

**1. Data Preparation**
Mage offers features to build, run, and manage data pipelines for data transformation and integration, including pipeline orchestration, notebook environments, data integrations, and streaming pipelines for real-time data.

**2. Training and Deployment**
Mage provides accessible API endpoints to help prepare data, train and deploy ML models

**3. Standardise Complex Processes**
Mage provides a uniform platform for data pipelining, model development, deployment, versioning, CI/CD, and maintainece. This allows developers to focus on model creation while improving efficiency and collaboration.

### Mage example pipeline
There is the following [quickstart guide](https://github.com/mleiwe/mlops-zoomcamp/blob/main/03-orchestration/README.md#Quickstart) or just follow the instructions below.

#### Set up the pipeline
1. Git Clone the repo
```
$git clone https://github.com/mage-ai/mlops.git
```

2. Change directory to the cloned repo
You should be able to cd to`mlops` as the repo should have been cloned into your current directory. If not you just need to navigate to that folder.
```
$cd mlops
```
3. Launch Mage and the database service (PostgreSQL)
```
$./scripts/start.sh
```
NB A warning may appear `WARN[0000] The "PYTHONPATH" variable is not set. Defaulting to a blank string.`. I'm guessing we don't need to worry about this.

You do however need to make sure the docker daemon is running. (In plain English make sure your docker app is running)

4. The subproject that contains all the pipelines and code is named [`unit_3_observability`](https://github.com/mage-ai/mlops/tree/master/mlops/unit_3_observability)

#### Running the pipeline
1. Open [`http://localhost:6789`](http://localhost:6789) into your browser. This will launch the Mage UI
2. Select the `unit_0_setup` option from the available projects.
3. Navigate to the pipeline option (2nd option on the left hand side) and select the pipeline names `example pipeline`.
4. Click on the button labelled `Run @once`. This will run the pipeline.

![How to run the example pipeline](Images/MageExamplePipeline_pt1.gif.crdownload)

Once the run is complete (should take <1 minute) you can then  view the log, and further details for that run of the pipeline.
![Viewing the results](Images/MageExamplePipeline_pt2.gif.crdownload)

NB a file titled `titanic_clean.csv` should have appeared in your `mlops` folder.

### Useful Resources
1. [Code for the example data pipeline](https://github.com/mage-ai/mlops/tree/master/mlops/unit_0_setup)
2. [The definitive end to end machine learning ML lifecycle guide and tutorial for data engineers](https://mageai.notion.site/The-definitive-end-to-end-machine-learning-ML-lifecycle-guide-and-tutorial-for-data-engineers-ea24db5e562044c29d7227a67e70fd56?pvs=4)
3. [Quickstart Guide](https://github.com/mleiwe/mlops-zoomcamp/blob/main/03-orchestration/README.md#Quickstart)
4. [Platform landscape for MLOps tools](https://neptune.ai/blog/mlops-tools-platforms-landscape)
5. [What is MLOps Orchestration](https://towardsdatascience.com/machine-learning-orchestration-vs-mlops-d4cfe3b7bec)

## 3.1 Data Preparation: ETL and Feature Engineering
## 3.2 Training: sklearn models and XGBoost
## 3.3 Observability: Monitoring and Alerting
## 3.4 Triggering: Inference and Retraining
## 3.5 Deploying: RUnning Operations in Production