# MCP hostile-protocol hardening

Date: 2026-10-07.

Posture: treat the **Model Context Protocol itself as hostile-by-default** —
not just the server implementations. Two converging disclosures this week
forced this stance:

- **ClawSecure AI Agent Threat Report Vol 1** (Sept 24, reported Oct 6):
  cracked MCP integrations (Linear, Notion, Dropbox Dash) — the report's
  central finding is that "the gap sits in the MCP protocol itself," not only
  in individual servers.
- **Mohiuddin analysis**: the MCP specification carries **no normative
  security requirements** — security is currently conventional, not mandated.

In other words: even a spec-conformant MCP deployment cannot be assumed safe.

## Hardening controls

1. **Allowlisted servers.** Only explicitly listed MCP servers may be
   attached to agents. Discovery-on-the-network is off by default.
2. **Pinned server versions.** Pin exact versions; upgrades are a deliberate
   review event, not `latest`.
3. **Credential isolation.** Agents' credentials are never handed to MCP
   servers; servers authenticate with their own scoped tokens. A compromised
   server must not become a launchpad into other systems (Oct-6 chain-of-trust
   analysis: one compromised agent = launchpad across every agent that trusts
   it).
4. **Upstream-response redaction.** Error messages, tool outputs, and
   response envelopes are scrubbed of secrets/PII before they cross trust
   boundaries — redaction is a transport requirement, not a logging
   afterthought. (See also the Oct-6 report: a US federal MCP server logged
   veterans' SSNs in *unredacted* error responses, unpatched 6 weeks
   post-disclosure.)
5. **No implicit intra-network trust.** Agents and servers inside the same
   network do not trust each other by default; every call re-authenticates.

## Evidence links

- unite.ai — researcher disclosure on the MCP protocol gap.
- techtimes (Oct 6) — 5 US federal MCP servers unpatched 6 weeks post-disclosure.
- einpresswire — ClawSecure AI Agent Threat Report Vol 1.

## Standing KEV/CRA input

The monthly dev.to "Open-Source Device CVEs: What to Patch by Vertical"
series is the standing human-readable layer over the KEV feed for
bootloader-class upstreams (Mbed TLS, U-Boot, TF-A) and is tracked as part of
the org's CRA-readiness posture.
