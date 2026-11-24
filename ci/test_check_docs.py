#!/usr/bin/env python3
"""Tests for ci/check_docs.py (stdlib unittest; run: python3 -m unittest discover -s ci)."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_docs  # noqa: E402


class FencedCodeTest(unittest.TestCase):
    def check(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "page.md")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
            return check_docs.check_h1(path, "page.md") + check_docs.check_links(path, "page.md")

    def test_comment_in_shell_block_is_not_an_h1(self):
        doc = "# Page\n\n```bash\n# clone the repo\ngit clone x\n```\n"
        self.assertEqual(self.check(doc), [])

    def test_tilde_fence_and_longer_backtick_fence(self):
        doc = "# Page\n\n~~~sh\n# one\n~~~\n\n````md\n```\n# two\n```\n````\n"
        self.assertEqual(self.check(doc), [])

    def test_link_syntax_inside_code_block_is_not_checked(self):
        doc = "# Page\n\n```markdown\nSee [the guide](docs/your-page.md).\n```\n"
        self.assertEqual(self.check(doc), [])

    def test_prose_is_still_checked(self):
        doc = "# Page\n\n```\ncode\n```\n\n# Second\n\n[x](missing.md)\n"
        errors = self.check(doc)
        self.assertEqual(len(errors), 2, errors)
        self.assertIn("expected exactly one H1, found 2 (line 1, line 7)", errors[0])
        self.assertIn("page.md:9: dangling relative link 'missing.md'", errors[1])

    def test_unclosed_fence_hides_the_rest(self):
        doc = "# Page\n\n```\n# not a heading\n"
        self.assertEqual(self.check(doc), [])


class SecurityTxtExpiresTest(unittest.TestCase):
    def check(self, expires):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "security.txt")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("Contact: mailto:security@example.org\nExpires: %s\n" % expires)
            saved = check_docs.SECURITY_TXT
            check_docs.SECURITY_TXT = path
            try:
                return check_docs.check_security_txt()
            finally:
                check_docs.SECURITY_TXT = saved

    def test_rfc3339_date_times_pass(self):
        for value in (
            "2099-10-04T00:00:00.000Z",
            "2099-10-04T00:00:00Z",
            "2099-10-04t00:00:00z",
            "2099-10-04 00:00:00Z",
            "2099-10-04T05:30:00+05:30",
            "2099-10-04T00:00:00.5-08:00",
        ):
            self.assertEqual(self.check(value), [], value)

    def test_iso8601_forms_outside_rfc3339_fail(self):
        for value in (
            "2099-10-04",  # date only
            "20991004",  # basic format
            "2099-W40-1",  # week date
            "2099-10-04T00",  # no minutes or seconds
            "2099-10-04T00:00:00",  # no UTC offset
        ):
            errors = self.check(value)
            self.assertEqual(len(errors), 1, value)
            self.assertIn("is not an RFC 3339 date-time", errors[0])

    def test_past_date_still_fails(self):
        errors = self.check("2000-01-01T00:00:00Z")
        self.assertEqual(len(errors), 1)
        self.assertIn("is in the past", errors[0])


if __name__ == "__main__":
    unittest.main()
