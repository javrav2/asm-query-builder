---
name: asm-query-builder
description: Write, debug, and optimize attack-surface-management (ASM) detection queries for Tenable ASM / Attack Surface Management inventories — matchers and saved filters that fingerprint internet-facing technology (VPN portals, admin interfaces, exposed databases, EOL software, weak TLS, open directories) so exposures can be triaged. Use this skill whenever the user asks for an ASM query, matcher, filter, subscription, or "detection" for a product or CVE; pastes an ASM query to fix; mentions errors like "Query is too complex" or the 15-criteria limit; asks how to fingerprint, hunt for, or inventory a technology across their external attack surface; or asks which scanner attributes/data points are available. Also use it when the user is doing external exposure triage and a query would answer the question, even if they never say the word "query".
---

# ASM Query Builder

Build detection logic for an attack surface management inventory. Queries are used as
**matchers** (tag/classify assets), **saved filters** (ad-hoc hunting), and
**subscriptions** (alert when a new asset matches).

The goal is always the same: turn "is this risky technology exposed to the internet
anywhere in our estate?" into a query that fires on the real thing and stays quiet
otherwise.

## Hard constraints of the query language

These come from the platform, not preference. Violating them produces an error or a
silently wrong result.

1. **Top-level operators cannot be mixed.** Every clause at the top level must be joined
   by `AND`, or every clause must be joined by `OR`. To mix logic, wrap the minority
   condition in parentheses and nest it.
2. **Fewer than 15 matching criteria per matcher.** Each `attribute operator value`
   triple counts as one, including ones inside parentheses. Aim for 8-12 to leave
   headroom.
3. **"Query is too complex. Please use less filters or simplify the queries"** appears
   when nesting is deep even if the criteria count looks legal. The fix is to *flatten*:
   convert `(A OR B) AND (C OR D OR E …)` into a single-level `OR` list, or split into
   two separate matchers. See `references/troubleshooting.md`.
4. **`is one of` collapses many `OR`s into one criterion.** `Ports is one of 3389, 23, 53, 137`
   is one criterion; four separate `Ports equals` clauses are four. Always prefer
   `is one of` for value lists on the same attribute — this is the single most effective
   way to stay under the limit.

Correct nesting:

```
(HTML contains kibanaWelcomeView OR Final HTML contains kibanaWelcomeView)
AND Response Code equals 200
AND ASN does not contain Cloudflare
```

Illegal, because the top level mixes operators:

```
HTML contains kibanaWelcomeView OR Response Code equals 200 AND ASN does not contain Cloudflare
```

## Workflow

1. **Establish what is being fingerprinted and why.** A product name is not enough — a
   query for "Citrix" differs depending on whether the concern is the login portal, a
   specific CVE, or every asset touching NetScaler. Ask if the intent is genuinely
   ambiguous; otherwise pick the highest-signal interpretation and say which one you chose.
2. **Choose attributes from what the scanner actually collects.** Read
   `references/attributes.md` before writing anything. Inventing an attribute name is the
   most common way these queries fail — there is no `Banner` (it is `Banners`), no
   `Title` (it is `Document Title`), no `Header` (it is `Response Header Name` /
   `Response Header Value`).
3. **Layer evidence, strongest first.** See "Signal quality" below.
4. **Add noise suppression.** Cloud/WAF ASNs, CDN-fronted responses, and parked pages
   generate most false positives. Reuse the exclusions in `references/query-library.md`.
5. **Count criteria out loud** in the response, and state the count. This catches limit
   violations before the user pastes the query into the console.
6. **Explain what a hit means and what to do about it.** A query that returns 400 assets
   with no triage guidance is not useful. Note the likely CVEs or hardening action.

## Signal quality

Rank evidence by how hard it is to fake or coincidentally match. Build queries from the
strongest tier available, then add a second tier as corroboration.

| Tier | Examples | Notes |
|---|---|---|
| Strongest | `Final URL contains /tmui/login.jsp`, `Response Header Name contains nsc_cert`, `CPE`, `CVE` | Path and header artifacts are emitted by the product itself |
| Strong | `Document Title`, unique DOM ids/classes in `HTML` / `Final HTML`, `JARM Hash`, `SSL/TLS Issuer Common Name` | Distinctive but themable/removable |
| Moderate | `Server`, `Web Servers`, `Sets Cookies`, `Verified Ports`, `Services` | Often generic or spoofed |
| Weak alone | vendor name anywhere in `HTML`, `Ports` with no service confirmation | Use only as corroboration |

Two habits that matter:

- **Pair `HTML` with `Final HTML`.** `HTML` is the first response; `Final HTML` is after
  redirects. Login portals frequently only appear in one. Wrap the pair in parentheses and
  `OR` them so the surrounding logic stays `AND`.
- **Prefer `Verified Ports` over `Ports`** when the question is "is this actually
  listening", and prefer `Services` over `Ports` when the question is "what protocol is
  this" — a database on a nonstandard port is invisible to a port query.

## Response format

For each query, output:

```
### <what it detects>
<the query, on its own lines, one clause per line>

Criteria: <n>/15
Why it fires: <the artifact being matched>
Triage: <what a hit likely means, CVEs if relevant>
False positives: <known noise and how it is suppressed>
```

When asked for several detections, keep them as separate matchers rather than one giant
query. Separate matchers stay under the limit, tag assets distinctly, and can be tuned
independently. Bundling ten technologies into one `OR` chain produces the complexity
error and an untriageable tag.

## Reference files

- `references/attributes.md` — every attribute the scanning engine collects, grouped by
  category, with the operators that make sense for each. Read this before writing queries.
- `references/query-library.md` — vetted detections for edge VPNs and gateways, admin
  interfaces, exposed data services, dev/CI tooling, TLS hygiene, and exposure hunting.
  Start from a library entry and adapt rather than writing from scratch.
- `references/troubleshooting.md` — fixes for the complexity error, the criteria limit,
  mixed top-level operators, and queries that return nothing or everything.

## Judgment notes

This skill supports defensive work: inventorying an organization's own external attack
surface. Detections describe *what a product looks like from outside* — they do not
include exploitation steps. If a request shifts toward exploiting a third party's
infrastructure rather than finding and fixing exposure in the user's own, say so plainly
and stay on the inventory side.

Be honest about coverage. Fingerprints drift as vendors change login pages, and a query
that worked last quarter can go quiet. When confidence in an artifact is low, say so and
suggest validating against one known-good asset before rolling the matcher out.
