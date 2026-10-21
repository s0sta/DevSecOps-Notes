---
id: p405
title: "SQL injection to a parameterised query, drawn"
slug: sql-injection-to-a-parameterised-query-drawn
sections: [devsecops]
topic: "Application & API security"
tags: [SQLInjection, AppSec, CyberSecurity, DevSecOps, WebSecurity]
source: "LinkedIn post P405 · DevSecOps series"
linkedin_date: 2029-04-29
design: explainer
---

# SQL injection to a parameterised query, drawn

The query looks harmless in the repository: a string, a variable, and a WHERE clause. The database sees one string too, and that is the whole problem.

## Quick reference

### The string concat

- Code and data share one string
- WHERE name = '" + name + "'
- The database cannot tell them apart

### The payload

- ' OR '1'='1' -- returns every row
- ' UNION SELECT password FROM users --
- The comment swallows the trailing quote

### The prepared statement

- SELECT \* FROM users WHERE name = ?
- The driver sends SQL and values separately
- The value can never become syntax

### The allow-list

- ORDER BY name is not a bindable parameter
- Map sort=name to a fixed column list
- Reject anything not on the list

> **Note:** Binding protects values; identifiers still need a list.

## Explained

### The string concat

The code builds SELECT \* FROM users WHERE name = '" + name + "'. The value is pasted into the statement before the database parses it. The parser cannot tell the developer's quote from the attacker's quote, because by then there is no difference.

### The payload

Send ' OR '1'='1' -- and the WHERE clause becomes true for every row; the comment swallows the trailing quote the developer added. A UNION SELECT can pull a password column into the response. No special tool is needed, only a parameter the app trusts.

### The prepared statement

The fix is to send the SQL and the values separately: SELECT \* FROM users WHERE name = ?. The driver parses the statement with a placeholder, then binds the value. The value is data at every stage and can never become syntax, even if it contains quotes, comments or a UNION.

### The allow-list

Binding has a boundary: identifiers cannot be parameters. ORDER BY ? does not sort by the column you pass, and a table name cannot be bound. Map the user's sort value to a fixed list of allowed columns and directions, and reject everything else.

> **The honest caveat:** prepared statements protect values, not identifiers, and an ORM that concatenates a column name reintroduces the same bug with nicer syntax.

> **The lesson:** bind the values and allow-list the names.

## In one line

> **Never build SQL with a string.** A prepared statement protects values; identifiers are still code.

**Test the param**

```bash
curl -si "$API/q?x=%27"
```
