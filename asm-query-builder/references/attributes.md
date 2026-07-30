# Scanner attributes

Every field the scanning engine collects, grouped by what it is useful for. Attribute
names are case-insensitive in practice but match this spelling when writing queries — a
misspelled attribute is the most common cause of a query that returns nothing.

## Contents

- [Operators](#operators)
- [Highest-value attributes](#highest-value-attributes)
- [Security / TLS](#security--tls)
- [HTTP response](#http-response)
- [HTML](#html)
- [Networking](#networking)
- [Services and ports](#services-and-ports)
- [Vulnerability data](#vulnerability-data)
- [Technology stack](#technology-stack)
- [Geolocation](#geolocation)
- [WHOIS](#whois)
- [Inventory metadata](#inventory-metadata)

## Operators

| Operator | Use with | Notes |
|---|---|---|
| `contains` / `does not contain` | text fields (`HTML`, `Final URL`, `Banners`, `ASN`) | substring, case-insensitive; the workhorse |
| `equals` / `does not equal` | exact-value fields (`Response Code`, `Ports`, `Domain`) | exact match |
| `is one of` / `is not one of` | any field with a value list | **collapses many ORs into one criterion — use this** |
| `starts with` / `ends with` | paths, hostnames, `Host` | good for subdomain patterns |
| `exists` / `does not exist` | optional fields (`CVE`, `Login`, `SSL/TLS error`) | presence check, cheap |
| `greater than` / `less than` | numeric (`CVSSv3 Scores`, `SSL/TLS Key Length`, `Content Length`) | |

## Highest-value attributes

If short on criteria budget, these carry the most signal per clause:

`Final URL`, `Document Title`, `Response Header Name`, `Response Header Value`, `HTML`,
`Final HTML`, `CPE`, `CVE`, `Verified Ports`, `Services`, `JARM Hash`, `Server`.

## Security / TLS

```
SSL/TLS Expiration              SSL/TLS Fingerprint
SSL/TLS EV Certificate          SSL/TLS Issuer Country / Region
SSL/TLS Issuer Organization     SSL/TLS Issuer Common Name
SSL/TLS Valid From              SSL/TLS Subject Alt Name
SSL/TLS Cypher Suites           SSL/TLS Key Length
SSL/TLS Protocol                SSL/TLS error
SSL/TLS Serial Number           JARM Hash
Captchas                        Cookie Compliance
Secret Keys                     Login
Bug Bounty URL
```

Notes: `SSL/TLS Issuer Common Name` reveals self-signed and appliance-generated certs
(appliance defaults are a strong fingerprint). `JARM Hash` fingerprints the TLS stack
itself and survives page rewrites. `Secret Keys` flags credentials found in responses —
worth a standing subscription on its own. `Login` marks assets presenting an auth form.

## HTTP response

```
Content Type            Content Language        Vary
Response Header Name    Response Header Value
Response Security Header Name   Response Security Header Value
Sets Cookies            Content Length          Canonical URL
Response Code           Final Response Code
```

Notes: header *names* and *values* are separate attributes — checking for a vendor header
means `Response Header Name contains x-vendor`, not a value search. `Sets Cookies` catches
appliance session cookie names (`NSC_`, `BIGipServer`, `JSESSIONIDSSO`). The security-header
attributes support the inverse question: which assets are *missing* HSTS or CSP.

## HTML

```
Document Title    HTML    Final HTML
```

`HTML` is the initial response body; `Final HTML` is post-redirect. Pair them.
`Document Title` maps to `<title>` and is often the cleanest single fingerprint.

## Networking

```
Host              Domain            Is Subdomain      Nameservers
Record Type       Record Value      Redirect Chain
IP Address        IP Range          ASN               ASN Number
Final URL         Hosting Provider  Cloud Hosted
Network Devices   Network Storage   Remote Access     Containers
Mixed Content     CDN               Load Balancer     Reverse Proxy
SaaS              PaaS              IaaS
```

Notes: `ASN` is the primary noise filter — excluding Cloudflare/Incapsula/Akamai removes
edge-terminated responses that describe the CDN rather than the origin. `Network Devices`,
`Remote Access`, `Network Storage`, and `Containers` are pre-computed category
classifications and are often a faster path than hand-built fingerprints.

## Services and ports

```
Ports    Verified Ports    Services    Banners    Server    Web Servers
Email Service    RBL
```

Notes: `Verified Ports` means the listener was confirmed — use it to cut speculative
findings. `Services` is protocol-level and catches nonstandard ports. `Banners` carries
version strings for non-HTTP services and is the best source for EOL detection.

## Vulnerability data

```
CPE    CVE    CVSSv3 Scores    CVSSv3 Vectors    Severity    DAST RANKING
```

`CPE` is the structured product/version identifier — when a CPE exists for the target
product it beats any HTML fingerprint. `CVE` supports `exists` for "anything known-vulnerable".

## Technology stack

Pre-classified detections. Querying these is cheaper and more stable than pattern-matching
HTML, so check whether a category already covers the target before writing a fingerprint.

**Web / infrastructure:** `Web Servers`, `Web Server Extensions`, `Operating Systems`,
`Reverse Proxy`, `Load Balancer`, `CDN`, `Cache Tools`, `Hosting`, `Hosting Panels`,
`Hosting Provider`, `Static Site Generator`, `Performance`

**Application platforms:** `CMS`, `Ecommerce`, `Web Frameworks`, `Programming Languages`,
`Mobile Frameworks`, `JavaScript Frameworks`, `JavaScript Libraries`, `JavaScript Graphics`,
`Landing Page Builders`, `Rich Text Editors`, `Font Scripts`

**WordPress:** `WordPress Core Version`, `WordPress Plugins`, `WordPress Scanned Plugins`,
`WordPress Themes`, `WordPress Vulnerability IDs`

**Data:** `Databases`, `Database Managers`, `Analytics`, `Customer Data Platform`,
`Segmentation`, `Document Management Systems`

**Dev / ops:** `Dev Tools`, `Build CI Systems`, `Issue Trackers`, `Documentation Tools`,
`Editors`, `Wikis`, `Control Systems`, `Containers`, `Feature Management`, `Tag Managers`

**Media / devices:** `Media Servers`, `Webcams`, `Printers`, `Video Players`,
`Photo Galleries`, `Livestreaming`, `Augmented Reality`

**Business apps:** `Web Mail`, `Live Chat`, `Comment Systems`, `Social Logins`,
`Social Profiles`, `Message Boards`, `Blogs`, `Search Engines`, `LMS`, `CRM`, `SEO`,
`Marketing Automation`, `Advertising Networks`, `Affiliate Programs`, `Accounting`,
`Payment Processors`, `Paywalls`, `Shopify Apps`, `Appointment Scheduling`,
`Reservations & Delivery`, `Ticket Booking`, `Shipping Carriers`, `Returns`,
`Loyalty & Rewards`, `Referral Marketing`, `Reviews`, `Recruitment & Staffing`,
`Buy Now Pay Later`, `Cart Abandonment`, `Cross Border ECommerce`, `Content Curation`,
`Digital Asset Management`, `Browser Fingerprinting`, `User Onboarding`, `Translation`,
`Accessibility`, `Widgets`, `Feed Readers`, `Maps`, `Geolocation`, `RUM`, `Cryptominer`,
`Miscellaneous`

`Cryptominer` deserves a standing subscription — a hit usually means compromise.

## Geolocation

```
Continent    Country/Region    City    Latitude    Longitude
Time Zone    Postal    In EU    Subdivisions    Registered Country/Region
```

Useful for data-residency and sanctions questions, and for spotting assets hosted in
regions the organization does not operate in.

## WHOIS

```
Registrar Name    Domain Name Expiration    WHOIS Status
Registrant Name / Organization / Email / Telephone / Fax
Registrant Street 1-4 / City / State / Postal Code / Country/Region
Administrative Contact Name / Email / Organization / Telephone
Technical Contact Name / Email / Technical Organization
Billing Contact Email    Contact Email    Zone Contact Email
```

`Domain Name Expiration` catches domains about to lapse — a takeover risk.
Contact fields help attribute shadow IT to the team that registered it.

## Inventory metadata

```
Asset ID    Severity    Added to Inventory    Last Metadata Change    Tags
```

`Added to Inventory` scopes a query to new assets, which is what makes a subscription
alert on *change* rather than re-firing on the existing estate.
