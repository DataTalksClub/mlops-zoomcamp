---
video_url: "https://www.youtube.com/watch?v=s0uaFZSzwfI&list=PL3MmuxUbc_hIUISrluw_A7wDSmfOhErJK"
---

# Introduction

MLOps is the set of practices we use to put machine learning into production. We use a taxi ride duration model throughout the course. It gives us one problem to follow from the first experiment to a running service.

## From a question to a prediction

We start by predicting taxi ride duration. A passenger supplies a pickup and drop-off location, and our model predicts the trip duration.

![A taxi trip drawn from a pickup location to a destination](images/01-introduction-01-taxi-trip.jpg)

The prediction is useful only when another application can call it. We expose the model through an API, send the trip information to that API, and return an estimated duration.

![A taxi trip prediction represented as an API deployment](images/01-introduction-02-deployment.jpg)

## Design, train, and operate

The course describes the work in three broad stages.

- During design, we decide whether machine learning is the right tool for the problem.
- During training, we prepare data, run experiments, and choose a model.
- During operation, we deploy the model, serve new requests, and check that its performance stays useful.

![The three stages of an ML project](images/01-introduction-03-design-train-operate.jpg)

MLOps connects these stages through experiment tracking, deployment, and monitoring. Tracking helps us reproduce a result, deployment makes the model available to other systems, and monitoring tells us when the data or model needs attention.
