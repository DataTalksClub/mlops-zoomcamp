# MLOps Zoomcamp: Deep Research and Course Renewal Strategy

## Executive Summary

**The course should not be shut down, and it should not be converted into an LLMOps-only program.** The strongest option is to keep the recognizable **MLOps Zoomcamp** brand while updating its promise:

> **MLOps Zoomcamp: Production ML & AI Systems**  
> Learn how to turn a model or AI feature into a reliable, observable, governed, and economically viable production system.

The course is not a dead asset. It is a strong search and community asset with accumulated technical debt. The repository still has significant visibility, stars, forks, backlinks, and organic traffic. At the same time, the public messaging is inconsistent: the repository says there is no live cohort planned for 2026, while the landing page can still give the impression that enrollment typically happens in spring.

That inconsistency should be fixed first. A visitor who is already interested in the course should immediately understand:

- whether the course is currently active;
- whether it is self-paced;
- which modules are current;
- which modules are legacy;
- whether a refreshed edition is planned;
- where to subscribe for updates.

A sensible content balance for a refreshed edition would be:

- **75–80%: general production ML engineering** — data, pipelines, testing, deployment, observability, reliability, security, governance, and cost;
- **15–20%: GenAIOps and LLMOps** as an extension of the same production lifecycle;
- **5–10%: AI-assisted engineering** — using AI for code generation, tests, migrations, debugging, infrastructure as code, documentation, and incident analysis.

The key opportunity is to reposition the course around a durable capability:

> **Engineering and operating production systems that contain ML or AI components.**

---

# 1. Is MLOps Still Relevant?

## MLOps Has Not Disappeared — Its Organizational Context Has Changed

AI adoption has grown dramatically, but using AI and operating AI reliably in production are very different things. Many organizations can build prototypes, call an API, or train a model. Far fewer can consistently:

- maintain quality after release;
- diagnose degradation;
- update models safely;
- control latency and cost;
- reproduce past results;
- manage lineage and approvals;
- connect technical metrics to business outcomes.

This is the modern MLOps problem.

Industry surveys continue to show that diagnosing failures in ML systems is difficult, often slow, and poorly connected to measurable business value. The market problem is therefore no longer simply “how do we train a model?” It is:

> **How do we turn models and AI features into dependable products?**

Relevant sources:

