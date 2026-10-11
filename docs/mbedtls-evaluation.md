# Mbed TLS evaluation for issue #5 milestone 1

**Repo:** `embeddedos-org/eSec` ·
**Decision of record:**
[ADR-012 — cryptographic provider selection](https://github.com/embeddedos-org/eos/blob/master/docs/adr/ADR-012-cryptographic-provider-selection.md)
(Proposed) ·
**Tracker:** [issue #5](https://github.com/embeddedos-org/eSec/issues/5)
("merge `eos/services/{security,crypto}` into eSec, 3 milestones")

This evaluation feeds **milestone 1** of issue #5: land ADR-012 — the Mbed TLS swap
for hand-rolled AES/SHA/RSA/ECC — so the `EOS_ALLOW_STUB_CRYPTO` stub gate
disappears with real verification. **No code moves in this document and none is
proposed to move here.** The merge decision remains with the issue tracker; this
document only records what the swap costs, what it buys, and what would change.

---

## 1. Current inventory: what `eos` ships today

Verified 2026-10-11 via the GitHub API against `embeddedos-org/eos`
(`GET /repos/embeddedos-org/eos/contents/services/crypto`, walking
`include/` and `src/` recursively). The eSec README's "16 source files (10 `.c`,
6 internal headers)" holds once the two *public* headers are counted separately:
**10 `.c` files, 6 internal headers, 2 public headers** (18 files, plus
`CMakeLists.txt`).

| File | Size | What it is |
|---|---|---|
| `src/aes.c` | ~9.4 KB | Hand-written AES (ECB/CBC-era design) |
| `src/sha256.c` | ~5.1 KB | Hand-written SHA-256 |
| `src/ed25519_fe.c` / `_ge.c` / `_sc.c` | ~73.5 KB | Hand-written Curve25519 field arithmetic |
| `src/ed25519_sha512.c`, `src/sha512.h` | ~11.6 KB | Hand-written SHA-512 |
| `src/ed25519_sign.c` / `_verify.c` | ~10.2 KB | Hand-written Ed25519 sign/verify |
| `src/precomp_data.h` | **~97.8 KB** | Precomputed Ed25519 tables (ROM pressure) |
| `src/fe.h`, `src/ge.h`, `src/sc.h`, `src/fixedint.h` | ~5.4 KB | Internal headers |
| `src/rsa_ecc_sha512.c` | ~9.9 KB | **RSA/ECDSA stubs — fail closed** |
| `src/crc.c` | ~2.1 KB | CRC-32 (not cryptographic; out of scope) |
| `include/eos/crypto.h` | ~4.3 KB | Public API |
| `include/ed25519.h` | ~1.6 KB | Public Ed25519 API |

The companion `services/security/` (`include/eos/security.h`, `src/security.c`)
holds the security framework: `eos_secureboot_verify_image()` calls
`eos_rsa_verify_sha256()`.

**What the code actually covers — and what it does not:**

- **Functional (NIST-vector passing):** AES, SHA-256, SHA-512, Ed25519 sign.
  Ed25519 *verification* is a known gap: per ADR-012 §5, the RFC 8032 §7.1
  vectors for verification **fail**, and they are the acceptance test for this
  work. A hand-written Ed25519 verify that fails standard vectors is exactly the
  code an attacker scrutinises first.
- **Stubs that refuse to run:** `eos_rsa_sign/verify_sha256`,
  `eos_ecc_sign/verify`, `eos_ecdsa_*` — `rsa_ecc_sha512.c` implements none of
  PKCS#1, PSS, or ECDSA. Without `EOS_ALLOW_STUB_CRYPTO` they print to stderr
  and return `-1`. The old versions were forgeable (the verify stub once
  accepted any 64-byte "signature"), and a real exploit path existed: secure
  boot consumed `eos_rsa_verify_sha256()`. Fail-closed is the right posture,
  but it means **secure boot with RSA currently cannot verify at all in a
  production build** — the stub *is* the feature.
- **Absent entirely:** TLS (any version), X.509 parsing/generation/verification,
  certificate chains, AEAD modes (GCM, CCM, ChaCha20-Poly1305), KDFs
  (PBKDF2/HKDF), DRBG, hardware-acceleration hooks. There is no story for a
  device that must terminate TLS to an OEM cloud or join a mutually-authenticated
  mesh.
- **Second copy:** `eBoot/core/` carries its own hand-rolled SHA-512 and an
  Ed25519 verify (ADR-012 context) — the same low-order-key bypass class existed
  in both copies, which is precisely the duplication the eSec README warns
  about.

## 2. Mbed TLS 3.x capability map

Mbed TLS 3.x is the current stable line; **3.6.4** is the recommended LTS
release as of October 2026 (the 4.0 line is in beta and explicitly not
production-ready). Verified against the Mbed-TLS releases page and Trusted
Firmware release notes.

- **TLS:** full TLS 1.3 (client and server, ephemeral key establishment,
  pre-shared keys, client authentication, server-side TLS 1.2/1.3 version
  negotiation, DTLS) alongside TLS 1.2. FFDH key exchange in TLS 1.3.
- **X.509:** parse, verify, generate; certificate chains, CSR parsing and
  generation, hostname verification, `cert_write` (PEM and DER), extended key
  usage.
- **PSA Crypto API:** Mbed TLS 3.x ships the PSA Crypto reference
  implementation and passes the PSA compliance suite. Since 3.1, essentially
  all TLS/X.509/PK operations run *through* PSA under the hood
  (`MBEDTLS_USE_PSA_CRYPTO` is effectively the only mode now). This is the
  interface that matters: silicon vendors map their crypto accelerators to the
  PSA driver interface, so the same call reaches software on one part and a
  crypto co-processor on another.
- **Footprint controls for MCUs:** `p256-m` (compact SECP256R1 via PSA —
  much smaller code and RAM than the classic ECP), `MBEDTLS_AES_ONLY_128_BIT_KEY_LENGTH`,
  ability to compile out AES/bignum/EC modules when PSA drivers provide them,
  PSA-client-only builds that offload everything to an external server.
- **Algorithmic breadth:** SHA-3, PBKDF2-HMAC/CMAC, HKDF, LMS/LM-OTS
  (post-quantum *verification* for firmware images), ChaCha20-Poly1305,
  CCM/GCM.
- **Maintenance:** a published security-advisory process with CVE-level
  disclosures and LTS backports — i.e. when a primitive breaks, there is a
  versioned upstream fix to pull instead of a hand-written line to patch.

## 3. Gap analysis: what `eos` lacks that Mbed TLS provides

| Need | `eos` today | Mbed TLS 3.x |
|---|---|---|
| TLS (client/server, 1.2/1.3) | Nothing | Complete |
| X.509 chain verification, cert issuance | Nothing | Complete |
| RSA/ECDSA verification that *works* | Fail-closed stubs | Production crypto |
| Ed25519 verification matching RFC 8032 | Hand-written, vectors fail | Verified implementation |
| AEAD (GCM/CCM/ChaCha20-Poly1305) | Nothing | Complete |
| KDFs (HKDF/PBKDF2) | Nothing | Complete |
| Hardware accelerator mapping | None | PSA driver interface |
| Advisory feed for discovered breaks | None (silent) | Published advisories + LTS backports |
| Secure boot end-to-end | Experimental, no real trust anchor shipped | Working verify + LMS for image signing |

The shape of the gap is what matters: it is not that `eos` has slow crypto —
it is that `eos` has **no verifiable asymmetric crypto and no transport
security at all**, while continuing to ship a secure-boot feature that depends
on both. Every new protocol the platform adds (OTA, device identity,
attestation) would otherwise re-invent these under the hand-rolled constraint.

## 4. Swap criteria for ADR-012

ADR-012 is **Proposed**, and names its own acceptance criteria. This evaluation
recommends holding it there until each is met — they are blocking
prerequisites, not follow-ups:

1. **Footprint budget for MCU targets.** Flash and RAM deltas must be measured
   on the smallest §21 Nano target in *both* configurations: the eBoot
   verify-only subset (SHA-512 + Ed25519 verify, everything else compiled out)
   and the full `eos` configuration. The 97.8 KB of precomputed Ed25519 tables
   leaves the tree; the Mbed TLS replacement's tables are the number to
   compare against, not a slogan.
2. **PSA alignment.** `eos/services/crypto/include/eos/crypto.h` stays as the
   EoS-facing API and becomes a thin shim over the PSA Crypto API, not over
   legacy `mbedtls_*` calls. This is what preserves the hardware-accelerator
   path: a future board's crypto co-processor plugs in as a PSA driver, and no
   call site changes.
3. **CRA SBOM implications.** A first third-party dependency in `eos` changes
   the compliance story: exact upstream version pinned, `NOTICE` attribution
   (Mbed TLS is Apache-2.0; ADR-012 flags re-verifying at import), SBOM entry
   per the EU Cyber Resilience Act obligations, and the project's security
   advisories wired into the intake process already standing up in eSec
   (`docs/cvd-intake.md`, `.well-known/security.txt`). A reviewed provider is
   only reviewed if it is *identifiable, versioned, and tracked* — ADR-012's
   provenance argument from the PR #57 rejection applies to the dependency
   itself.
4. **Conformance vectors in CI, deletion not coexistence.** Each adopted
   primitive lands with published vectors (FIPS 180-4, FIPS-197, RFC 8032
   §7.1) executing in the test suite; the hand-written file is deleted in the
   same commit its PSA replacement lands. CRC-32 stays (not a primitive).

Alternatives considered by ADR-012 stand: BearSSL (smaller, no PSA mapping —
forfeits the accelerator argument), libsodium verify-only (would mean two
providers), wolfSSL (GPLv2-or-commercial — incompatible with the MIT runtime),
and repairing the hand-rolled code (rejected by ADR-011 item 2).

## 5. Threat-model note: the Oct-2026 perimeter zero-day density

The perimeter-appliance CVE cluster of autumn 2026 is the strongest argument
for a fail-closed, maintained crypto substrate:

- **Cisco CVE-2026-76504** — added to the CISA Known Exploited Vulnerabilities
  catalog on 2026-09-30.
- **SonicWall CVE-2026-83548** — KEV-listed in early September; then
  **CVE-2026-102255** (CVSS 10.0, pre-authentication SSRF in the SMA1000
  Work Place interface, disclosed 2026-10-07) — the *third* pre-auth SSRF in
  the same interface in 2026, not yet KEV-listed but with exploitation
  attempts observed within 48 hours of disclosure.
- **FortiMail CVE-2026-104286** — KEV-listed 2026-10-01.

The pattern is not "four vendors had a bad month." It is that the appliances
sitting at trust boundaries — the exact network position EoS targets will
increasingly occupy in industrial and edge roles — are being probed with
pre-authentication remote flaws at a cadence measured in weeks, and the same
interface keeps yielding new zero-days after patching.

The lesson for this platform is fail-closed at every layer:

- An MCU target cannot absorb a weekly hotfix cadence. Its defence is (a)
  minimise the attack surface of the trusted code, and (b) make every
  unverifiable primitive **refuse** — which `eos` already does with
  `EOS_ALLOW_STUB_CRYPTO`, but only by leaving the feature absent.
- A maintained upstream with a published advisory feed (Mbed TLS's security
  advisories + LTS backports) is the only realistic way a small platform team
  matches the fix velocity of the threat. Hand-rolled crypto gets neither a
  fuzzing community nor a backport — when it breaks, it breaks silently.
- Until the swap lands, the honest status is the one ADR-011 requires:
  `EOS_SIG_ED25519` is **non-functional**, and package-signature verification
  stays Experimental. Inflating either is how the perimeter appliances in the
  CVE list got their "secure" labels.

## 6. Recommendation and milestone 1 changes

**Recommendation:** adopt Mbed TLS 3.6.x LTS via the PSA Crypto API as the
cryptographic provider for `eos`, per ADR-012 — contingent on the four swap
criteria in §4, with the footprint measurement as the blocking prerequisite.
The alternatives were weighed in ADR-012 and the weighting stands; the CVE
cluster in §5 only hardens the maintenance argument.

**What milestone 1 changes in `eos` (all in-tree, none of it in this repo):**

1. `services/crypto/src/aes.c` and `src/sha256.c` deleted; `eos/crypto.h`
   re-implemented as a thin PSA shim.
2. Real RSA/ECDSA/Ed25519 via Mbed TLS; `rsa_ecc_sha512.c` and the
   fail-closed stubs deleted; `EOS_ALLOW_STUB_CRYPTO` retired — nothing that
   pretends to verify remains.
3. RFC 8032 §7.1 verification vectors (currently failing) pass in CI, along
   with FIPS 180-4 and FIPS-197 vectors per primitive.
4. eBoot links the verify-only Mbed TLS configuration (SHA-512 + Ed25519
   verify; no signing, no TLS, no AEAD in the boot chain), deleting its
   hand-rolled SHA-512 and Ed25519 verify.
5. SBOM + `NOTICE` entries for the pinned Mbed TLS version land with the
   import; ADR-012 moves Proposed → Accepted.

Issue #5 stays open: milestones 2 (API stabilisation) and 3 (the `git subtree
split`, gated on Aswin's decision per §11) are untouched by this document.
