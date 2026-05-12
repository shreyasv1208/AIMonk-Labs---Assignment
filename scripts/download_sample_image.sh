#!/usr/bin/env bash
set -euo pipefail

mkdir -p sample-inputs
curl -L "https://ultralytics.com/images/bus.jpg" -o sample-inputs/bus.jpg

echo "Downloaded sample image to sample-inputs/bus.jpg"
