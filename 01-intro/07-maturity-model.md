---
video_url: "https://www.youtube.com/watch?v=XwTH8BDGzYk&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK"
---

# MLOps Maturity Model

The maturity model helps us choose the amount of automation a project actually needs. It describes five levels, from a manually executed notebook to a system that automatically detects a problem, retrains a model, and deploys the replacement.

## Level 0: no MLOps automation

At level 0, we work in a notebook without a proper pipeline, experiment tracking, or model metadata. A data scientist may give the notebook to an engineer, who then reimplements it for a service. This level is often enough for an early proof of concept.

## Level 1: DevOps without MLOps

At level 1, the team adopts normal software engineering practices. Releases are automated, tests cover the service, CI/CD runs the checks, and operational metrics show whether the service is available. The team still lacks ML-specific tracking, easy model reproduction, and a clear connection between the data scientists and engineers.

## Level 2: automated training

At level 2, a command such as `python train.py` runs the training process without opening a notebook. The script accepts parameters such as the training month, records experiments, and identifies the model currently in production. Deployment may still be manual, but the training process is repeatable and low friction.

## Level 3: automated deployment

At level 3, the trained model moves to a serving platform as part of the workflow. The platform can expose a model endpoint and may support A/B tests that compare two model versions. Monitoring becomes part of the deployment process because we need to know whether the model works after it starts serving traffic.

## Level 4: full MLOps automation

At level 4, monitoring can trigger the rest of the process. The system detects model drift or a performance drop. It starts training, evaluates the new model, deploys it, and rolls it out to users when the result is better.

## Choose the level pragmatically

Not every project needs level 4. A proof of concept can stay at level 0, while a model moving into production needs reliable engineering practices. A team with several production models may benefit from tracking and automated training. Highly important or risky models may still need a human to approve the final deployment even when the surrounding steps are automated.

For this course, we target level 2 and parts of level 3. That means tracked experiments, repeatable training, several deployment modes, and monitoring that exposes problems before they remain hidden.
