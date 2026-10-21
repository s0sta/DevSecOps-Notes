---
id: p404
title: "XSS in four panels, drawn"
slug: xss-in-four-panels-drawn
sections: [devsecops]
topic: "Application & API security"
tags: [XSS, AppSec, WebSecurity, CyberSecurity, DevSecOps]
source: "LinkedIn post P404 · DevSecOps series"
linkedin_date: 2029-04-26
design: explainer
---

# XSS in four panels, drawn

An XSS report usually arrives as a screenshot with an alert box. The screenshot proves a payload ran; it does not say which kind, and the fix differs for each.

## Quick reference

### Reflected XSS

- Payload rides in the request and echoes back
- Crafted link: ?q=\<script>alert(1)\</script>
- Server-side encoding stops the echo

### Stored XSS

- Payload is saved: a comment, profile or ticket
- Every reader runs it until the row is fixed
- One write, many victims, no link needed

### DOM XSS

- The page's own JavaScript writes the payload
- innerHTML with location.hash is the classic
- The server never sees it in the response

### The fix

- Encode on output, for the context it lands in
- CSP blocks inline script it did not allow
- CSP is a backstop, not the fix

> **Note:** Encode every output. CSP catches what encoding misses.

## Explained

### Reflected

Reflected XSS rides in the request and comes back in the response. A link like ?q=\<script>alert(1)\</script> is enough if the page prints q without encoding. The server stored nothing: the payload lives in the crafted URL and the chat app that carried it.

### Stored

Stored XSS is saved first: a comment, a profile field, a support ticket. Every reader of that row runs the payload until the row is fixed, which is why one write can hit thousands of sessions and no link is needed.

### DOM

DOM XSS never reaches the server. The page's own JavaScript reads location.hash or a query parameter and writes it into innerHTML, so the response is clean and the browser still executes the payload. Server-side filters cannot see it.

### The fix

The fix is contextual output encoding: HTML entities in HTML text, attribute encoding in attributes, JSON encoding in script blocks, URL encoding in URLs. Then add a CSP that disallows inline script and allows only the origins you name. CSP is the backstop for the encoder you missed, not a substitute for it.

> **The honest caveat:** a CSP containing 'unsafe-inline' or a wildcard source gives you the header and none of the protection, and encoding the input instead of the output breaks data in ways users notice.

> **The lesson:** encode where the data lands, not where it came from.

## In one line

> **Encode the output, not the input.** CSP catches what a missed encoder lets through.

**Find the sink**

```bash
grep -rn 'innerHTML' src/
```
