#!/usr/bin/env bash
set -euo pipefail

IMAGE_PATH="${1:-sample-inputs/bus.jpg}"

if [[ ! -f "$IMAGE_PATH" ]]; then
  echo "Image not found: $IMAGE_PATH"
  echo "Run: ./scripts/download_sample_image.sh"
  exit 1
fi

SUCCESS=0

for attempt in 1 2 3 4 5; do
  echo "Attempt ${attempt}: requesting detection..."
  RESPONSE=$(curl -s -X POST "http://localhost:8000/detect" -F "file=@${IMAGE_PATH}")
  echo "$RESPONSE" > outputs/latest_response.json

  if ! echo "$RESPONSE" | grep -q '"detail"'; then
    SUCCESS=1
    break
  fi
done

cat outputs/latest_response.json

if [[ "$SUCCESS" -ne 1 ]]; then
  echo
  echo "Detection request failed after retries."
  exit 1
fi

echo
echo "Detection call complete."
echo "Saved API response to outputs/latest_response.json"
echo "Boxed image and structured JSON are saved in outputs/ by ui-backend."
