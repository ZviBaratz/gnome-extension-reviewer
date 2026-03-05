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
parse_lint_output = parse_lint.parse_lint_output
parse_annotations = diff_baselines.parse_annotations
diff_results = diff_baselines.diff_results


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


class TestParseLintOutput(unittest.TestCase):
    """Test ego-lint output parsing."""

    def test_result_lines(self):
        lines = [
            "[PASS] metadata/exists  metadata.json found\n",
            "[FAIL] R-SEC-01  extension.js:42 uses eval()\n",
            "[WARN] R-WEB-01  setTimeout in 2 file(s): a.js, b.js\n",
            "[SKIP] schema/validate  no schemas found\n",
        ]
        findings, metrics, counts, prov = parse_lint_output(lines)
        self.assertEqual(counts, {'pass': 1, 'fail': 1, 'warn': 1, 'skip': 1, 'total': 4})
        self.assertEqual(len(findings), 3)  # PASS not in findings
        self.assertEqual(findings[0]['status'], 'FAIL')
        self.assertEqual(findings[0]['check'], 'R-SEC-01')

    def test_metric_lines(self):
        lines = [
            "[METRIC] js-files: 5\n",
            "[METRIC] total-lines: 1200\n",
            "[METRIC] largest-file: extension.js (800 lines)\n",
        ]
        findings, metrics, counts, prov = parse_lint_output(lines)
        self.assertEqual(metrics['js_files'], 5)
        self.assertEqual(metrics['total_lines'], 1200)
        self.assertEqual(metrics['largest_file'], 'extension.js (800 lines)')

    def test_fix_suggestions(self):
        lines = [
            "[FAIL] R-WEB-01  setTimeout in 1 file(s): a.js\n",
            "--- FIX SUGGESTIONS ---\n",
            "  R-WEB-01: Use GLib.timeout_add() instead\n",
            "------\n",
        ]
        findings, metrics, counts, prov = parse_lint_output(lines)
        self.assertEqual(findings[0]['fix'], 'Use GLib.timeout_add() instead')

    def test_provenance_score(self):
        lines = [
            "[PASS] quality/code-provenance  score 3 (hand-written)\n",
        ]
        findings, metrics, counts, prov = parse_lint_output(lines)
        self.assertEqual(prov, 3)

    def test_zero_results_warns(self):
        import io
        from contextlib import redirect_stderr
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            findings, metrics, counts, prov = parse_lint_output(["not a result line\n"])
        self.assertIn('parsed 0 results', stderr.getvalue())

    def test_empty_input(self):
        findings, metrics, counts, prov = parse_lint_output([])
        self.assertEqual(counts['total'], 0)
        self.assertEqual(findings, [])
        self.assertIsNone(prov)

    def test_metric_non_integer_fallback(self):
        import io
        from contextlib import redirect_stderr
        stderr = io.StringIO()
        lines = ["[METRIC] js-files: unknown\n"]
        with redirect_stderr(stderr):
            findings, metrics, counts, prov = parse_lint_output(lines)
        self.assertEqual(metrics['js_files'], 'unknown')
        self.assertIn("non-integer value for metric 'js-files'", stderr.getvalue())


class TestDiffResults(unittest.TestCase):
    """Test baseline diff computation."""

    def _make_result(self, findings, counts=None):
        if counts is None:
            counts = {'pass': 0, 'fail': len(findings), 'warn': 0, 'skip': 0,
                      'total': len(findings)}
        return {'name': 'test', 'findings': findings, 'counts': counts,
                'ego_lint_version': 'abc', 'timestamp': '2026-01-01'}

    def test_identical_findings(self):
        f = [{'id': 'a::1', 'status': 'FAIL', 'check': 'a', 'detail': '1'}]
        result = diff_results(self._make_result(f), self._make_result(f), {})
        self.assertFalse(result['changed'])
        self.assertEqual(result['new_findings'], [])
        self.assertEqual(result['resolved_findings'], [])

    def test_new_finding(self):
        old = [{'id': 'a::1', 'status': 'FAIL', 'check': 'a', 'detail': '1'}]
        new = old + [{'id': 'b::2', 'status': 'WARN', 'check': 'b', 'detail': '2'}]
        result = diff_results(self._make_result(new), self._make_result(old), {})
        self.assertTrue(result['changed'])
        self.assertEqual(len(result['new_findings']), 1)
        self.assertEqual(result['new_findings'][0]['id'], 'b::2')

    def test_resolved_finding(self):
        old = [{'id': 'a::1', 'status': 'FAIL', 'check': 'a', 'detail': '1'}]
        result = diff_results(self._make_result([]), self._make_result(old), {})
        self.assertTrue(result['changed'])
        self.assertEqual(len(result['resolved_findings']), 1)

    def test_annotation_filtering(self):
        f = [{'id': 'a::1', 'status': 'FAIL', 'check': 'a', 'detail': '1'}]
        annotations = {'a::1': 'tp'}
        result = diff_results(self._make_result(f), self._make_result(f), annotations)
        self.assertEqual(len(result['unannotated_findings']), 0)

    def test_unannotated_findings(self):
        f = [{'id': 'a::1', 'status': 'FAIL', 'check': 'a', 'detail': '1'}]
        result = diff_results(self._make_result(f), self._make_result(f), {})
        self.assertEqual(len(result['unannotated_findings']), 1)

    def test_empty_findings(self):
        result = diff_results(self._make_result([]), self._make_result([]), {})
        self.assertFalse(result['changed'])


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
