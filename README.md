# Technical Assessment - Microservice Object Detection

This project implements two backend microservices:

1. **UI Backend Service**: accepts image uploads from the user, forwards to AI backend, and saves outputs.
2. **AI Backend Service**: runs object detection on CPU using an open-source YOLO model and returns structured JSON.

## Architecture

- **ui-backend** (FastAPI, port 8000)
  - Endpoint `POST /detect` accepts image upload.
  - Calls AI backend (`POST /detect` on port 8001).
  - Saves:
    - boxed image (`*_boxed.jpg`)
    - corresponding JSON (`*.json`)
  - Also provides a minimal browser UI at `GET /`.

- **ai-backend** (FastAPI, port 8001)
  - Loads `yolov3u.pt` model from Ultralytics (CPU mode).
  - Performs object detection.
  - Returns detections and base64-encoded annotated image.

## Folder Structure

```text
.
├── ai-backend/
│   ├── app/
│   │   ├── detector.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── ui-backend/
│   ├── app/
│   │   ├── templates/
│   │   │   └── index.html
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── scripts/
│   ├── download_sample_image.sh
│   ├── generate_outputs.sh
│   └── package_project.sh
├── sample-inputs/
├── outputs/
├── docker-compose.yml
└── README.md
```

## Prerequisites

- Docker
- Docker Compose

## Run Instructions

1. Build and start services:
   ```bash
   docker compose up --build
   ```
2. Open UI:
   - `http://localhost:8000`
3. Upload an image and run detection.
4. Generated outputs are saved in `outputs/`:
   - boxed output image (`*_boxed.jpg`)
   - JSON file (`*.json`)

## API Usage

### UI Backend

- `GET /health`
- `GET /` (upload page)
- `POST /detect` (multipart image file)

Example:

```bash
curl -X POST "http://localhost:8000/detect" -F "file=@sample-inputs/bus.jpg"
```

### AI Backend

- `GET /health`
- `POST /detect` (multipart image file)

## Generate Sample Outputs Quickly

```bash
chmod +x scripts/*.sh
./scripts/download_sample_image.sh
./scripts/generate_outputs.sh
```

This will:
- download a sample image (`sample-inputs/bus.jpg`)
- run detection through UI backend
- save API response to `outputs/latest_response.json`
- save boxed image + JSON in `outputs/`

## Packaging for Submission

```bash
./scripts/package_project.sh
```

Creates `technical-assessment-submission.zip`.

## Notes

- This solution is configured to run on **CPU** by default.
- Default model is set with `MODEL_NAME=yolov3u.pt`.
- You can adjust confidence threshold via `CONFIDENCE_THRESHOLD` in `docker-compose.yml`.

## References

- Ultralytics YOLOv3 repository (reference requested):
  - https://github.com/ultralytics/yolov3
- Ultralytics model/runtime docs:
  - https://docs.ultralytics.com
