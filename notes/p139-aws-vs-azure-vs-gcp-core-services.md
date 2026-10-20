---
id: p139
title: "AWS vs Azure vs GCP: core services"
slug: aws-vs-azure-vs-gcp-core-services
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [AWS, Azure, GCP, CloudComputing, DevOps]
source: "LinkedIn post P139 · IT series"
linkedin_date: 2027-08-17
design: matrix
---

# AWS vs Azure vs GCP: core services

The three big clouds look overwhelming until you notice they offer the same building blocks under different names. Learn the concept once and you can work on any of them.

## Quick reference

| | **AWS** | **Azure** | **GCP** |
|:--|:--|:--|:--|
| Virtual machines | EC2 | Virtual Machines | Compute Engine |
| Object storage | S3 | Blob Storage | Cloud Storage |
| Managed Kubernetes | EKS | AKS | GKE |
| Serverless functions | Lambda | Functions | Cloud Functions |
| Managed SQL | RDS | SQL Database | Cloud SQL |
| Identity | IAM | Entra ID | Cloud IAM |

**How to pick**

- **Learn one deeply** → the concepts transfer to the others.
- **AWS** → biggest, most services. Azure  ->  Microsoft shops.
- **GCP** → strong Kubernetes and data. Names differ, ideas match.

## Explained

Virtual machines: EC2 on AWS, Virtual Machines on Azure, Compute Engine on GCP. A server you rent by the hour. The starting point for lift-and-shift.

Object storage: S3, Blob Storage, Cloud Storage. Cheap, near-unlimited storage for backups, media and static files, accessed over HTTPS. S3 is so common its API is a de facto standard.

Managed Kubernetes: EKS, AKS, GKE. The cloud runs the Kubernetes control plane so you do not have to. GKE is often praised as the most polished, since Google created Kubernetes.

Serverless functions: Lambda, Azure Functions, Cloud Functions. Run code on an event without managing servers. Great for glue and automation, and you pay per execution.

Managed SQL: RDS, Azure SQL Database, Cloud SQL. A database where the cloud handles backups, patching and failover.

Identity: IAM, Entra ID, Cloud IAM. Who can do what. This is the part people underestimate, and the part attackers love when it is too permissive.

The practical advice: pick one cloud and learn it deeply. The hard concepts, networking, IAM, storage classes and cost, transfer almost directly. After that, a new cloud is mostly learning new names.

One warning on all three: data egress, moving data out, is where surprise bills come from.

## In one line

> **Different names, same building blocks.** Learn the concept once; the console is just labels.

**Know your bill:** compute + storage + egress
