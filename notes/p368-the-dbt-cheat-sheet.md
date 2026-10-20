---
id: p368
title: "The dbt cheat sheet"
slug: the-dbt-cheat-sheet
sections: [devsecops]
topic: "Data engineering"
tags: [dbt, DataEngineering, AnalyticsEngineering, SQL, DataPipelines]
source: "LinkedIn post P368 · Data series"
linkedin_date: 2029-02-01
design: cheatsheet
---

# The dbt cheat sheet

A dbt project is a graph, and every command chooses part of it. Four blocks cover the working day.

## Quick reference

### Build

```bash
dbt build
dbt build --select staging+
dbt run --full-refresh
dbt seed
dbt snapshot
```

### Test

```bash
dbt test
dbt test --select +orders
dbt test --store-failures
dbt test --select source:raw
dbt source freshness
```

### Run

```bash
dbt run
dbt run --select +orders
dbt run --select orders+
dbt run --exclude tag:slow
dbt compile --select orders
```

### Docs

```bash
dbt docs generate
dbt docs serve --port 8080
dbt ls --select tag:nightly
dbt debug
dbt parse
```

## Explained

### Build

`dbt build` runs models, tests, seeds and snapshots in dependency order, and tests each node as it is built, so a failure stops everything downstream. `dbt build --select staging+` adds everything downstream, and `dbt run --full-refresh` rebuilds a model whose SQL changed shape.

### Test

`dbt test` runs the schema tests and the singular tests you wrote. `--select +orders` tests orders and everything upstream, `--store-failures` writes the failing rows to a table you can query, `--select source:raw` tests the sources themselves, and `dbt source freshness` compares loaded_at with the declared thresholds.

### Run

`dbt run` executes models only, which is faster and less safe. `--select +orders` builds upstream first, `--select orders+` builds downstream, `--exclude tag:slow` removes a tagged set, and dbt compile renders the SQL without running it, which checks a Jinja change before it costs a warehouse.

### Docs

`dbt docs generate` writes the manifest and catalogue the docs site reads, and `dbt docs serve --port 8080` opens it. dbt ls shows what a selector would run without running it. `dbt debug` checks the connection and the profile; `dbt parse` validates the project.

> **The honest caveat:** dbt tests are SQL you wrote, so a project can pass them all and still publish a wrong number. The test only checks the rule somebody thought of.

> **The lesson:** selection is the skill, and the command is just the verb.

## In one line

> **The DAG decides the order.** You name the nodes; dbt works out what runs before what.

**See the selection**

```bash
dbt ls --select staging+
```
