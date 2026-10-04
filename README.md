# eSec

Security framework for the EmbeddedOS platform — reusable security services above the boot chain.

**Status: Planned.** There is no implementation in this repository yet. The
code that will become eSec lives in [`eos`](https://github.com/embeddedos-org/eos)
today, at `services/security/ and services/crypto/`.

This repository exists so the component has a home, an issue tracker, and a
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

## Security

eSec is the home for platform security policy. To report a vulnerability,
see [SECURITY.md](SECURITY.md) (coordinated disclosure policy),
[docs/cvd-intake.md](docs/cvd-intake.md) (report template), and
[.well-known/security.txt](.well-known/security.txt) (RFC 9116 contact).

## Reference

- Architecture & Ecosystem Design Document — §11 (Platform / Core)
- [Repository taxonomy](https://github.com/embeddedos-org/eos) — §22
- [Organization model](https://github.com/embeddedos-org/.github) — §23

## License

MIT. See [LICENSE](LICENSE).
