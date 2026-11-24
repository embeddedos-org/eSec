#!/usr/bin/env python3
"""Minimal docs check for the eSec repo (docs-only).

Checks (stdlib only):
  1. Every docs/*.md has exactly one H1. The GitHub-wiki navigation file
     docs/wiki/_Sidebar.md is exempt (it is a link list, not a document).
     Lines inside fenced code blocks (``` or ~~~) are code, not Markdown:
     a "# comment" there is not an H1, and link syntax there is not a link.
  2. Every relative link in every doc resolves to an existing file in the
     repo. GitHub-wiki-style extensionless links (e.g. `[Home](Home)`)
     resolve to `<page>.md` next to the linking file. Absolute URLs
     (http/https/mailto/...) and pure #anchors are skipped.
  3. .well-known/security.txt carries the RFC 9116 mandatory fields
     (Contact, Expires), its Expires value is an RFC 3339 date-time with
     a UTC offset (RFC 9116 section 2.5.5), and that date is not in the past. An
     expired security.txt silently breaks the CRA reporting path
     documented in docs/cra-reporting.md, so expiry is a hard failure
     here, not a warning that can age unnoticed.

Exits non-zero with clear messages when anything fails.
"""

import os
import re
import sys
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
H1_EXEMPT = {os.path.join("docs", "wiki", "_Sidebar.md")}

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
SECURITY_TXT = os.path.join(REPO_ROOT, ".well-known", "security.txt")
ABS_URL_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
# RFC 3339 section 5.6 date-time: full-date "T" full-time, where full-time
# ends in a time-offset ("Z" or +hh:mm / -hh:mm). The section 5.6 note
# allows lower-case t/z and a space in place of the "T".
RFC3339_DATE_TIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}[Tt ]\d{2}:\d{2}:\d{2}(\.\d+)?([Zz]|[+-]\d{2}:\d{2})$"
)


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


def prose_lines(path):
    """(line number, text) for each line outside fenced code blocks.

    A fence opens with 3+ backticks or tildes (up to 3 spaces of indent) and
    closes with a line of the same character, at least as long, and nothing
    else. An unclosed fence runs to the end of the file (CommonMark).
    """
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    fence = None
    for n, line in enumerate(lines, 1):
        match = FENCE_RE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
            else:
                yield n, line
        elif (match and match.group(1)[0] == fence[0]
              and len(match.group(1)) >= len(fence)
              and not line.strip().lstrip(fence[0])):
            fence = None


def check_h1(path, rel):
    errors = []
    h1s = [n for n, line in prose_lines(path) if line.startswith("# ")]
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
    for n, line in prose_lines(path):
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


def check_security_txt():
    """RFC 9116: Contact and Expires are mandatory; Expires must be future."""
    errors = []
    rel = ".well-known/security.txt"
    if not os.path.isfile(SECURITY_TXT):
        return ["%s: file is missing" % rel]
    fields = {}
    with open(SECURITY_TXT, encoding="utf-8") as fh:
        for line in fh.read().splitlines():
            if ":" in line and not line.lstrip().startswith("#"):
                key, _, value = line.partition(":")
                fields.setdefault(key.strip().lower(), value.strip())
    for required in ("contact", "expires"):
        if not fields.get(required):
            errors.append("%s: RFC 9116 mandatory field '%s' is missing" % (rel, required))
    raw_expires = fields.get("expires")
    if raw_expires:
        # datetime.fromisoformat() also takes ISO 8601 forms that RFC 3339
        # does not (a bare date, a week date, no UTC offset), so match the
        # RFC 3339 shape first and parse only what passes.
        try:
            if not RFC3339_DATE_TIME_RE.match(raw_expires):
                raise ValueError(raw_expires)
            expires = datetime.fromisoformat(
                raw_expires.replace("Z", "+00:00").replace("z", "+00:00")
            )
        except ValueError:
            errors.append(
                "%s: Expires '%s' is not an RFC 3339 date-time with a UTC "
                "offset (e.g. 2027-10-04T00:00:00Z)" % (rel, raw_expires)
            )
            return errors
        if expires <= datetime.now(timezone.utc):
            errors.append(
                "%s: Expires %s is in the past — an expired security.txt "
                "breaks the CRA reporting path (docs/cra-reporting.md); "
                "renew it before it lapses" % (rel, raw_expires)
            )
    return errors


def main():
    files = doc_files()
    if not files:
        print("FAIL: no markdown docs found under docs/", file=sys.stderr)
        return 1
    errors = []
    errors.extend(check_security_txt())
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
