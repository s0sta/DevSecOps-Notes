---
id: p184
title: "Azure Blob storage tiers: Hot vs Cool vs Archive"
slug: azure-blob-storage-tiers-hot-vs-cool-vs-archive
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [Azure, AZ104, CloudStorage, CloudComputing, CostOptimization]
source: "LinkedIn post P184 · Cloud / DevSecOps series"
linkedin_date: 2027-11-30
design: matrix
---

# Azure Blob storage tiers: Hot vs Cool vs Archive

Azure Blob storage has access tiers, and picking the right one is both an AZ-104 topic and a real way to cut the cloud bill. The trade-off is always between storage cost and access cost.

## Quick reference

| | **Hot** | **Cool** | **Archive** |
|:--|:--|:--|:--|
| Storage cost | ❌ Highest | 🟡 Lower | ✅ Lowest |
| Access cost | ✅ Lowest | 🟡 Higher | ❌ Highest |
| Retrieval time | ✅ Instant | ✅ Instant | ❌ Hours (rehydrate) |
| Min retention | None | 30 days | 180 days |
| Best for | Live data | Backups, monthly | Compliance, cold |
| Example | Website assets | Last quarter's logs | 7-year archives |

**How to pick**

- **Hot** → data you read often. Cheap to access, costly to store.
- **Cool** → backups you rarely touch but may need soon.
- **Archive** → cold data for years. Cheapest, but slow to get back.

## Explained

Hot tier has the highest storage cost but the lowest access cost, and data is available instantly. It is for data you read often: website images, active app data, anything served to users right now.

Cool tier lowers the storage cost in exchange for higher access costs and a 30-day minimum retention. It suits backups and data you rarely touch but might need soon, like last quarter's logs. Reading it a lot in Cool can cost more than just keeping it Hot, so it is for genuinely infrequent access.

Archive tier is the cheapest to store and the most expensive and slowest to read. Data is offline, and retrieving it means a rehydration that can take hours. The minimum retention is 180 days. It is for compliance copies and cold data you must keep for years but almost never open.

### How to choose

Read often: Hot. Rarely, but need it fast when you do: Cool. Keep for years, fine to wait: Archive.

The feature that makes it automatic: lifecycle management rules. You can move blobs Hot to Cool to Archive based on age, so old data drifts to cheaper tiers without anyone remembering to do it.

The two mistakes to avoid: frequently reading Cool or Archive data (the access cost bites), and leaving everything in Hot forever (the storage cost bites).

## In one line

> **Match the tier to the access.** Wrong tier means a surprise bill or a slow restore.

**Set a lifecycle rule:** auto-move blobs Hot -> Cool -> Archive by age
