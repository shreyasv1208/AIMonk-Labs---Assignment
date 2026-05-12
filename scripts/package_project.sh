#!/usr/bin/env bash
set -euo pipefail

ZIP_NAME="technical-assessment-submission.zip"

rm -f "$ZIP_NAME"
zip -r "$ZIP_NAME" . \
  -x "*.git*" \
  -x "__pycache__/*" \
  -x "*.pyc" \
  -x "outputs/*.jpg" \
  -x "outputs/*.json"

echo "Created $ZIP_NAME"
