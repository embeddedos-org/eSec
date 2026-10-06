# Vulnerability report intake

Copy this template into a
[private security advisory](https://github.com/embeddedos-org/eSec/security/advisories/new).
Fill in every section you can; "unknown" is an acceptable answer, a blank
section is not — it tells triage what still needs discovery.

## Affected component

- Repository:
- Version / commit:
- Board / target (if firmware):
- Configuration (build type, feature flags):

## Description

What is wrong, in one paragraph. Then the details: which file and function,
what the code does, and why that is a vulnerability rather than a bug.

## Reproduction

Steps, commands, or a minimal proof of concept. For a firmware issue, note
the hardware or simulator (EoSim) it was reproduced on.

## Impact

- What can an attacker achieve? (code execution, privilege escalation,
  information disclosure, denial of service, secure-boot bypass, …)
- What must the attacker already have? (physical access, a signed package,
  network adjacency, …)
- Your severity estimate and why:

## Suggested fix

Optional, but welcome — especially a pointer to how a comparable project
fixed the same class of issue.

## Reporter

- Name / handle (for credit in the advisory):
- Contact for follow-up questions:
- Disclosure preference: [ ] coordinated disclosure after fix
  [ ] full disclosure on a date: ____
  [ ] keep my name out of the public advisory

## Triage notes (maintainers only)

- Reproduced: [ ] yes [ ] no — notes:
- Severity:
- Fix PR / commit:
- CVE requested: [ ] yes [ ] no — ID:
- Advisory published:
