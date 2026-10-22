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

## Appendix: worked examples (October 2026)

Timestamped, CVE-numbered proof the taxonomy above is live — not theoretical.

**Langflow CVE-2026-105697 (CVSS 9.9, disclosed Oct 5).** OS command
injection in MCP server handling: the stdio transport launched a
user-supplied `command`/`args` pair via `bash -c` with no allowlist on the
executable and no validation of the arguments. Public proof-of-concept;
fixed in 1.10.3. The flaw was not in Langflow's business logic but in its
*protocol handling* — which is why the command-injection control has to
live at the trust boundary (allowlisted executables, declared at
registration), not inside each tool. This is the class the eIPC
tool-registration allowlist and the eVera tool-use policy exist for.

**ClawSecure AI Agent Threat Report Vol 1 (Sept 24).** Three clean,
production MCP implementations — Linear, Notion, Dropbox Dash — cracked
with the same attack class. Three independent codebases, three vendors,
one flaw shape: when the same class lands in three clean implementations,
the defect is in the protocol's missing security requirements, not in any
one implementation. That is the entire reason a hostile-protocol hardening
document has to exist: the MCP spec's lack of normative security
requirements pushes the security burden onto every implementer, and most
implementers will not carry it.

## Appendix: the October 2026 OAuth/session cluster (2026-10-20)

Three advisories in nine days, one shared shape — **trust placed in
counterparty-supplied metadata, and fallbacks that authenticate
nobody**:

- **CVE-2026-104850 / GHSA-6qxp-vccf-f47h** (high, 2026-10-06) —
  MCP TypeScript SDK: an OAuth client could be steered to send
  credentials to an authorization server chosen by the MCP server
  (issuer confusion). Affected `@modelcontextprotocol/sdk`
  >= 1.12.0 < 1.31.0 and `@modelcontextprotocol/client`
  >= 2.0.0 < 2.2.0; fixed in 1.31.0 / 2.2.0.
- **CVE-2026-59822 / GHSA-7488-6r32-c95q** (2026-10-13) —
  LiteLLM's MCP Streamable HTTP endpoint allowed unauthenticated
  session establishment through an OAuth2-passthrough fallback: a
  fabricated `Authorization` header was treated as authenticated.
  Fixed in LiteLLM 1.84.0.
- **CVE-2026-59951 / GHSA-84m7-p3x7-pcfv** (medium, 2026-10-15) —
  MCP Python SDK: unbounded session accumulation in the
  StreamableHTTP transport allows resource exhaustion.

Two controls follow directly and are adopted here as additions to
the list above:

7. **Authorization-server identity is pinned, never discovered from
   the counterparty.** A server may not choose, redirect, or
   substitute the issuer a client authenticates against
   (CVE-2026-104850). This is Control 5 applied to identity
   metadata: the issuer is configuration, not protocol data.
8. **Authentication has no fallback path, and sessions are a
   bounded resource.** A failed or absent credential is terminal —
   never a passthrough to an authenticated session
   (CVE-2026-59822) — and any stateful transport caps concurrent
   sessions and expires idle ones (CVE-2026-59951). An
   unauthenticated peer must not be able to allocate unbounded
   server state.

**Org exposure, measured 2026-10-20 (code search, not assumed):**
no repository in the org uses `@modelcontextprotocol/sdk`
(zero hits org-wide), and the org's MCP servers (EoSim, eFlow,
eosllm) are stdio transports with no OAuth flow — the
issuer-confusion and passthrough classes do not reach them as
built. The one dependency thread, eVera's LiteLLM, was assessed
the same day: `pyproject.toml` floors it at `>= 1.40` and
`requirements.txt` at `>= 1.0.0` (floors, not pins — nothing
holds it below the 1.84.0 fix), `vera.spec` carries no version
pin, and no code serves LiteLLM's proxy or MCP endpoint.
CVE-2026-59822 is therefore **assessed, not applicable** to
eVera as built; it becomes applicable the day any org component
exposes a LiteLLM proxy endpoint, which is why the control
belongs here rather than in a per-repo note.

The cluster is also the worked example for the agent fabric's
gateway evaluation: a gateway is exactly where counterparty
metadata concentrates, so the gateway inherits Controls 7–8 as
acceptance criteria, alongside the eNet bridge trial's "no
unauthenticated fallback path" exit check.

## Appendix: the October 2026 session-binding cluster (2026-10-22)

Two further advisories, published 2026-10-20 and verified
first-party in GitHub's advisory database on 2026-10-22, share a
different shape from the OAuth cluster above — **an identifier
trusted without being bound to its owner**:

- **CVE-2026-111770 / GHSA-jm63-cq47-j5jp** —
  `@modelcontextprotocol/server` 2.0.0 through 2.2.0, fixed in
  2.3.0: an HTTP MCP server that shared one stateless transport
  or one server instance across clients matched responses and
  notifications to connections by JSON-RPC `id` alone. SDK
  clients number requests from 0, so ids collide in normal use
  and one client could receive another's messages. Not affected:
  stdio servers, per-request server factories, and
  `@modelcontextprotocol/sdk` 1.26.0 and later.
- **CVE-2026-111767 / GHSA-22jm-h49p-29qw** —
  `@modelcontextprotocol/sdk` 1.24.0 through 1.31.0, fixed in
  1.32.0: the experimental tasks feature's `taskStore` did not
  check which session created a task, so clients sharing one
  `InMemoryTaskStore` could list, read, and cancel each other's
  tasks. Each task is now tied to the session that created it.

One control follows and is adopted here as an addition to the
list above:

9. **Responses and tasks are bound to the connection that
   created them.** Routing and lookup are keyed by
   (connection, id), never by id alone, and task/result stores
   are session-scoped — one client's objects are not listable,
   readable, or cancellable by another (CVE-2026-111770,
   CVE-2026-111767). An identifier is a name inside a scope,
   not a capability.

**Census correction (2026-10-22).** The exposure line in the
2026-10-20 appendix above was measured against a single package
name, `@modelcontextprotocol/sdk`. Re-run on 2026-10-22 (code
search, org-wide) against all three package names plus the bare
string: `@modelcontextprotocol/server` — zero hits;
`@modelcontextprotocol/client` and `@modelcontextprotocol/sdk`
— two hits each, both this document and its `llms-full.txt`
(prose mentions, not dependencies); bare `modelcontextprotocol`
adds one EoSim README mention. **Zero MCP TypeScript SDK
dependencies exist anywhere in the org under any of the three
names** — the correction widens the measurement, and the
conclusion stands.

Control 9 joins Controls 7–8 as an acceptance criterion for the
agent fabric's gateway evaluation: a gateway that routes by id
alone, or pools task state across sessions, fails the eval on
this control. The same keying rule is a design input for eIPC's
planned zero-copy tensor transport — tensors, like tasks, must
be keyed by (owner, id), never by id alone.
