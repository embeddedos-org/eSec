# Security Policy — EmbeddedOS (EoS) Research Foundation

This is the coordinated vulnerability disclosure (CVD) policy for all
repositories in the [embeddedos-org](https://github.com/embeddedos-org)
GitHub organization. It covers the operating system (`eos`), the bootloader
(`eBoot`), build and developer tooling, simulators, applications, and this
repository (`eSec`), which is the home for platform security policy even
though the implementation currently lives in `eos/services/crypto/` and
`eos/services/security/`.

## Reporting a vulnerability

**Do not open a public issue for a suspected vulnerability.**

- **Preferred:** open a [private security
  advisory](https://github.com/embeddedos-org/eSec/security/advisories/new)
  on this repository. Advisories keep the report confidential while the
  maintainers triage, and they become the CVE request vehicle if the issue
  qualifies.
- **Fallback:** if advisories are unavailable to you, open an issue titled
  "Security contact request" with no technical details; a maintainer will
  open a private channel.

Use the [intake template](docs/cvd-intake.md) so the report arrives with
everything needed for triage: affected repository and version/commit,
description, reproduction, impact, and your disclosure preferences.

## What happens next

| Step | Target |
|------|--------|
| Acknowledgement of your report | 2 business days |
| Triage (reproduced / not reproduced, severity) | 7 days |
| Fix on the default branch | 30 days for High/Critical, 90 days for others |
| Public disclosure (advisory + CVE if applicable) | after the fix is released, or 90 days from the report, whichever the reporter agrees to |

Targets are goals, not guarantees: a bootloader or OS fix that needs
hardware validation can take longer, and the maintainers will say so on the
advisory rather than go quiet.

## Scope

In scope: every public repository under `embeddedos-org`, including
firmware, host tooling, simulators, and the www.embeddedos.org site. Out of
scope: the archived `embeddedos-org.github.io` static site (parked, not
maintained), and vulnerabilities in third-party dependencies themselves —
report those upstream, then tell us so we can take the fixed dependency.

## Safe harbor

If you follow this policy — report privately, give the maintainers a
reasonable window to fix, and avoid data destruction, service disruption,
or accessing other users' data — the EmbeddedOS project will not pursue
legal action for your security research. This is a statement of intent,
not legal advice.

## EU Cyber Resilience Act readiness

The CRA obliges manufacturers of products with digital elements to run a
vulnerability-handling process: a CVD policy, timely fixes, and SBOMs. This
repository is where the project's side of that process lives:

- this policy (`SECURITY.md`) — the CVD process;
- [`docs/cvd-intake.md`](docs/cvd-intake.md) — the report template;
- [`.well-known/security.txt`](.well-known/security.txt) — machine-readable
  security contact (RFC 9116);
- per-build CycloneDX SBOMs — emitted by CI (see `.github/workflows/`);
- CISA KEV screening — reusable workflow in `.github`.

## Supported versions

Security fixes land on each repository's default branch. There are no
long-term support branches yet; when a release is cut, its branch receives
security backports for 6 months.
