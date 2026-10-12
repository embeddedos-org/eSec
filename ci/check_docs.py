#!/usr/bin/env python3
"""Minimal docs check for the eSec repo (docs-only).

Checks (stdlib only):
  1. Every docs/*.md has exactly one H1. The GitHub-wiki navigation file
     docs/wiki/_Sidebar.md is exempt (it is a link list, not a document).
  2. Every relative link in every doc resolves to an existing file in the
     repo. GitHub-wiki-style extensionless links (e.g. `[Home](Home)`)
     resolve to `<page>.md` next to the linking file. Absolute URLs
     (http/https/mailto/...) and pure #anchors are skipped.

Exits non-zero with clear messages when anything fails.
"""

import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
H1_EXEMPT = {os.path.join("docs", "wiki", "_Sidebar.md")}

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
ABS_URL_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def doc_files():
    """All markdown docs: docs/**.md plus the root README.md."""
    found = []
    for dirpath, dirnames, filenames in os.walk(DOCS_DIR):
        dirnames.sort()
        for name in sorted(filenames):
            if name.endswith(".md"):
                found.append(os.path.join(dirpath, name))
    readme = os.path.join(REPO_ROOT, "README.md")
    if os.path.isfile(readme):
        found.append(readme)
    return found


def check_h1(path, rel):
    errors = []
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    h1s = [n + 1 for n, line in enumerate(lines) if line.startswith("# ")]
    if rel in H1_EXEMPT:
        return errors
    if len(h1s) != 1:
        errors.append(
            "%s: expected exactly one H1, found %d (%s)"
            % (rel, len(h1s), ", ".join("line %d" % n for n in h1s) or "none")
        )
    return errors


def check_links(path, rel):
    errors = []
    base = os.path.dirname(path)
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    for n, line in enumerate(lines, 1):
        for match in LINK_RE.finditer(line):
            target = match.group(1).strip()
            if not target or ABS_URL_RE.match(target) or target.startswith("#"):
                continue
            target = target.split("#", 1)[0]  # strip anchor fragment
            if not target:
                continue
            candidate = os.path.normpath(os.path.join(base, target))
            resolved = candidate if os.path.isfile(candidate) else None
            if resolved is None and not os.path.splitext(candidate)[1]:
                # GitHub-wiki convention: extensionless page links mean <page>.md
                with_md = candidate + ".md"
                if os.path.isfile(with_md):
                    resolved = with_md
            if resolved is None:
                errors.append(
                    "%s:%d: dangling relative link '%s' (no such file)"
                    % (rel, n, match.group(1))
                )
    return errors


def main():
    files = doc_files()
    if not files:
        print("FAIL: no markdown docs found under docs/", file=sys.stderr)
        return 1
    errors = []
    for path in files:
        rel = os.path.relpath(path, REPO_ROOT)
        errors.extend(check_h1(path, rel))
        errors.extend(check_links(path, rel))
    if errors:
        print("FAIL: docs check found %d problem(s):" % len(errors))
        for err in errors:
            print("  - %s" % err)
        return 1
    print("OK: %d docs checked, one H1 each, all relative links resolve" % len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
