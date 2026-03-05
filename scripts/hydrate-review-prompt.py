#!/usr/bin/env python3
"""hydrate-review-prompt.py — Substitute placeholders in review prompt template.

Usage: hydrate-review-prompt.py --name NAME --ext-path PATH --lint-json FILE
           --plugin-dir DIR [--diff-json FILE] [--annotations FILE]
           --template FILE

Reads the template and replaces {{PLACEHOLDER}} tokens. Outputs to stdout.
"""

import argparse
import json
import sys


def read_file(path):
    """Read file contents, return empty string if missing."""
    try:
        with open(path) as f:
            return f.read()
    except (FileNotFoundError, PermissionError):
        return ""


def main():
    parser = argparse.ArgumentParser(description="Hydrate review prompt template")
    parser.add_argument("--name", required=True, help="Extension name")
    parser.add_argument("--ext-path", required=True, help="Extension directory path")
    parser.add_argument("--lint-json", required=True, help="Path to lint results JSON")
    parser.add_argument("--plugin-dir", required=True, help="Plugin directory path")
    parser.add_argument("--diff-json", default="", help="Path to diff results JSON")
    parser.add_argument("--annotations", default="", help="Path to annotations YAML")
    parser.add_argument("--template", required=True, help="Path to prompt template")
    args = parser.parse_args()

    template = read_file(args.template)
    if not template:
        print(f"Error: cannot read template: {args.template}", file=sys.stderr)
        sys.exit(1)

    lint_json = read_file(args.lint_json)
    if not lint_json:
        print(f"Error: cannot read lint JSON: {args.lint_json}", file=sys.stderr)
        sys.exit(1)

    # Build diff section
    diff_section = ""
    if args.diff_json:
        diff_content = read_file(args.diff_json)
        if diff_content:
            diff_section = (
                "## Baseline Comparison (Diff)\n\n"
                "```json\n"
                f"{diff_content}"
                "```\n"
            )
    if not diff_section:
        diff_section = "## Baseline Comparison\n\nNo baseline comparison available.\n"

    # Build annotations section
    ann_section = ""
    if args.annotations:
        ann_content = read_file(args.annotations)
        if ann_content:
            ann_section = (
                "## Known Finding Classifications\n\n"
                "Skip findings already classified below (tp, fp, borderline, expected):\n\n"
                "```yaml\n"
                f"{ann_content}"
                "```\n"
            )
    if not ann_section:
        ann_section = "## Known Finding Classifications\n\nNo prior annotations available.\n"

    # Substitute placeholders
    output = template
    output = output.replace("{{NAME}}", args.name)
    output = output.replace("{{EXT_PATH}}", args.ext_path)
    output = output.replace("{{LINT_JSON}}", lint_json.strip())
    output = output.replace("{{DIFF_JSON_SECTION}}", diff_section)
    output = output.replace("{{ANNOTATIONS_SECTION}}", ann_section)
    output = output.replace("{{PLUGIN_DIR}}", args.plugin_dir)

    sys.stdout.write(output)


if __name__ == "__main__":
    main()
