# Query library

Vetted detections to adapt. Each entry lists its criteria count so the budget stays
visible when clauses are added. Where a fingerprint is version- or theme-sensitive, that
is noted — validate against one known asset before rolling out a matcher.

## Contents

- [Reusable noise suppression](#reusable-noise-suppression)
- [Edge VPNs and remote access gateways](#edge-vpns-and-remote-access-gateways)
- [Management and admin interfaces](#management-and-admin-interfaces)
- [Dev, CI, and observability tooling](#dev-ci-and-observability-tooling)
- [Container and orchestration exposure](#container-and-orchestration-exposure)
- [Exposed data services](#exposed-data-services)
- [Legacy and high-risk protocols](#legacy-and-high-risk-protocols)
- [TLS and certificate hygiene](#tls-and-certificate-hygiene)
- [Content and secret exposure](#content-and-secret-exposure)
- [End-of-life software](#end-of-life-software)
- [CVE-driven triage](#cve-driven-triage)

## Reusable noise suppression

Append to port, service, and banner queries. Edge-terminated responses describe the CDN,
not the origin, and produce most of the false positives in port-based detections.

```
AND ASN does not contain Cloudflare
AND ASN does not contain Incapsula
AND ASN does not contain Akamai
AND ASN does not contain Fastly
```

Four criteria. If the budget is tight, `Cloudflare` and `Incapsula` alone remove the bulk.

## Edge VPNs and remote access gateways

The highest-priority category: internet-facing by design, historically the most exploited
initial-access vector, and frequently unpatched because patching means a maintenance window.

### Citrix NetScaler / Gateway — 3 criteria

```
Response Header Name contains nsc_cert
OR Final URL contains logon/logonpoint/
OR Response Header Value contains netscaler
```

Triage: check for CitrixBleed-class session-token and pre-auth RCE exposure. Confirm build
number in the admin console — the login page rarely reveals it.

### Palo Alto GlobalProtect portal — 6 criteria

```
Document Title contains GlobalProtect Portal
OR Final URL contains /global-protect/login.esp
OR HTML contains /global-protect/
OR Final HTML contains /global-protect/
OR HTML contains <div id="heading">GlobalProtect Portal</div>
OR Final HTML contains <div id="heading">GlobalProtect Portal</div>
```

The `/global-protect/` substring clauses are the durable ones; the `<div id="heading">`
markup changes between PAN-OS versions. Drop the markup clauses first if criteria are needed.

### Fortinet FortiGate SSL-VPN — 5 criteria

```
Final URL contains /remote/login
OR HTML contains /sslvpn/portal.html
OR Final HTML contains /sslvpn/portal.html
OR Server contains xxxxxxxx-xxxxx
OR Sets Cookies contains SVPNCOOKIE
```

The `Server: xxxxxxxx-xxxxx` header is a Fortinet quirk and an unusually clean fingerprint.

### Ivanti Connect Secure / Pulse Secure — 4 criteria

```
Final URL contains /dana-na/auth
OR HTML contains /dana-na/
OR Final HTML contains /dana-na/
OR Sets Cookies contains DSID
```

Triage: this product family has had repeated pre-auth chains. Treat any hit as urgent
patch-verification work.

### Cisco ASA / AnyConnect WebVPN — 4 criteria

```
Final URL contains /+CSCOE+/logon.html
OR HTML contains /+CSCOE+/
OR Final HTML contains /+CSCOE+/
OR Sets Cookies contains webvpn
```

### SonicWall SSL-VPN — 4 criteria

```
Final URL contains /cgi-bin/welcome
OR Document Title contains SonicWall
OR HTML contains sonicwall
OR Sets Cookies contains swap
```

### Any remote-access surface, category-based — 3 criteria

```
Remote Access exists
AND Login exists
AND ASN does not contain Cloudflare
```

Cheap catch-all for coverage gaps. Run it after the specific matchers and review whatever
it finds that they missed — that delta is where unknown appliances live.

## Management and admin interfaces

Administrative panels reachable from the internet are almost always a misconfiguration
rather than a design decision, which makes this category high-yield.

### F5 BIG-IP TMUI — 3 criteria

```
Final URL contains /tmui/login.jsp
OR HTML contains /tmui/login.jsp
OR Sets Cookies contains BIGipServer
```

Triage: TMUI should never be internet-facing. A hit is a finding regardless of patch level.
The `BIGipServer` cookie alone only proves BIG-IP load balancing, not an exposed TMUI —
keep it as corroboration, not a standalone matcher.

### VMware vCenter / vSphere — 5 criteria

```
Document Title contains vSphere
OR Final URL contains /websso/SAML2/SSO
OR HTML contains /ui/login
OR HTML contains VMware vCenter
OR Final HTML contains VMware vCenter
```

### Microsoft Exchange OWA / ECP — 4 criteria

```
Final URL contains /owa/auth/logon.aspx
OR Final URL contains /ecp/
OR Response Header Name contains x-owa-version
OR HTML contains /owa/auth/
```

Triage: an exposed `/ecp/` is materially worse than `/owa/` — ECP has been the entry point
for several exploit chains. Consider splitting these into two matchers so the tags differ.

### Out-of-band management (iDRAC / iLO / IPMI) — 6 criteria

```
Document Title contains iDRAC
OR Document Title contains Integrated Lights-Out
OR HTML contains hpilo
OR HTML contains /restgui/
OR SSL/TLS Issuer Common Name contains iDRAC
OR SSL/TLS Issuer Common Name contains Default Issuer
```

Triage: BMCs on the internet are a critical finding — they sit below the OS and often run
firmware years out of date. The self-signed issuer clauses catch appliances that have had
their web UI rebranded.

### Database and hosting admin panels — 8 criteria

```
Database Managers exists
OR Hosting Panels exists
OR Document Title contains phpMyAdmin
OR HTML contains pma_username
OR Document Title contains Webmin
OR HTML contains /adminer.php
OR Document Title contains cPanel
OR Document Title contains Plesk
```

## Dev, CI, and observability tooling

Internal tooling that drifted onto the internet. Frequently unauthenticated, and CI systems
hold credentials to everything else.

### Jenkins — 4 criteria

```
Response Header Name contains x-jenkins
OR Document Title contains [Jenkins]
OR HTML contains /static/ AND HTML contains Jenkins ver.
OR Final HTML contains Jenkins ver.
```

Note the third clause mixes `AND` inside an `OR` list — wrap it in parentheses:
`(HTML contains /static/ AND HTML contains Jenkins ver.)`. Without parentheses the query
violates the top-level operator rule.

### GitLab / Gitea / self-hosted git — 5 criteria

```
Response Header Name contains x-gitlab-feature-category
OR Document Title contains GitLab
OR HTML contains gon.gitlab_url
OR Document Title contains Gitea
OR HTML contains /assets/js/gitea
```

### Grafana — 3 criteria

```
Document Title contains Grafana
OR HTML contains grafana-app
OR Final HTML contains grafana_session
```

### Kibana — 3 criteria

```
(HTML contains kibanaWelcomeView OR Final HTML contains kibanaWelcomeView)
AND Response Code equals 200
```

The `Response Code equals 200` clause matters: without it, error pages and redirect stubs
that mention Kibana in a script bundle will match.

### Elasticsearch REST API — 4 criteria

```
(HTML contains You Know, for Search OR Final HTML contains You Know, for Search)
AND Verified Ports is one of 9200, 9243
AND ASN does not contain Cloudflare
```

Triage: an Elasticsearch node answering on 9200 without auth is a data-breach-in-waiting.
Check for a `cluster_name` in the response body to confirm.

### Issue trackers and wikis — 5 criteria

```
Response Header Name contains x-confluence-request-time
OR HTML contains ajs-version-number
OR Document Title contains Jira
OR Issue Trackers exists
OR Wikis exists
```

## Container and orchestration exposure

### Kubernetes Dashboard — 2 criteria

```
HTML contains Kubernetes Dashboard</title>
OR Final HTML contains Kubernetes Dashboard</title>
```

### Kubernetes and container control planes by port — 5 criteria

```
Verified Ports is one of 2375, 2376, 6443, 10250, 2379
AND ASN does not contain Cloudflare
AND ASN does not contain Incapsula
AND ASN does not contain Akamai
AND ASN does not contain Fastly
```

Triage by port: 2375 is unauthenticated Docker (immediate container escape to host), 2376
is Docker over TLS, 6443 is the Kubernetes API server, 10250 is kubelet (command execution
if anonymous auth is on), 2379 is etcd (every cluster secret in plaintext). Splitting 2375
and 10250 into their own matcher is worth the extra tag — they are the ones that warrant
paging someone.

### Container platforms, category-based — 3 criteria

```
Containers exists
AND Login exists
AND ASN does not contain Cloudflare
```

## Exposed data services

### Databases listening to the internet — 3 criteria

```
Services is one of mysql, postgresql, mongodb, redis, elasticsearch, memcached, mssql, cassandra, couchdb
AND ASN does not contain Incapsula
AND ASN does not contain Cloudflare
```

Prefer `Services` over `Ports` here — a MongoDB on 27018 or a Redis on 6380 is invisible
to a port list but obvious to protocol detection.

### Database ports as a fallback — 5 criteria

```
Verified Ports is one of 3306, 5432, 27017, 6379, 11211, 1433, 5984, 9042, 1521
AND ASN does not contain Cloudflare
AND ASN does not contain Incapsula
AND ASN does not contain Akamai
AND ASN does not contain Fastly
```

Use when `Services` detection is incomplete. `Verified Ports` rather than `Ports` keeps
speculative results out. Memcached on 11211 doubles as a UDP amplification risk.

### Network storage — 3 criteria

```
Network Storage exists
AND ASN does not contain Cloudflare
AND ASN does not contain Incapsula
```

## Legacy and high-risk protocols

### RDP exposure — 3 criteria

```
Ports equals 3389
AND ASN does not contain incapsula
AND ASN does not contain Cloudflare
```

### Multiple legacy protocols by port — 3 criteria

```
Ports is one of 3389, 23, 53, 137, 21, 445, 5900, 161, 111, 512
AND ASN does not contain incapsula
AND ASN does not contain Cloudflare
```

One criterion for the whole port list. Triage priority: 445 (SMB) and 3389 (RDP) first as
ransomware entry points, then 23 (telnet) and 5900 (VNC) as cleartext admin access, then
53/161/111/1900 as amplification and information-disclosure risks.

### Legacy protocols by service — 3 criteria

```
Services is one of ssh, telnet, dns, netbios, rdp, docker, ftp, smb, vnc, snmp, rsync
AND asn does not contain incapsula
AND asn does not contain Cloudflare
```

Catches the same protocols on nonstandard ports. Note that `ssh` in this list will match a
large share of the estate — either accept it as an inventory query rather than a finding,
or drop `ssh` to keep the result actionable.

## TLS and certificate hygiene

### Deprecated TLS versions — 2 criteria

```
SSL/TLS Protocol is one of SSLv2, SSLv3, TLSv1.0, TLSv1.1
AND ASN does not contain Cloudflare
```

### Weak keys — 2 criteria

```
SSL/TLS Key Length less than 2048
AND SSL/TLS Key Length exists
```

The `exists` clause suppresses assets with no TLS at all, which otherwise register as
below-threshold.

### Broken or self-signed certificates — 5 criteria

```
SSL/TLS error exists
OR SSL/TLS Issuer Common Name contains localhost
OR SSL/TLS Issuer Common Name contains self-signed
OR SSL/TLS Issuer Common Name contains Default
OR SSL/TLS Issuer Common Name contains Internal
```

Triage: a self-signed cert on an internet-facing host usually means the asset was never
meant to be exposed. Follow the finding to *why* it is reachable, not just to the cert.

### Certificates and domains about to lapse — 2 criteria

```
SSL/TLS Expiration less than 30
OR Domain Name Expiration less than 30
```

Operational rather than adversarial, but an expired domain is a takeover route.

## Content and secret exposure

### Open directory listing — 2 criteria

```
HTML contains <html><head><title>Index of /</title></head>
AND HTML contains " - /</title></head><body><H1>"
```

The two clauses cover Apache-style and IIS-style listings respectively. If this returns
nothing, run them as separate matchers — combining with `AND` requires both patterns in the
same response, which some servers will not produce.

### Exposed secrets — 1 criterion

```
Secret Keys exists
```

Worth a standing subscription. Every hit needs credential rotation, not just a config fix —
assume anything published was collected.

### Cryptominer — 1 criterion

```
Cryptominer exists
```

A hit generally indicates compromise or a supply-chain injection in a third-party script.
Route to incident response rather than to patching.

### Mixed content and missing security headers — 3 criteria

```
Mixed Content exists
AND Login exists
AND Response Security Header Name does not contain strict-transport-security
```

Prioritises the combination that matters: a login form served with mixed content and no HSTS.

## End-of-life software

Version fingerprints go stale, so anchor on `CPE` and `Banners` where possible and treat
`Server` string matching as a supplement.

### EOL operating systems — 2 criteria

```
Operating Systems is one of Windows Server 2008, Windows Server 2008 R2, Windows Server 2012, Windows Server 2012 R2, CentOS 6, CentOS 7, Ubuntu 14.04, Ubuntu 16.04, Ubuntu 18.04
AND ASN does not contain Cloudflare
```

### EOL web servers — 5 criteria

```
Server contains Apache/2.2
OR Server contains Apache/2.0
OR Server contains nginx/1.1
OR Server contains Microsoft-IIS/6.0
OR Server contains Microsoft-IIS/7.
```

Note `nginx/1.1` also matches `nginx/1.14` through `1.19`, several of which are current
enough to be arguable. Tighten to specific versions if the result set is noisy.

### EOL PHP — 3 criteria

```
Response Header Name contains x-powered-by
AND Response Header Value contains PHP/5
AND ASN does not contain Cloudflare
```

Swap `PHP/5` for `PHP/7.` to catch the 7.x line, which is also past end of life.

### Vulnerable WordPress — 3 criteria

```
WordPress Vulnerability IDs exists
OR WordPress Core Version is one of 4.9, 5.0, 5.1, 5.2, 5.3, 5.4
OR WordPress Scanned Plugins exists
```

The third clause is broad — use it for inventory, not alerting. `WordPress Vulnerability IDs`
alone is the actionable matcher.

## CVE-driven triage

### Critical CVEs on authenticated surfaces — 4 criteria

```
CVE exists
AND CVSSv3 Scores greater than 9.0
AND Login exists
AND ASN does not contain Cloudflare
```

The `Login exists` clause is what makes this a priority queue rather than a report: a
critical CVE on an asset presenting a login form is where credential attacks and pre-auth
chains meet.

### Product-specific CVE hunting — 2 criteria

```
CPE contains cpe:/a:citrix:netscaler
AND CVE exists
```

Substitute the vendor/product string for the target. `CPE` matching is version-aware and
survives login-page redesigns, so prefer it whenever the scanner populates it — check
coverage first, since `CPE` is absent on many web assets.

### New critical assets only — 3 criteria

```
Added to Inventory less than 7
AND Severity is one of Critical, High
AND Login exists
```

The pattern for a subscription that alerts on *change*. Without the `Added to Inventory`
clause, a subscription re-fires on the existing estate and gets muted.
