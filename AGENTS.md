# eSec — agent notes

Placeholder repository (Status: Planned). No implementation, build manifests,
tests, or automation exist on `master` yet. The code that will become eSec
lives in [`embeddedos-org/eos`](https://github.com/embeddedos-org/eos) at
`services/security/` and `services/crypto/`. See [README.md](README.md).

## Build / test / lint

No verified commands exist: the tree holds only `README.md`, `LICENSE`, and
`.gitignore` — no manifest (`package.json`, `pyproject.toml`,
`CMakeLists.txt`), no workflows, no tests, and the README documents no
commands. Do not invent commands; re-check the README before running anything.

## Contributing

No `CONTRIBUTING.md` exists. Keep changes scoped and follow the repository's
automation and review requirements.

## Security

No `SECURITY.md` exists. Do not report suspected vulnerabilities in public
issues; use GitHub private security advisories or a private org channel.
Background: [docs/wiki/Security.md](docs/wiki/Security.md).

## Wiki mirror

`docs/wiki/` is a byte-for-byte mirror of the eSec wiki sources for offline
reference. The wiki and the source tree remain authoritative.
