# eSec — agent notes

Placeholder repository (Status: Planned). No implementation, build manifests
or tests exist on `master` yet. The repository holds the org security policy
(`SECURITY.md`, `.well-known/security.txt`) and security docs under `docs/`.
A docs workflow checks those docs, the README and `security.txt` (not
`SECURITY.md` or this file). The code that will become eSec lives in
[`embeddedos-org/eos`](https://github.com/embeddedos-org/eos) at
`services/security/` and `services/crypto/`. See [README.md](README.md).

## Build / test / lint

There is no build and there are no tests: no manifest (`package.json`,
`pyproject.toml`, `CMakeLists.txt`) and no source code. The one verified
command is the docs check that CI runs (`.github/workflows/ci.yml`):

```sh
python3 ci/check_docs.py
```

It needs only the Python standard library. It checks that each doc under
`docs/` and the README has one H1, that relative links resolve, and that
`.well-known/security.txt` has `Contact` and `Expires` and has not expired.
Do not invent other commands.

## Contributing

No `CONTRIBUTING.md` exists. Keep changes scoped and follow the repository's
automation and review requirements.

## Security

[SECURITY.md](SECURITY.md) is the coordinated vulnerability disclosure policy
for the whole organization; [docs/cvd-intake.md](docs/cvd-intake.md) is the
report template and [.well-known/security.txt](.well-known/security.txt) the
RFC 9116 contact file. Do not report suspected vulnerabilities in public
issues.

## Wiki mirror

`docs/wiki/` is a byte-for-byte mirror of the eSec wiki sources for offline
reference. The wiki and the source tree remain authoritative.
