#!/usr/bin/env bash
set -euo pipefail
WEEK_DIR="${1:-}"
if [[ -z "$WEEK_DIR" ]]; then
  echo "Usage: $0 week_XX" >&2
  exit 1
fi
REPORT_MD="runs/${WEEK_DIR}/report_week_${WEEK_DIR#week_}.md"
REPORT_PDF="runs/${WEEK_DIR}/report_week_${WEEK_DIR#week_}.pdf"
if [[ ! -f "$REPORT_MD" ]]; then
  echo "Missing $REPORT_MD" >&2
  exit 1
fi
if ! command -v pandoc >/dev/null 2>&1; then
  echo "pandoc is required. Install via: brew install pandoc" >&2
  exit 1
fi
pandoc "$REPORT_MD" -o "$REPORT_PDF"
echo "Wrote $REPORT_PDF"
