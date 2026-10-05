# CRA incident-reporting runbook (EU Cyber Resilience Act)

**Status:** Maintainer runbook. **Date:** 2026-10-05
**Companion docs:** `docs/cvd-intake.md` (reporter-facing intake),
`SECURITY.md` (org CVD policy).

> **Urgency:** the CRA's vulnerability-reporting obligations have applied
> since **11 September 2026**. Fines reach €15M or 2.5% of worldwide
> turnover. This runbook maps those obligations onto the org's existing
> coordinated vulnerability disclosure (CVD) process.

## 1. The three CRA deadlines

All clocks start when the org **becomes aware** of the incident — i.e.
when a private security advisory (or credible report) lands in eSec and
triage confirms it is real. "Becoming aware" is the triage-confirmation
timestamp, not the report-arrival timestamp; record both.

| Deadline | What | To whom |
|---|---|---|
| **24 hours** | Early notification: the fact of an actively exploited vulnerability or a severe incident, with initial details | ENISA via the single reporting platform, **and** the CSIRT of the Member State(s) where affected products are on the market |
| **72 hours** | Severe-incident notification: fuller details — impact, affected products/versions, mitigation status | Same channels |
| **14 days** | Final report: root cause, complete impact assessment, corrective measures taken | Same channels |

A **severe incident** = one that affects the availability, authenticity,
integrity, or confidentiality of data/services, or that has cross-border
impact. When in doubt, treat it as severe — over-reporting within the
deadlines is safe; missing a deadline is not.

## 2. Severity classification (triage → CRA track)

Triage in the private advisory first, using the existing
`docs/cvd-intake.md` fields, then classify:

- **Actively exploited** (evidence of exploitation in the wild, not just a
  PoC) → the 24h clock applies. Confirm exploitation evidence before
  filing, but do not wait for perfect certainty — file the early
  notification and update it.
- **Severe incident** (per the definition above) → 72h notification + 14d
  final report.
- **Non-severe vulnerability** (no active exploitation, no severe
  impact) → no CRA notification duty, but the normal CVD fix flow still
  applies, and the vulnerability goes into the org's records for the
  technical documentation file.

Record the classification decision and its rationale in the advisory's
triage notes — the market-surveillance authority may ask why a track was
chosen.

## 3. What the disclosure must contain

Map the ENISA/CSIRT fields onto the advisory sections:

| CRA field | Source in our process |
|---|---|
| Affected product(s) and versions | Intake: "Affected component" (repo, version/commit, board/target) |
| Nature of the vulnerability / incident | Intake: "Description" + "Reproduction" |
| Severity and impact | Intake: "Impact" (attacker capability, prerequisites, severity estimate) |
| Whether exploitation is observed | Triage: exploitation evidence (logs, reports, honeypot hits) |
| Mitigation / corrective measures | Triage: "Fix PR / commit", plus user-facing mitigations |
| Number of affected users/products (if known) | Estimate; "unknown, under assessment" is acceptable at 24h |

## 4. Runbook: when triage confirms a real report

1. **Timestamp it.** Record report-arrival and triage-confirmation times
   in the advisory. The 24h/72h clocks run from confirmation.
2. **Classify** (see §2) and write the rationale into triage notes.
3. **Draft the 24h early notification** from the intake fields — even if
   some are "unknown". File it; do not wait for the fix.
4. **Start the fix in parallel** (private branch, security advisory
   workflow). The 72h notification must describe mitigation status, so
   the fix timeline matters.
5. **72h notification:** update with impact assessment, affected
   versions, and mitigation status.
6. **14d final report:** root cause, complete impact, corrective measures,
   and confirmation the fix is shipped.
7. **Close the loop:** link the ENISA/CSIRT case references back into the
   advisory; keep the advisory private until coordinated disclosure.

## 5. Standing readiness (do this before an incident)

- [ ] One maintainer owns the ENISA single-reporting-platform account and
  the CSIRT contact list; a deputy is named. (Names live in the private
  advisory template, not in this public doc.)
- [ ] The intake template's "Triage notes" already has fields for the two
  timestamps and the CRA classification — keep them.
- [ ] SBOM generation (`ebuild sbom`, where available) is the fastest way
  to answer "which products/versions are affected" — keep it working.
- [ ] Review this runbook after every incident (add a "lessons" section to
  the advisory) and at least yearly.

## 6. What this runbook is not

Legal advice. The CRA text and ENISA guidance are authoritative; when
they change, this runbook follows. The org's CVD policy (`SECURITY.md`)
governs disclosure to reporters and the public; this runbook governs
disclosure to authorities.
