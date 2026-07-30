# Troubleshooting

## "Query is too complex. Please use less filters or simplify the queries"

Triggered by nesting depth, not only by criteria count — a query can be under 15 criteria
and still fail. The fix is to flatten the tree into a single-level `OR` list.

This form fails:

```
(HTML contains intercom-app OR Final HTML contains intercom-app)
AND (HTML contains liveChat OR Final HTML contains liveChat OR HTML contains ZendeskChat
     OR Final HTML contains ZendeskChat OR HTML contains drift-widget
     OR Final HTML contains drift-widget OR HTML contains crisp-chat
     OR Final HTML contains crisp-chat OR HTML contains tawkto
     OR Final HTML contains tawkto OR HTML contains livechat-widget
     OR Final HTML contains livechat-widget
     OR (HTML contains chat-bubble AND HTML contains send-message))
```

Flattened to a single level, it evaluates:

```
HTML contains intercom-app OR
HTML contains liveChat OR
HTML contains ZendeskChat OR
HTML contains drift-widget OR
HTML contains crisp-chat OR
HTML contains tawkto OR
HTML contains livechat-widget OR
Final HTML contains intercom-app OR
Final HTML contains liveChat OR
Final HTML contains ZendeskChat OR
Final HTML contains drift-widget OR
Final HTML contains crisp-chat OR
Final HTML contains tawkto OR
Final HTML contains livechat-widget OR
(HTML contains chat-bubble AND HTML contains send-message)
```

The semantics changed — the original required Intercom *and* another widget; the flattened
version matches any single widget. That is usually the intent anyway, but say so explicitly
when flattening for a user rather than presenting it as an equivalent rewrite. If the
conjunction genuinely matters, build two matchers and intersect them by tag instead.

**Flattening checklist**

1. Remove one level of parentheses at a time and retest — the threshold is not documented,
   so find it empirically.
2. Collapse same-attribute value lists with `is one of`.
3. Move `AND` corroboration clauses (response code, ASN exclusions) out of the nested
   groups to the top level, if the top level is already `AND`.
4. If none of that works, split into two matchers and combine by tag.

## "You need to use fewer than 15 matching criteria when creating matchers"

Every `attribute operator value` triple counts, including inside parentheses. To reduce:

- **Collapse with `is one of`.** Four `Ports equals` clauses become one
  `Ports is one of 3389, 23, 53, 137`. This is the biggest single win and works for
  `Services`, `Operating Systems`, `Response Code`, `Country/Region`, and any other
  enumerable field.
- **Cut the weakest fingerprint clauses.** Version-specific HTML markup ages out fastest —
  drop it before dropping path or header artifacts.
- **Trim ASN exclusions** from four to two (`Cloudflare`, `Incapsula` cover most volume).
- **Drop redundant `Final HTML` pairs** where redirects are not in play, e.g. when the
  detection is already anchored on `Final URL`.
- **Split the matcher.** Two focused matchers beat one that barely fits, and they produce
  distinguishable tags for triage.

## Query returns nothing

In rough order of likelihood:

1. **Misspelled attribute.** `Banner` vs `Banners`, `Title` vs `Document Title`,
   `Header` vs `Response Header Name`. Check `references/attributes.md`.
2. **Attribute not populated for that asset class.** `CPE` and `CVE` are sparse on web
   assets; `Banners` is empty for HTTPS-only hosts. Test each clause alone to find the
   one that zeroes the result.
3. **`AND` over mutually exclusive evidence.** `HTML contains X AND Final HTML contains X`
   fails on assets that redirect. Use `OR` between the pair.
4. **Over-specific string.** Markup with exact whitespace, attribute order, or a version
   number rarely survives a product update. Shorten to the stable substring —
   `/global-protect/` rather than a full `<div>`.
5. **Exclusion too aggressive.** `ASN does not contain Cloudflare` also removes legitimately
   Cloudflare-hosted origins the organization owns.

## Query returns far too much

1. **Vendor name matched anywhere in HTML.** A footer credit, a script bundle, or a CDN
   reference all match `HTML contains <vendor>`. Anchor on `Final URL`, `Document Title`,
   or a header instead.
2. **No response-code filter.** Add `Response Code equals 200` so 404 pages and redirect
   stubs that still ship the vendor's JS bundle drop out.
3. **Broad category attribute used as a finding.** `Containers exists` or `Services is one
   of ssh, …` are inventory queries. Pair with `Login exists` or a port restriction to make
   them actionable.
4. **`Ports` instead of `Verified Ports`.** Unverified ports include speculative results.

## Mixed top-level operators

The error is structural: every top-level clause must share one operator. Wrap the minority
logic in parentheses.

Broken:

```
Document Title contains Grafana OR HTML contains grafana-app AND Response Code equals 200
```

Fixed:

```
(Document Title contains Grafana OR HTML contains grafana-app)
AND Response Code equals 200
```

The general shape that works for most detections: a parenthesised `OR` group of
fingerprints, joined by `AND` to corroboration and exclusion clauses.

## Validating before rollout

Before saving a matcher or subscription:

1. Run it as an ad-hoc filter and eyeball 5-10 results — confirm they are the product, not
   a page that mentions it.
2. Run the inverse (`does not contain` on the primary artifact) against one asset known to
   run the product, to confirm the fingerprint is actually present in the scan data rather
   than assumed.
3. For subscriptions, add `Added to Inventory less than 7` so the alert fires on change
   rather than on the existing estate.
4. Record the date and the fingerprint's basis alongside the matcher. Vendor login pages
   change; a matcher with no provenance note becomes impossible to audit when it goes quiet.
