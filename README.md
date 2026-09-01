# eSec

Security framework for the EmbeddedOS platform — reusable security services above the boot chain.

**Status: Implemented, with one part Experimental — in
[`eos`](https://github.com/embeddedos-org/eos), at `services/crypto/`.** Not here.

Under §28, *Implemented* means "feature exists and is usable", evidenced by code
and functional tests. The crypto services meet that: 15 source files and seven
test suites — `test_crypto`, `_aes`, `_ecc`, `_rsa`, `_sha512`,
`_ed25519_loworder`, `_failclosed` — all passing.

One part is **Experimental** rather than Implemented, and should not be read as
finished: package signature verification. `services/pkg/eos_pkg.c` verifies
against `eos_pkg_public_key[32] = {0}`, an all-zero trust anchor, and the
low-order-key rejection that makes such a key fail closed rather than open was
only just added (embeddedos-org/eos#99). Tracked as embeddedos-org/eos#98. A
verifier with no real key authenticates nothing, and this README should not
imply otherwise.

Depend on eSec through a **component manifest**, not through this repository —
see embeddedos-org/embeddedos-stack#20. The v2.0 master design is direct:

> §10: **Repositories should not be the dependency API.**

> §21.1: A subsystem earns a separate repository when it has a stable interface,
> independent release lifecycle, clear maintainers and multiple consumers.

None of those four holds for eSec today, and the cost of splitting anyway is
already visible: there are two independent Ed25519 implementations in the
platform, in eos and eBoot, and the same low-order-key bypass was present in
both. Duplication across repositories is how one fix stops being one fix.

This repository exists so the component has an issue tracker and a
place to record decisions before any code moves. It is deliberately not a
mirror: duplicating the sources here would give the platform two copies to
keep in step, and §24 of the architecture document is explicit that internal
modules should not be promoted into separate brands until they have stable
interfaces and users.

## What eSec owns

- Crypto abstraction
- Key management
- Device identity
- Secure storage
- Capabilities and permissions
- Attestation
- Certificates and TLS integration
- TPM / secure element / HSM adapters
- TrustZone and hardware isolation adapters

Today `eos` implements AES, SHA-256 and SHA-512, which pass NIST vectors. RSA
and ECC signature verification are stubs that refuse to run unless a build
defines `EOS_ALLOW_STUB_CRYPTO`; ADR-012 selects Mbed TLS to replace them.

## Where the code is now

| | |
|---|---|
| Implementation | [`eos`](https://github.com/embeddedos-org/eos) → `services/security/ and services/crypto/` |
| Maturity | [`eos/STATUS.md`](https://github.com/embeddedos-org/eos/blob/master/STATUS.md) |
| Decision of record | [ADR-012 — cryptographic provider selection](https://github.com/embeddedos-org/eos/blob/master/docs/adr/ADR-012-cryptographic-provider-selection.md) |

## When code moves here

The architecture document sets one condition, and it has not been met:

> It may start inside eos and become a separate repository only if independent release/versioning is justified. — §11

Until then, work on eSec happens in `eos`. Opening the split earlier would
cost a release cycle, a CI pipeline and a versioning story for a component
whose interface is still changing.

## Reference

- Architecture & Ecosystem Design Document — §11 (Platform / Core)
- [Repository taxonomy](https://github.com/embeddedos-org/eos) — §22
- [Organization model](https://github.com/embeddedos-org/.github) — §23

## License

MIT. See [LICENSE](LICENSE).
