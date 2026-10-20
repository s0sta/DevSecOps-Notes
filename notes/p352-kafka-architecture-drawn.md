---
id: p352
title: "Kafka architecture, drawn"
slug: kafka-architecture-drawn
sections: [devsecops]
topic: "Data engineering"
tags: [Kafka, DataEngineering, Streaming, Architecture, Backend]
source: "LinkedIn post P352 · Data series"
linkedin_date: 2028-12-26
design: architecture
---

# Kafka architecture, drawn

A customer updates an address and four teams want it before the commit returns. Kafka turns one write into an event without four integrations.

## Quick reference

- **Tier 1 · Producers:** Order service (APP) · CDC connector (CDC)
- **Tier 2 · Brokers:** KRaft controller (META) · Broker 1 (B1) · Broker 2 (B2) · Broker 3 (B3)
- **Tier 3 · Consumers:** Consumer group (CG) · Sink connector (SINK)

**Request flow:** KRaft controller → Broker 1 → Consumer group; Order service → Broker 1; Order service → Broker 2 → Sink connector; CDC connector → Broker 3 → Consumer group

**Around it:** Schema Registry (SR) · Kafka Connect (KC) · Monitoring (OPS)

## Explained

**Producers**  
The order service is a producer: it sends a record with a key and a value, and the key chooses the partition. The CDC connector is one too, but its source is the database transaction log, so a table change becomes a record without a second write.

**Brokers**  
Three brokers hold the partitions and their replicas. The order service writes to broker 1 and broker 2, which lead its partitions, and the CDC connector writes to broker 3. Every record is appended to a log and kept for a retention window you set, not for the slowest consumer. The KRaft controller sits beside them and holds the cluster metadata: which broker leads which partition. It carries no records, which is why it gets its own box.

**Consumers**  
The consumer group splits the partitions between its members, so a fourth member takes work off the other three. The sink connector reads the same topic and writes each record into the warehouse.

**Around the tiers**  
Schema Registry holds the record contract, Kafka Connect runs the connectors, and monitoring watches the lag.

> **The honest caveat:** a topic is not a queue or a database. Retention deletes old records whether or not your consumer read them, and a consumer that falls behind the window loses data without an error.

> **The lesson:** producers and consumers never meet. The topic is the contract, and its retention is part of it.

## In one line

> **The log is the contract.** Producers and consumers never meet; the topic is the agreement.

**Follow the lag**

```bash
kafka-consumer-groups --describe --group g
```