- [Stanford AI Index](https://hai.stanford.edu/ai-index)
- [MLOps Community research](https://mlops.community/)
- [DORA research](https://dora.dev/)

## The Job Titles Have Changed

The word **MLOps** is still used, but the work is increasingly distributed across roles such as:

- Machine Learning Engineer;
- ML Platform Engineer;
- AI Platform Engineer;
- ML Infrastructure Engineer;
- Applied AI Engineer;
- GenAI Platform Engineer;
- Production AI Engineer.

Across these roles, the recurring responsibilities are similar:

- training and evaluation pipelines;
- batch and online inference;
- model serving;
- CI/CD;
- data and model quality;
- feature infrastructure;
- observability;
- incident response;
- platform developer experience;
- governance;
- infrastructure and GPU utilization;
- latency and cost optimization;
- LLM evaluation and tracing.

A useful positioning statement is:

> **MLOps remains an important engineering discipline, but it is less likely to exist as a separate operational function owned by a standalone MLOps team. It is becoming a core part of ML engineering and AI platform engineering.**

A learner may not apply for a role called “MLOps Engineer,” but the course skills remain highly relevant for ML Engineer, AI Engineer, and Platform Engineer roles.

---

# 2. What Does Day-to-Day MLOps Work Look Like Now?

Modern production ML work is less about continuously training new models and more about serious software, data, platform, and reliability engineering.

It can be divided into five major categories.

## 2.1. Ship: Deliver Changes Safely

An engineer turns a notebook or prototype into:

- a maintainable package;
- a training pipeline;
- a batch job;
- an online service;
- a reusable internal component.

The engineer then adds:

- automated tests;
- code review;
- dependency management;
- reproducible environments;
- CI;
- model or evaluation gates;
- deployment automation;
- rollback procedures.

For online systems, this may include:

- contract tests;
- load tests;
- canary deployments;
- shadow traffic;
- version routing.

For batch systems, it may include:

- partitioning;
- backfills;
- retries;
- idempotency;
- freshness checks;
- SLA monitoring.

The defining characteristic of the role is increasingly **end-to-end ownership**, from features and training to deployment and production debugging.

## 2.2. Operate: Keep the System Working

A significant part of the job is handling operational failures:

- a pipeline failed;
- data is stale;
- an upstream schema changed;
- latency increased;
- the error rate increased;
- inference cost became too high;
- offline and online results diverged;
- a new model version behaves unexpectedly;
- an external provider changed behavior;
- an incident requires investigation and mitigation.

Common production concerns include:

- SLOs and SLIs;
- availability;
- latency;
- token usage;
- GPU utilization;
- queue depth;
- throughput;
- failure rate;
- cost per request;
- operational runbooks;
- postmortems.

## 2.3. Enable: Build Platforms for Other Teams

In many companies, the MLOps or ML Platform engineer is not expected to deploy every model manually. Instead, the team creates a **golden path** for other engineers and data scientists.

Typical platform deliverables include:

- project templates;
- reusable pipeline components;
- SDKs and CLIs;
- standard serving runtimes;
- standard CI/CD workflows;
- built-in observability;
- access to compute;
- artifact and model registries;
- secrets and permissions;
- documentation;
- self-service deployment.

The product of an ML Platform team is not a model. It is an **internal platform and developer experience** that allows other teams to ship ML systems safely.

## 2.4. Govern: Make Systems Auditable and Controllable

A production ML system should be able to answer questions such as:

- Which data was used to train this version?
- Which code and configuration produced it?
- Who approved the release?
- Which evaluation results were available before deployment?
- Which data can the service access?
- Where are secrets stored?
- Can the result be reproduced?
- Can the system be rolled back?
- Which actions are recorded in an audit log?

These requirements are no longer limited to heavily regulated industries. Lineage, documentation, access control, approval workflows, and auditability are becoming normal production engineering concerns.

The EU AI Act also increases the practical importance of governance, documentation, transparency, and risk management. The course should not become a legal course, but it should teach the engineering foundations that make governance possible.

Relevant source:

- [European Commission: Regulatory framework for AI](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)

## 2.5. Improve: Connect Technical Performance to Real Outcomes

A mature ML team does not only monitor model accuracy or drift. It also looks at:

- coverage;
- adoption;
- conversion;
- customer complaints;
- manual overrides;
- cost per prediction;
- downstream errors;
- delayed outcomes;
- human review rates;
- feedback-loop quality.

This is one of the main reasons the old definition of monitoring — “draw a drift chart” — is no longer sufficient.

---

# 3. What Has Changed in the Last Five Years?

| Earlier MLOps emphasis | Current production emphasis |
|---|---|
| The model is the primary artifact | The **system** is the artifact: data, features, code, model, API, workflow, policies, and observability |
| Experiment tracking | Full lineage: code → data → features → model → evaluation → deployment |
| Registry stages such as `Staging` and `Production` | Versioning, aliases, tags, policies, approvals, and deployment metadata |
| One-time API deployment | Batch, online, and streaming; safe rollout, rollback, shadow, and canary |
| Monitoring accuracy and drift | Service + infrastructure + data + model + business + cost observability |
| Automatic retraining as the goal | Deliberate retraining with schedule, event, or manual triggers plus evaluation gates and approvals |
| CI/CD for Python code | CI/CD/CT with code, data, model, policy, and evaluation checks |
| One cloud-specific stack | Architecture patterns and portable interfaces |
| A central MLOps team receiving tickets | Self-service platforms and golden paths |
| Mostly manual infrastructure development | AI-assisted engineering with mandatory verification |
| Predictive ML only | A common production foundation plus GenAI-specific artifacts |

Major cloud providers and platform vendors increasingly describe GenAIOps not as a replacement for MLOps, but as an extension of the lifecycle.

Traditional artifacts still matter:

- code;
- data;
- features;
- model binaries;
- environments;
- deployments;
- metrics.

GenAI adds new artifacts:

- prompts;
- chains and workflows;
- retrieval indexes;
- evaluation datasets;
- adapters;
- tool definitions;
- safety policies;
- conversation traces;
- token usage;
- user feedback.

## Monitoring Has Become Observability

A modern course should teach at least five observability layers.

### 1. Service

- availability;
- latency;
- throughput;
- errors;
- saturation.

### 2. Infrastructure

- CPU and GPU;
- memory;
- disk;
- queue depth;
- network;
- autoscaling behavior.

### 3. Data

- freshness;
- schema;
- missing values;
- distributions;
- ranges;
- category coverage;
- point-in-time correctness.

### 4. Model

- prediction distribution;
- calibration;
- quality;
- drift;
- segment performance;
- delayed-label evaluation;
- online/offline consistency.

### 5. Product and Business

- adoption;
- conversion;
- revenue or savings;
- user feedback;
- manual intervention;
- cost per successful outcome.

For GenAI systems, additional signals include:

- prompt and model versions;
- traces;
- retrieved documents;
- tool calls;
- token usage;
- judge scores;
- safety failures;
- user feedback;
- provider errors;
- cache hit rate.

OpenTelemetry is developing semantic conventions for generative AI observability. This is a useful example of why the course should focus on concepts and interfaces rather than one vendor-specific tool.

Relevant source:

- [OpenTelemetry](https://opentelemetry.io/)

---

# 4. What Is Outdated in the Current MLOps Zoomcamp?

The overall learning path is still strong:

- infrastructure;
- experiment tracking and model registry;
- orchestration;
- deployment;
- monitoring;
- testing and CI/CD;
- final project.

The problem is not the list of topics. The problem is that some modules reflect the technical reality of 2022–2024 too closely.

Current course page:

- [MLOps Zoomcamp](https://datatalks.club/blog/mlops-zoomcamp.html)
- [GitHub repository](https://github.com/DataTalksClub/mlops-zoomcamp)

## Module Audit

| Module | Recommendation | What should change |
|---|---|---|
| **Introduction and environment** | Rewrite the setup | Replace old Anaconda-based setup with a modern reproducible environment, `pyproject.toml`, lockfiles, containers or devcontainers, and a consistent task runner |
| **Experiment tracking and MLflow** | Keep and update | The concept remains relevant, but registry stages are deprecated; teach aliases, tags, lineage, and promotion criteria |
| **Orchestration** | Rewrite substantially | Avoid teaching five orchestrators at once; choose one canonical tool and teach workflow design, retries, idempotency, partitioning, backfills, and failure handling |
| **Deployment** | Keep patterns, replace the canonical lab | Retain Flask, Lambda, and Kinesis as optional or legacy examples; use batch scoring and containerized FastAPI as the main path |
| **Monitoring** | Rewrite most aggressively | Replace a narrow drift-dashboard approach with end-to-end observability, SLOs, delayed labels, business metrics, alerting, incidents, and postmortems |
| **Best practices and CI/CD** | Keep and expand | Add data contracts, model and evaluation gates, secrets, security scanning, deployment policies, lineage, and cost checks |
| **Final project** | Replace the rubric | Reward reproducibility, reliability, observability, safe releases, cost awareness, security, and engineering trade-offs — not the number of tools or cloud services |

## The Main Pedagogical Problem

A course should not treat “ask ChatGPT to implement one of several tools” as a substitute for instruction.

AI should absolutely be used in the refreshed course, but in a controlled way:

> AI produces a first draft. The learner must verify its behavior through tests, metrics, controlled failures, and an explicit architecture rationale.

DORA research makes a similar point: AI amplifies the engineering system that already exists. In organizations with weak delivery foundations and poor feedback loops, AI can increase output while reducing stability.

Relevant source:

- [DORA](https://dora.dev/)

---

# 5. What Do Modern 2026 Programs Teach?

An important distinction: some programs were newly launched in 2026, while others were existing courses updated in 2026.

## Google Cloud: MLOps for Generative AI

Google’s current curriculum combines predictive ML and GenAI rather than replacing one with the other.

Common topics include:

- feature stores;
- training pipelines;
- model evaluation;
- lineage;
- automated workflows;
- Kubeflow components;
- AI-assisted data science workflows.

What MLOps Zoomcamp can learn from this:

- teach one lifecycle for predictive and generative systems;
- make evaluation part of the pipeline;
- teach lineage and reusable workflow components;
- treat AI agents as engineering assistants or workloads, not as a magical separate discipline.

Reference:

- [Google Cloud MLOps specialization on Coursera](https://www.coursera.org/specializations/machine-learning-operations-mlops-on-google-cloud)

## Microsoft AI-300: Operationalizing Machine Learning and Generative AI Solutions

Microsoft now explicitly combines MLOps and GenAIOps in one operational role.

The program includes:

- infrastructure;
- traditional ML lifecycle management;
- GenAI applications and agents;
- evaluation;
- monitoring;
- optimization;
- GitHub Actions;
- command-line tooling;
- infrastructure as code.

What to adopt:

- a shared operations layer for ML and GenAI;
- infrastructure, observability, and governance as first-class topics;
- post-deployment evaluation and optimization;
- agents as one workload type rather than the center of the course.

Reference:

- [Microsoft AI-300](https://learn.microsoft.com/en-us/training/courses/ai-300t00)

## Carnegie Mellon: Machine Learning in Production

The CMU course includes classical ML, LLMs, and agents, but its organization is centered on real production systems:

- real users;
- production load;
- safety;
- security;
- fairness;
- transparency;
- deployment and operations.

This is a particularly useful model for rethinking MLOps Zoomcamp. The course is organized around engineering decisions and failure modes, not a list of tools.

What to adopt:

- start with product and system requirements, not MLflow;
- discuss failure modes and risks before choosing tools;
- evaluate architecture by consequences, not technology count.

Reference:

- [CMU Machine Learning in Production](https://mlip-cmu.github.io/)

## KodeKloud: Hands-on MLOps

This curriculum still focuses heavily on classic MLOps:

- ingestion;
- orchestration;
- tracking;
- deployment;
- monitoring;
- governance;
- CI/CD/CT.

This is a strong signal that traditional production ML has not disappeared and does not need to become an LLM-only curriculum.

Reference:

- [Fundamentals of MLOps specialization](https://www.coursera.org/specializations/fundamentals-of-mlops)

## Board Infinity: MLOps

Topics include:

- FastAPI;
- Docker;
- GitHub Actions;
- AWS, Azure, and GCP;
- multi-model APIs;
- A/B testing;
- latency;
- batch and real-time deployment.

Again, the course is not attempting to replace all production ML with generative AI.

Reference:

- [Machine Learning Operations specialization](https://www.coursera.org/specializations/machine-learning-operations-mlops)

## MLOps and LLMOps

Current LLMOps-focused programs commonly cover:

- token cost;
- latency;
- reliability;
- LLM-as-a-judge gates;
- tracing;
- RAG;
- deployment patterns;
- evaluation datasets;
- safety checks.

This is useful as a reference for an additional GenAI module, but it should not become the template for the entire MLOps Zoomcamp.

Reference:

- [MLOps and LLMOps course](https://www.coursera.org/learn/mlops-and-llmops-deploying-and-scaling-ai-in-production)

## Overall Pattern

Strong modern programs tend to follow one of two models:

1. Keep a complete production ML foundation and add GenAI evaluation and observability.
2. Create a separate LLMOps module or specialization.

They generally do not claim that predictive ML is obsolete or that all MLOps should now be about prompts and vector databases.

---

# 6. Recommended New Course Structure

## Module 0. Production ML Systems, Not Just Models

The first module should give learners a map of the complete system:

- source data;
- transformations;
- features;
- training;
- evaluation;
- registry;
- batch and online inference;
- downstream consumers;
- feedback;
- observability;
- governance.

The key learning objective is to distinguish:

- model performance;
- service performance;
- product performance.

The technical setup should include:

- a modern Python project;
- `pyproject.toml`;
- locked dependencies;
- a Makefile or task runner;
- container or devcontainer;
- configuration management;
- secrets separation.

## Module 1. From Notebook to Maintainable ML Code

The goal should go beyond moving notebook cells into `.py` files.

Topics:

- package structure;
- explicit interfaces;
- configuration;
- data contracts;
- unit tests;
- property-based tests;
- deterministic behavior;
- reproducible training;
- dependency boundaries;
- logging and error handling.

### AI Exercise

Ask AI to refactor a poorly organized notebook into a package.

Then give the learner:

- hidden tests;
- edge cases;
- intentionally broken assumptions;
- reproducibility requirements.

The learner is evaluated on whether they can identify and correct AI-generated problems.

## Module 2. Experiments, Datasets, Lineage, and Registry

MLflow is worth keeping.

It now spans:

- traditional experiment tracking;
- model registry;
- tracing;
- evaluation;
- prompt management;
- GenAI and agent workflows.

This makes it a useful bridge between classical ML and generative AI.

The course should teach:

- what must be logged;
- how a run is connected to code and data versions;
- how models are compared;
- how promotion criteria are defined;
- how aliases and tags are used;
- how a deployment can be reproduced;
- how experiment tracking differs from production lineage.

Reference:

- [MLflow documentation](https://mlflow.org/docs/latest/)

## Module 3. Pipelines and Orchestration

Choose **one canonical orchestrator** for the main course path.

Other tools can be presented in:

- a comparison guide;
- optional labs;
- community-maintained examples.

Core concepts:

- tasks and assets;
- schedules and event triggers;
- retries;
- idempotency;
- partitioning;
- backfills;
- caching;
- artifacts;
- failure handling;
- local and remote execution;
- lineage;
- pipeline observability.

### Tool Choice

Two reasonable options:

- **Airflow** — broad industry recognition and strong overlap with data engineering;
- **Dagster** — a modern asset-oriented teaching model and strong developer experience.

The exact tool matters less than avoiding a catalog of five orchestrators.

## Module 4. Serving and Safe Delivery

The module should present three first-class deployment modes.

### Batch

Batch inference should not be treated as a simplified deployment mode. In many real systems it is the primary architecture.

Topics:

- partitioned jobs;
- backfills;
- output contracts;
- idempotency;
- freshness SLAs;
- cost control;
- downstream dependencies.

### Online

Canonical lab:

- FastAPI or a specialized serving framework;
- Docker;
- model loading and warm-up;
- health and readiness checks;
- schema validation;
- load testing;
- latency budgets;
- autoscaling;
- a managed container runtime.

### Streaming

Keep streaming as an advanced or optional lab.

Kinesis and Lambda can remain as a legacy AWS implementation, but they should not define the required path for every learner.

### Release Engineering

Add:

- model and API compatibility;
- canary deployments;
- shadow deployments;
- blue-green deployments;
- rollback;
- version routing;
- validation on production-like traffic.

KServe can be introduced as an optional Kubernetes implementation of these patterns rather than a mandatory prerequisite.

Reference:

- [KServe rollout strategies](https://kserve.github.io/website/docs/model-serving/predictive-inference/rollout-strategies/canary)

## Module 5. Observability, Reliability, and Incidents

This should become the central module of the refreshed course.

### What to Measure

**Service metrics**

- availability;
- error rate;
- p50, p95, and p99 latency;
- throughput.

**Data metrics**

- freshness;
- missing values;
- schema validity;
- ranges;
- categories;
- coverage.

**Model metrics**

- prediction distribution;
- calibration;
- drift;
- segment performance;
- delayed-label quality.

**Product metrics**

- adoption;
- business outcome;
- human override;
- cost per successful decision.

**Pipeline metrics**

- duration;
- failures;
- retries;
- stale partitions;
- data availability.

### Practical Assignment

Run a service and deliberately introduce:

- a schema change;
- stale data;
- a latency regression;
- a distribution shift;
- a broken dependency;
- quality degradation for one user segment.

The learner must:

1. detect the problem;
2. define an alert;
3. estimate the impact;
4. localize the cause;
5. perform mitigation or rollback;
6. write a short postmortem.

This is much closer to real production work than building only a drift dashboard.

### Tools

Possible stack:

- OpenTelemetry for traces, metrics, and context;
- Prometheus and Grafana for service and infrastructure metrics;
- Evidently or custom checks for data and model quality;
- structured logging;
- alerting.

For advanced GenAI serving, vLLM can be shown as an optional runtime with Prometheus metrics and per-request information useful for SLA and cost accounting.

Reference:

- [vLLM metrics documentation](https://docs.vllm.ai/en/stable/design/metrics/)

## Module 6. CI/CD, Infrastructure, Security, Governance, and Cost

The existing best-practices module can become a complete quality system.

The pipeline should check:

- formatting and static analysis;
- unit tests;
- integration tests;
- contract tests;
- data contracts;
- training reproducibility;
- model quality thresholds;
- segment regressions;
- latency;
- container image size;
- dependency vulnerabilities;
- infrastructure plans;
- evaluation reports;
- approval requirements for production.

Additional topics:

- Terraform or OpenTofu;
- IAM and least privilege;
- secrets management;
- dependency scanning;
- artifact signing and SBOMs as advanced topics;
- data access controls;
- audit logs;
- lineage;
- cost budgets and quotas.

A feature store should be taught as a solution to specific problems:

- training-serving consistency;
- point-in-time correctness;
- reusable online features.

It should not be presented as mandatory for every ML system.

## Module 7. GenAIOps and LLMOps Extension

This module should answer:

> What remains the same in the production lifecycle, and what is specific to LLM, RAG, and agent systems?

### What Remains the Same

- version control;
- CI/CD;
- deployment;
- access control;
- observability;
- rollback;
- SLOs;
- cost management;
- incident response;
- user feedback.

### What Is Added

- prompt versioning;
- model and provider versions;
- chain and agent configuration;
- retrieval corpus and index lineage;
- evaluation datasets;
- deterministic checks;
- model-based evaluation;
- human review;
- traces and tool calls;
- prompt-injection checks;
- unsafe-output checks;
- token cost;
- context size;
- cache hit rate;
- provider fallback;
- conversation-level evaluation.

Cloud providers describe GenAIOps in this way: as a specialized extension of MLOps with prompt management, retrieval, evaluation, monitoring, and feedback loops.

Reference:

- [AWS Generative AI Lens](https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/genops04-bp02.html)

### Why LLMOps Should Not Become the Main Focus

LLM tooling changes much faster than the underlying production concepts. A course organized around the currently popular agent framework may become outdated again very quickly.

A better design is to build one small RAG or tool-using application and use it to teach:

- evaluation;
- tracing;
- versioning;
- safe release;
- latency and cost trade-offs;
- incident investigation.

GenAI becomes a **second workload** that demonstrates the same production principles.

---

# 7. How AI Should Be Used by Learners

AI has changed ML engineering in two different ways:

1. Engineers now operate GenAI systems.
2. Engineers use AI to build and maintain all kinds of software, including predictive ML systems.

These topics should be taught separately.

## AI as an Engineering Assistant

AI can be used for:

| Task | How AI helps | What the engineer must verify |
|---|---|---|
| Notebook to package | Refactoring and scaffolding | Interfaces, hidden state, reproducibility |
| Tests | Generating test cases | Coverage, meaningful assertions, edge cases |
| Pipeline | Generating DAGs or assets | Idempotency, retries, backfills, dependencies |
| API | Scaffolding endpoints | Validation, concurrency, error handling |
| Infrastructure as code | Drafting Terraform | IAM, destructive changes, networking, cost |
| Monitoring | Suggesting alerts | Signal quality, thresholds, false positives |
| Incident analysis | Summarizing logs and traces | Root cause and supporting evidence |
| Evaluation | Generating synthetic cases and rubrics | Bias, leakage, representativeness |
| Documentation | Drafting runbooks and ADRs | Accuracy and alignment with actual behavior |

## Mandatory AI Verification Protocol

Every AI-assisted task should end with five artifacts:

1. the code or configuration diff;
2. tests;
3. execution evidence;
4. a short explanation of the decision;
5. a list of known risks or unverified assumptions.

This teaches learners both how to use AI and how not to trust it blindly.

The final project can require an **AI-use disclosure**:

- where AI was used;
- which tool was used;
- what it generated;
- how the result was verified;
- which AI mistakes were discovered.

The course should evaluate the quality of the verification process, not whether AI was used.

---

# 8. Recommended Technology Stack

The course should not become a large product catalog. It should define capabilities and choose one canonical tool for each capability.

| Capability | Canonical option | Optional or advanced alternatives |
|---|---|---|
| Python environment | `pyproject.toml` and locked dependencies | devcontainer or Codespaces |
| Experiment tracking and registry | MLflow | Managed alternatives in a comparison guide |
| Orchestration | Airflow **or** Dagster | Prefect, Kestra, and Mage as optional labs |
| Batch inference | Orchestrated Python job | Spark or Databricks as advanced topics |
| Online serving | FastAPI plus container | BentoML or Ray Serve |
| Kubernetes serving | Not required | KServe as advanced |
| LLM inference | Provider API in the basic lab | vLLM as advanced |
| Metrics | Prometheus and Grafana | Managed cloud monitoring |
| Tracing | OpenTelemetry | MLflow tracing or specialized LLM tools |
| Data and model checks | Contracts plus Evidently or custom checks | Great Expectations and alternatives |
| CI/CD | GitHub Actions | Reusable workflows |
| Infrastructure as code | Terraform or OpenTofu | Cloud-specific modules |
| Packaging and release | Docker | Registry, signing, and SBOMs as advanced |

## Technology Selection Principles

### Do Not Make Kubernetes Mandatory

Kubernetes is important for platform engineering, but it creates too much complexity for the first production path.

Learners should first understand:

- serving;
- scaling;
- rollout;
- rollback;
- observability.

These concepts can be taught on a managed container platform before introducing Kubernetes.

### Keep MLflow

MLflow is one of the few cases where updating the existing stack is more practical than replacing it.

It now supports:

- traditional ML tracking;
- registry;
- evaluation;
- tracing;
- prompts;
- LLM and agent workflows.

This makes it a useful bridge between classical and generative AI.

### Treat Batch as a First-Class Pattern

An online endpoint is not the universal endpoint of every ML project.

Batch remains critical for:

- recommendations;
- risk scoring;
- forecasting;
- enrichment;
- scheduled decision systems;
- large-scale offline processing.

### Separate Stable Concepts from Versioned Labs

A video about idempotency, canary deployments, or delayed labels can remain useful for years.

A step-by-step tutorial tied to one specific version of Prefect or Evidently may become outdated within months.

The course should explicitly separate:

- stable conceptual lessons;
- versioned hands-on labs.

---

# 9. Redesigning the Final Project

The current style of rewarding additional technologies or cloud services can encourage architecture theater. Learners may add more tools without creating a more reliable system.

The new rubric should reward evidence and engineering quality.

## 1. Product Framing

- user or consumer;
- prediction or decision;
- latency and freshness expectations;
- business metric;
- baseline;
- failure impact.

## 2. Reproducibility and Lineage

- versioned code and configuration;
- repeatable environment;
- dataset and version information;
- training run;
- model alias or version;
- deployment metadata.

## 3. Automated Quality Gates

- code tests;
- data checks;
- model evaluation;
- segment evaluation;
- integration or contract tests;
- latency or load tests.

## 4. Deployment and Rollback

- batch or online deployment;
- explicit release process;
- previous version retention;
- rollback or version routing;
- compatibility considerations.

## 5. Observability

- service metrics;
- data and model metrics;
- product metric;
- logs or traces;
- alert;
- dashboard.

## 6. Operations

- runbook;
- one simulated incident;
- diagnosis;
- mitigation;
- postmortem.

## 7. Security, Governance, and Cost

- secrets;
- access model;
- data sensitivity;
- auditability and lineage;
- rough cost model or budget;
- known risks.

## 8. Engineering Rationale

The learner should explain:

- why batch or online was selected;
- why a feature store is or is not needed;
- why the orchestrator was selected;
- which trade-offs were consciously accepted.

## 9. AI-Use Disclosure

- where AI was used;
- what it generated;
- how it was verified;
- which mistakes were found.

This project would demonstrate readiness for real production work much better than requiring Terraform, Kubernetes, and several AWS services in the same solution.

---

# 10. How to Use the Existing Traffic

## 10.1. Keep the Existing URL and Main Brand

Keep **MLOps Zoomcamp** in:

- the title;
- the URL;
- the repository name;
- the first paragraphs of the landing page.

This preserves accumulated search intent, backlinks, and community recognition.

Add a modern subtitle:

> **Production ML & AI Systems: From Experimentation to Reliable Operation**

A complete rename to “AI Platform Engineering Zoomcamp” might be more fashionable, but it would weaken the existing search and brand asset.

## 10.2. Clarify the Course Status Immediately

The landing page should explicitly state:

- the course is available in self-paced format;
- there is no live cohort in 2026;
- materials are being refreshed;
- which modules are current;
- which modules are legacy;
- where users can subscribe for updates.

The landing page and repository should communicate the same status.

## 10.3. Publish “What Changed in MLOps Since the First Edition?”

This can become an independent SEO article and an entry point into the new course.

Possible sections:

- model stages → aliases and policies;
- Flask-only deployment → batch plus container serving;
- drift dashboard → end-to-end observability;
- CI/CD → quality and policy gates;
- model artifact → production system;
- MLOps → ML and AI platform engineering;
- the LLMOps delta;
- AI-assisted engineering.

This article would explain the reason for the update to the old audience and provide a modern map of the field to new visitors.

## 10.4. Separate Stable Concepts from Versioned Labs

Each lesson can show:

- **Concept status:** stable;
- **Lab verified:** date;
- **Tested versions:** versions;
- **Maintainer:** core or community;
- **Legacy alternative:** link.

This prevents an outdated Prefect lab from making the orchestration concept itself look obsolete.

## 10.5. Use Traffic as a Research Channel

Add a short intent survey instead of only a generic waitlist.

Useful questions:

- current role;
- goal: job, production project, or platform work;
- predictive ML or GenAI;
- largest production challenge;
- preferred cloud or local-first;
- self-paced or cohort;
- interest in capstone review.

Also analyze:

- module-to-module navigation;
- drop-off;
- search queries;
- GitHub issues;
- Slack questions;
- popular older videos;
- project starts and completions.

This allows the refresh to be driven by actual user intent rather than assumptions.

## 10.6. Turn the Page into a Router for the DataTalksClub Ecosystem

Visitors may have different goals:

- production ML → refreshed MLOps core;
- LLMs, RAG, and agents → LLM Zoomcamp;
- AI-assisted development → AI developer tooling content;
- model training fundamentals → ML Zoomcamp.

The old traffic can support the broader educational ecosystem even before the full course refresh is complete.

---

# 11. How to Update the Course Without Rewriting Everything

## First: Fix Trust and Navigation

1. Synchronize the landing page and README.
2. Clearly mark self-paced status and no 2026 cohort.
3. Add status and last-verified dates to each module.
4. Publish a refresh roadmap.
5. Preserve a legacy branch or release.

## Then: Update the Most Outdated Areas

Recommended priority:

1. **Monitoring → Observability and Reliability**
2. **Orchestration**
3. **Serving and Safe Delivery**
4. **Environment and reproducibility**
5. **MLflow migration**
6. **Final project rubric**
7. **GenAIOps extension**

Monitoring, orchestration, and deployment will determine whether the course feels like modern production engineering or a historical overview of MLOps tooling.

## Preserve Stable Explanations

Many conceptual lessons can remain:

- experiment tracking;
- model registry;
- testing;
- CI/CD;
- infrastructure as code;
- batch versus online;
- deployment patterns.

They may only need:

- a new introduction;
- a migration note;
- an updated lab.

## Use a Refresh Format Before a Full Cohort

Before launching a complete new cohort, publish a smaller **MLOps Refresh**:

- a new introductory lecture;
- one modern end-to-end project;
- an observability and incident lab;
- a GenAIOps extension;
- a new capstone rubric.

This can reveal which demand is actually behind the existing traffic:

- career transition;
- practical production engineering;
- GenAI;
- platform engineering;
- older backlinks and historical interest.

---

# 12. What Not to Do

## Do Not Turn the Course into a LangChain and Agents Course

That would become outdated quickly and overlap with LLM Zoomcamp.

## Do Not Teach Five Orchestrators in the Main Path

Use one canonical implementation. Keep others in comparisons or community labs.

## Do Not Make Kubernetes Mandatory

It should be an advanced platform-engineering path.

## Do Not Define Monitoring as a Drift Dashboard

Monitoring must cover reliability, data, models, products, cost, and incidents.

## Do Not Use “Ask ChatGPT” as a Replacement for Course Material

AI should participate in a controlled engineering workflow with verification.

## Do Not Reward Technology Count

Evaluate evidence, reliability, reproducibility, and trade-offs.

## Do Not Treat Continuous Retraining as the Highest Maturity Level

For many systems, controlled retraining with evaluation and approval is more mature than fully automatic retraining.

## Do Not Create a Completely New Website or Repository

Update the existing asset and preserve links, history, and community.

---

# Final Recommendation

The strongest next version is:

## **MLOps Zoomcamp: Production ML & AI Systems**

### Course Promise

> Learn how to turn an ML or AI prototype into a production system that can be reproduced, tested, released safely, observed, operated, improved, governed, and controlled for cost.

### Core Curriculum

- maintainable ML code;
- lineage and registry;
- pipelines;
- batch and online serving;
- safe releases;
- observability;
- incidents;
- CI/CD and infrastructure as code;
- security, governance, and cost.

### Modern Extension

- prompts, RAG, and agent artifacts;
- evaluation and tracing;
- user feedback;
- safety;
- token and latency economics;
- provider and model versioning.

### AI in the Learning Process

Learners use AI for:

- code;
- tests;
- infrastructure as code;
- debugging;
- documentation.

Every AI-generated change must be supported by:

- tests;
- metrics;
- execution evidence;
- an explanation;
- a risk assessment.

This structure does not depend on whether predictive ML, RAG, or agents are the most fashionable topic next year.

It teaches the more durable skill:

> **How to engineer and operate systems that contain ML or AI components.**
