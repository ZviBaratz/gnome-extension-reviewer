#!/usr/bin/env python3
"""Tests for field test pipeline helper functions.

Covers make_finding_id (parse-lint-results.py) and
parse_annotations (diff-baselines.py) — the two most fragile
hand-rolled functions in the pipeline.
"""

import os
import sys
import tempfile
import unittest

# Add scripts/ to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from importlib import import_module

# Import modules with hyphens in names
parse_lint = import_module('parse-lint-results')
diff_baselines = import_module('diff-baselines')

make_finding_id = parse_lint.make_finding_id
parse_annotations = diff_baselines.parse_annotations


class TestMakeFindingId(unittest.TestCase):
    """Test stable finding ID generation."""

    def test_strips_line_numbers(self):
        result = make_finding_id('R-SEC-01', 'extension.js:42 uses eval()')
        self.assertEqual(result, 'R-SEC-01::extension.js uses eval()')

    def test_strips_multiple_line_numbers(self):
        result = make_finding_id('check', 'file.js:10 and file.js:20 issue')
        self.assertEqual(result, 'check::file.js and file.js issue')

    def test_strips_file_count_suffix(self):
        result = make_finding_id('R-WEB-01', 'setTimeout in 3 file(s): a.js, b.js, c.js')
        self.assertEqual(result, 'R-WEB-01::setTimeout')

    def test_strips_leading_file_list_with_path(self):
        result = make_finding_id('check', 'src/extension.js: uses deprecated API')
        self.assertEqual(result, 'check::uses deprecated API')

    def test_strips_dotfile_prefix(self):
        result = make_finding_id('check', './lib/utils.js: missing return')
        self.assertEqual(result, 'check::missing return')

    def test_preserves_non_file_colon_prefix(self):
        """GLib: message should NOT be stripped (no path-like . or /)."""
        result = make_finding_id('check', 'GLib: message about something')
        self.assertEqual(result, 'check::GLib: message about something')

    def test_normalizes_whitespace(self):
        result = make_finding_id('check', 'too   many    spaces')
        self.assertEqual(result, 'check::too many spaces')

    def test_combined_stripping(self):
        result = make_finding_id(
            'R-WEB-01',
            'src/lib/timer.js:99: setTimeout in 2 file(s): timer.js, main.js'
        )
        self.assertEqual(result, 'R-WEB-01::setTimeout')

    def test_no_detail_change_needed(self):
        result = make_finding_id('quality/code-provenance', 'score 3 (hand-written)')
        self.assertEqual(result, 'quality/code-provenance::score 3 (hand-written)')

    def test_check_name_preserved(self):
        result = make_finding_id('quality/ai-slop', 'some detail')
        self.assertTrue(result.startswith('quality/ai-slop::'))


class TestParseAnnotations(unittest.TestCase):
    """Test hand-rolled YAML annotation parser."""

    def _write_temp(self, content):
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        f.write(content)
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

    def test_basic_parsing(self):
        path = self._write_temp("""\
findings:
  - id: "R-SEC-01::uses eval()"
    classification: tp
  - id: "R-WEB-01::setTimeout"
    classification: fp
""")
        result = parse_annotations(path)
        self.assertEqual(result, {
            'R-SEC-01::uses eval()': 'tp',
            'R-WEB-01::setTimeout': 'fp',
        })

    def test_skips_comments_and_blanks(self):
        path = self._write_temp("""\
# This is a comment
findings:
  - id: "check::detail"
    classification: borderline

  # Another comment
  - id: "check2::detail2"
    classification: expected
""")
        result = parse_annotations(path)
        self.assertEqual(len(result), 2)

    def test_missing_classification_warns(self, ):
        path = self._write_temp("""\
findings:
  - id: "orphan::no-class"
  - id: "next::has-class"
    classification: tp
""")
        import io
        from contextlib import redirect_stderr
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            result = parse_annotations(path)
        self.assertIn('orphan::no-class', stderr.getvalue())
        self.assertEqual(result, {'next::has-class': 'tp'})

    def test_trailing_entry_without_classification_warns(self):
        path = self._write_temp("""\
findings:
  - id: "last::entry"
""")
        import io
        from contextlib import redirect_stderr
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            result = parse_annotations(path)
        self.assertIn('last::entry', stderr.getvalue())
        self.assertEqual(result, {})

    def test_nonexistent_file_returns_empty(self):
        result = parse_annotations('/nonexistent/path.yaml')
        self.assertEqual(result, {})

    def test_none_path_returns_empty(self):
        result = parse_annotations(None)
        self.assertEqual(result, {})

    def test_unquoted_ids(self):
        path = self._write_temp("""\
findings:
  - id: check::detail
    classification: tp
""")
        result = parse_annotations(path)
        self.assertEqual(result, {'check::detail': 'tp'})

    def test_single_quoted_ids(self):
        path = self._write_temp("""\
findings:
  - id: 'check::detail'
    classification: fp
""")
        result = parse_annotations(path)
        self.assertEqual(result, {'check::detail': 'fp'})

    def test_notes_field_ignored(self):
        path = self._write_temp("""\
findings:
  - id: "check::detail"
    classification: tp
    notes: "this should be ignored"
""")
        result = parse_annotations(path)
        self.assertEqual(result, {'check::detail': 'tp'})


if __name__ == '__main__':
    unittest.main()
