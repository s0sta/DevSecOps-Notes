---
id: p354
title: "The Kafka CLI cheat sheet"
slug: the-kafka-cli-cheat-sheet
sections: [devsecops]
topic: "Data engineering"
tags: [Kafka, DataEngineering, CommandLine, Streaming, DataOps]
source: "LinkedIn post P354 · Data series"
linkedin_date: 2028-12-31
design: cheatsheet
---

# The Kafka CLI cheat sheet

You need the lag for one group, the topic name is spelled two ways, and the documentation page is 400 lines. Four Kafka tools answer most of the questions you actually ask. The t and g in the commands are your topic and your group.

## Quick reference

### Topics

```bash
kafka-topics --list
kafka-topics --describe --topic t
kafka-topics --create --topic t
kafka-topics --delete --topic t
```

### Produce

```bash
kafka-console-producer --topic t
kafka-console-producer --topic t --sync
kafka-console-producer --topic t < e.json
echo hi|kafka-console-producer --topic t
```

### Consume

```bash
kafka-console-consumer --topic t
kafka-console-consumer --topic t --group g
kafka-console-consumer --include t
kafka-console-consumer --topic t|head -1
```

### Groups

```bash
kafka-consumer-groups --list
kafka-consumer-groups --describe --group g
kafka-consumer-groups --delete --group g
kafka-get-offsets --topic t --time -1
```

## Explained

**Topics**  
`kafka-topics --list` shows every topic. `--describe` adds the partitions, the leader and the replicas, `--create` makes one, and `--delete` removes it and its data. This is the tool you use before you touch anything else.

**Produce**  
`kafka-console-producer --topic t` opens a prompt where each line is a record. Add `--sync` to wait for the acknowledgement, redirect a file to send a batch, or pipe one line in from a script.

**Consume**  
`kafka-console-consumer --topic t` reads from the end by default. Add `--group g` to start from that group's committed offsets, use `--include` when the topic name is a family, and pipe through head when you only want one record. The group is what makes the read repeatable: a restart resumes where the last commit left off.

**Groups**  
`kafka-consumer-groups --list` finds the groups. `--describe --group g` is the lag report, `--delete --group g` removes the offsets, and `kafka-get-offsets --time -1` gives the broker's end offset, the number lag is measured against.

> **The honest caveat:** `--describe` shows state, not history. A lag of zero proves the consumer committed an offset, not that it processed the record correctly.

> **The lesson:** the flag you cannot remember is the one worth writing down.

## In one line

> **The flag is the whole job.** Four tools, one broker, and the flags that matter.

**See the lag**

```bash
kafka-consumer-groups --describe --group g
```
