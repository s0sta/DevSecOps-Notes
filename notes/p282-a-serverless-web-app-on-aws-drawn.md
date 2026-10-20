---
id: p282
title: "A serverless web app on AWS, drawn"
slug: a-serverless-web-app-on-aws-drawn
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [AWS, Serverless, CloudArchitecture, DevOps, CloudNative]
source: "LinkedIn post P282 · Visual series"
linkedin_date: 2028-07-16
design: architecture
---

# A serverless web app on AWS, drawn

The first serverless architecture you draw looks empty: six managed services and not one server to patch. The request path still has three tiers, and each tier fails differently.

## Quick reference

- **Tier 1 · Edge:** Route 53 (DNS) · API Gateway (API)
- **Tier 2 · Compute:** Lambda (FN) · SQS queue (SQS)
- **Tier 3 · Data:** DynamoDB (DB) · S3 objects (OBJ)

**Request flow:** Route 53 → API Gateway → Lambda → DynamoDB; Lambda → S3 objects; API Gateway → SQS queue → Lambda

## Explained

**Edge**  
Route 53 answers DNS and API Gateway is the front door. API Gateway can check the caller, applies throttling and sends the request to an integration; it can invoke Lambda directly or put a message on a queue. Neither service is a machine you own, which is the point.

**Compute**  
Lambda runs the request. Fifteen minutes is the hard ceiling per invocation, so it suits short work rather than a nightly batch. When work can wait, API Gateway writes to SQS and Lambda polls the queue in batches through an event source mapping, adding concurrency as the backlog grows. The queue is the part that survives a traffic spike.

**Data**  
DynamoDB stores the session and the order, S3 stores the uploads, and the execution role is what lets Lambda write to either. Permissions live in that role, not in the function code. A VPC is optional here: add it only when the function must reach a private database, and then give it a NAT gateway for outbound internet calls.

> **The honest caveat:** serverless moves the operational work rather than deleting it. Cold starts, concurrency limits and per-request pricing become your capacity plan, and a retry storm on a queue can bill you twice for the same failure.

> **The lesson:** in a serverless diagram the arrows are permissions and queues, not cables.

## In one line

> **Draw the arrows, not the servers.** In serverless, the arrows are permissions and queues.

**Follow the function**

```bash
aws logs tail /aws/lambda/fn --follow
```
