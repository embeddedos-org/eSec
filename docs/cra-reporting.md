# CRA vulnerability reporting — triggers, channel, and templates

**Status:** operational runbook (2026-10-13), not legal counsel.
**Companion:** [`cra-incident-reporting-runbook.md`](cra-incident-reporting-runbook.md)
covers the incident workflow step by step; this page covers what
*triggers* a report, *who* files it, and the standing artifacts
(`security.txt`, SBOM, support period) that make filing possible
inside the clock. The org CVD policy in [`../SECURITY.md`](../SECURITY.md)
governs disclosure to reporters and the public.

## The clock

The CRA's reporting obligations have applied since **2026-09-11**:

| Deadline | What is filed |
|---|---|
| 24 hours | Early warning: an actively exploited vulnerability (or severe incident) has been confirmed, with initial details. |
| 72 hours | Fuller notification: impact, affected products and versions, mitigation status. |
| 14 days after a fix is available | Final report: root cause, complete impact, corrective measures. |

Full CRA obligations (beyond reporting) apply from **2027-12-11**.
Clocks run from triage confirmation, as defined in the companion
runbook — read that page for the workflow; this page assumes it.

## The trigger: what counts as "actively exploited"

The org's working trigger is a **CISA KEV listing**: a vulnerability
in the Known Exploited Vulnerabilities catalog is, by definition,
known to be actively exploited. This is the same signal the org
already tracks operationally — `embeddedos-stack`'s KEV gate
(`docs/kev-gate.md` in that repo) dispositions every KEV entry
against the stack, dated, so the trigger decision has a written
record before any incident starts.

In practice:

- A KEV entry matching a component in an org product starts the
  clock-assessment: triage confirms whether the shipped product is
  actually affected, and the runbook's classification applies.
- Credible exploitation evidence from any other source (researcher
  report, logs, honeypot) triggers the same assessment — KEV is the
  standing trigger, not the only one.
- A vulnerability with no exploitation evidence follows the normal
  CVD fix flow; it is recorded, but no CRA notification is due.

## The channel, and who files

- **Channel:** the ENISA single reporting platform — one submission
  reaches ENISA and the relevant national CSIRTs; there is no
  separate per-country filing for the early warning.
- **Who files:** the maintainer holding the **product security
  lead** role for the affected product (with the named deputy from
  the companion runbook's readiness list as fallback). Roles, not
  personal names, are recorded here — the current role-holders live
  in the private advisory template.
- The filer files even when fields are "unknown, under assessment";
  a late complete report is a missed deadline, an early incomplete
  one is the process working.

## Standing artifact: `security.txt` (RFC 9116)

Every org product ships a `security.txt` so a reporter can find the
intake before an incident exists. Template (this repo's own live
copy is [`../.well-known/security.txt`](../.well-known/security.txt)):

```text
Contact: https://github.com/embeddedos-org/<repo>/security/advisories/new
Expires: <one year from issue, ISO 8601 UTC>
Preferred-Languages: en
Policy: https://github.com/embeddedos-org/<repo>/blob/master/SECURITY.md
```

Expiry discipline is the operational point: an expired `Expires:`
field silently breaks the reporting path, so the date is reviewed
whenever the file is touched and at least yearly. Fields follow
RFC 9116; no field a product cannot honour may be listed.

## Supporting regime (design inputs)

Two CRA duties shape engineering before any incident:

- **SBOM.** Products maintain a software bill of materials
  (CycloneDX or SPDX). The SBOM is what turns "is the KEV-listed
  component in our product?" from an archaeology project into a
  lookup that fits inside the 24-hour clock.
- **Update support.** Products are designed for a support period of
  at least **five years**: update infrastructure, signing keys, and
  build reproducibility must be provisioned for that horizon, not
  for the launch quarter.

Both are design inputs to new products, reviewed like any other
requirement — not paperwork reconstructed after an incident.

## What this page is not

Legal advice. The CRA text and ENISA guidance are authoritative;
when they change, this page and the companion runbook follow.
