# asm-query-builder

A Claude skill for writing, debugging, and tuning attack-surface-management detection
queries — the matchers, saved filters, and subscriptions used to fingerprint
internet-facing technology across an external asset inventory.

Built for defensive exposure management: finding the VPN portal, admin interface, exposed
database, or end-of-life server in your own estate before someone else does.

## What it does

Ask for a detection in plain language and get back a query that respects the platform's
constraints, with its criteria count, what a hit means, and the false positives it
suppresses.

```
### Fortinet FortiGate SSL-VPN
Final URL contains /remote/login
OR HTML contains /sslvpn/portal.html
OR Final HTML contains /sslvpn/portal.html
OR Server contains xxxxxxxx-xxxxx
OR Sets Cookies contains SVPNCOOKIE

Criteria: 5/15
Why it fires: the Server: xxxxxxxx-xxxxx header is a Fortinet quirk and an
unusually clean fingerprint.
```

## Contents

| File | Purpose |
|---|---|
| `SKILL.md` | Query-language constraints, signal-quality ranking, workflow, output format |
| `references/attributes.md` | Every scanner attribute, grouped by purpose, with operator guidance |
| `references/query-library.md` | ~35 vetted detections across VPN gateways, admin panels, dev tooling, container control planes, exposed data services, TLS hygiene, EOL software, and CVE triage |
| `references/troubleshooting.md` | Fixes for complexity errors, the criteria limit, and queries that return nothing or everything |

## Query-language rules it encodes

- Top-level operators cannot be mixed — all `AND` or all `OR`, with parentheses to nest
- Fewer than 15 matching criteria per matcher
- `is one of` collapses a value list into a single criterion, which is the main lever for
  staying under the limit
- Deep nesting triggers a complexity error even when the criteria count is legal; the fix
  is flattening, which sometimes changes the semantics

## Install

This is a skill, not a program — there is nothing to execute. It is a set of
instructions and reference material that Claude loads when a request matches the
skill's description. "Running" it means installing it, then asking for a detection in
plain language.

**Claude Code** — clone straight into your skills directory:

```bash
git clone https://github.com/DrewVravick/asm-query-builder.git \
  ~/.claude/skills/asm-query-builder
```

Restart Claude Code. Available immediately, no packaging step.

**Claude.ai / Claude Desktop** — download the `.skill` bundle from
[Releases](../../releases), then upload it under Settings → Capabilities → Skills.

To build the bundle yourself instead:

```bash
git clone https://github.com/DrewVravick/asm-query-builder.git
cd asm-query-builder
python package.py
```

That writes `asm-query-builder.skill`. Requires Python 3.8+ and no dependencies.

**Claude Project** — paste `SKILL.md` and the three files in `references/` into a
Project's knowledge base. Slightly worse than a real skill install, since everything
loads on every turn rather than on demand, but it works and needs no tooling.

## Usage

Once installed, ask in plain language:

- "Give me a matcher for exposed Ivanti Connect Secure"
- "This query throws a complexity error, fix it: `...`"
- "What attributes can I use to detect end-of-life web servers?"
- "Build me a subscription that alerts on new critical assets with a login form"

Output includes the query, its criteria count against the 15 limit, what a hit means,
and the false positives it suppresses.

## Caveats

Fingerprints drift. Vendors redesign login pages, rename cookies, and change header
values between releases, so a matcher that worked last quarter can go quiet without
failing loudly. Validate any new detection against one asset you know runs the product
before rolling it out, and record the date and basis alongside the matcher so it can be
audited later.

Some fingerprints in the library are derived from documented product behaviour rather than
from observed scan data. Those are flagged in `query-library.md`. Confirm against your own
inventory.

## Scope

This skill describes what products look like from the outside for the purpose of
inventorying and remediating exposure. It contains no exploitation tooling and is not
intended for use against infrastructure you do not own or have authorization to assess.

## License

MIT — see [LICENSE](LICENSE).
