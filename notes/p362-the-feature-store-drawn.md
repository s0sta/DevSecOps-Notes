---
id: p362
title: "The feature store, drawn"
slug: the-feature-store-drawn
sections: [devsecops]
topic: "Data engineering"
tags: [DataEngineering, FeatureStore, MachineLearning, MLOps, DataArchitecture]
source: "LinkedIn post P362 · Data series"
linkedin_date: 2029-01-18
design: architecture
---

# The feature store, drawn

The model that scored 0.91 in the notebook scored 0.74 in production, and nobody had retrained it. The same features were being computed twice, by two jobs that had drifted apart.

## Quick reference

- **Sources:** Event stream (EVT) · Orders database (DB) · Nightly dumps (DUMP)
- **Transform:** Batch job (BATCH) · Streaming job (FLOW) · Validation (CHECK)
- **Serve:** Online store (ONLN) · Offline store (OFFLN) · Training pipeline (TRAIN)

**Request flow:** Event stream → Streaming job → Online store; Orders database → Batch job → Validation → Offline store → Training pipeline; Nightly dumps → Batch job

## Explained

### Sources

The event stream carries clicks and orders as they happen, with a timestamp on every event. The orders database holds the current state and forgets what the row looked like last week. The nightly dumps are a full copy, once a day, and already hours old when they land.

### Transform

The batch job reads the database and the dumps and computes features over history. The streaming job reads the event stream and recomputes the last few seconds. Validation sits after the batch job and before the offline store: null counts, ranges, and a row count that has not collapsed, because a job that writes nothing should fail loudly.

### Serve

The online store answers one entity at a time on the request path, in milliseconds, keyed by user or order. The offline store keeps every historical value, so a training set can be assembled as of the moment each label happened. The training pipeline reads the offline store only, which is the point: training and serving share a definition, not a copy of the code.

> **The honest caveat:** a feature store does not fix a label that was written late, and a point-in-time join is only as correct as the event timestamp you feed it. A perfect feature from a wrong clock is still skew.

> **The lesson:** one definition, two stores, and a clock you can defend.

## In one line

> **One definition, two stores.** Online for the request, offline for the training set.

**Register features**

```bash
feast apply
```
