# Project Documentation

## Objective

Develop a microservice-based object detection solution with:
- a UI backend to receive user images
- an AI backend to run detection and return structured JSON

## Approach Taken

1. Selected **FastAPI** for both services to keep implementation lightweight and consistent.
2. Split responsibilities:
   - UI backend: upload handling, orchestration, persistence
   - AI backend: model loading + inference only
3. Chosen detector: **Ultralytics YOLOv3 family model (`yolov3u.pt`)** with CPU execution.
4. Containerized both services with Docker and orchestrated via docker-compose.
5. Added scripts for:
   - downloading sample input image
   - running a detection request
   - packaging submission zip

## Service Communication

- UI backend receives multipart image upload.
- UI backend forwards bytes to AI backend endpoint.
- AI backend returns:
  - model metadata
  - image dimensions
  - detection list (`label`, `class_id`, `confidence`, `bbox`)
  - base64 annotated image
- UI backend persists outputs and returns structured response.

## Output Format

Per request, UI backend saves:

1. **Bounding-box image** (`*_boxed.jpg`)
2. **JSON result** (`*.json`) containing:
   - model/device metadata
   - detections list
   - image dimensions
   - saved image file name

## Reproducibility Steps

1. `docker compose up --build`
2. Browse `http://localhost:8000`
3. Upload image and trigger detection
4. Check `outputs/`

Optional automated sample run:
1. `./scripts/download_sample_image.sh`
2. `./scripts/generate_outputs.sh`

## References Used

- Requested reference repo:
  - https://github.com/ultralytics/yolov3
- Ultralytics documentation:
  - https://docs.ultralytics.com
