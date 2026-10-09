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
6. **Tool-registration command allowlists.** Any tool registration that can
   cause command execution declares the exact commands/paths allowed; a
   config-supplied command is untrusted input, never interpolated into a
   shell string. (CVE-2026-105697 below is the CVSS 9.9 proof this control
   is load-bearing.)

## Threat taxonomy: the six MCP attack classes

The Agentics' *Enterprise MCP Guide 2026* (Oct 5) names six attack
classes — with 68 MCP server CVEs disclosed in one month as the
backdrop. Each maps to an existing control above; the guide is the
external validation of this posture.

| # | Attack class | What it is | eSec control |
|---|---|---|---|
| 1 | **Tool poisoning** | A tool's description is altered to smuggle malicious instructions into the agent's context | Control 1 (allowlisted servers) + pinned descriptions at registration |
| 2 | **Schema poisoning** | The declared parameter schema is widened beyond what the tool honestly accepts | Boundary schema validation — descriptors are validated, never trusted |
| 3 | **Tool shadowing** | A lower-privilege tool overrides a higher-privilege tool's identity | Privilege-scoped registration: no shadowing across trust levels; collisions fail closed |
| 4 | **Command injection** | Tool arguments become shell commands | Control 6 (command allowlists) — CVE-2026-105697 is the CVSS 9.9 proof |
| 5 | **Shadow servers** | Rogue servers the agent discovers and trusts | Control 1 + Control 5 (no implicit intra-network trust; every call re-authenticates) |
| 6 | **Context oversharing** | Tools receive more context than they need | Control 3 (credential isolation) + Control 4 (upstream redaction) |

The guide's control set — per-agent allowlists, identity binding,
centralized MCP gateways, human approval for destructive actions —
is the day-one posture the agent-fabric gateway evaluation
(`embeddedos-org/EoSim` `docs/mcp-gateway-eval.md`) now requires.

## Evidence links

- unite.ai — researcher disclosure on the MCP protocol gap.
- techtimes (Oct 6) — 5 US federal MCP servers unpatched 6 weeks post-disclosure.
- einpresswire — ClawSecure AI Agent Threat Report Vol 1.
- CVE-2026-105697 (CVSS 9.9, Oct 5) — Langflow MCP server config executed
  the user-typed `command` via `bash -c` with no allowlist: config-file
  command execution. Patch 1.10.3. Control 6 is the mitigation.
- CVE-2026-104120 (Oct 2) — `mcp-server-fetch` <= 2026.6.4 SSRF via
  `fetch_url`, publicly disclosed exploit. Fetch-style tools are network
  egress: allowlisted destinations only.

## Trust-track input: Logic Fruit L-Nex (2026-10-06)

L-Nex is an FPGA-based OCP DC-SCM 2.x BMC running OpenBMC, announced with
a hardware root of trust (secure + measured boot, attestation,
NIST SP 800-193) and "a path to post-quantum cryptography without
replacing the management architecture." Three angles for the eBoot/eSec
trust tracks:

1. **NIST SP 800-193 as the compliance anchor.** Protection, detection,
   and recovery for firmware resiliency -- the same triad the KEV/CRA
   docs already track. L-Nex shipping it in a BMC is the precedent for
   requiring it in our boot design docs.
2. **PQC crypto-agility without re-spin.** L-Nex's post-quantum path
   argues for *measured-boot crypto agility* in eBoot: the boot chain
   must be able to swap signature algorithms without a hardware
   re-spin. The #162 envelope's algorithm agility is the software side
   of this.
3. **Measured boot + attestation as table stakes.** A BMC shipping
   attestation in 2026 means our boot chain's attestation story is not
   a differentiator -- it is the entry ticket.

## Standing KEV/CRA input

The monthly dev.to "Open-Source Device CVEs: What to Patch by Vertical"
series is the standing human-readable layer over the KEV feed for
bootloader-class upstreams (Mbed TLS, U-Boot, TF-A) and is tracked as part of
the org's CRA-readiness posture.
