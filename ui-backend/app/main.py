import base64
import json
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="UI Backend Service", version="1.0.0")
templates = Jinja2Templates(directory="app/templates")

AI_BACKEND_URL = os.getenv("AI_BACKEND_URL", "http://localhost:8001/detect")
OUTPUTS_DIR = Path(os.getenv("OUTPUTS_DIR", "/outputs"))
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def _persist_outputs(detection_result: dict[str, Any]) -> tuple[str, str]:
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    run_id = uuid.uuid4().hex[:8]

    image_filename = f"{timestamp}_{run_id}_boxed.jpg"
    json_filename = f"{timestamp}_{run_id}.json"

    image_path = OUTPUTS_DIR / image_filename
    json_path = OUTPUTS_DIR / json_filename

    annotated_bytes = base64.b64decode(detection_result["annotated_image_base64"])
    image_path.write_bytes(annotated_bytes)

    json_payload = {
        k: v
        for k, v in detection_result.items()
        if k != "annotated_image_base64"
    }
    json_payload["annotated_image_file"] = image_filename

    json_path.write_text(json.dumps(json_payload, indent=2), encoding="utf-8")
    return image_filename, json_filename


def _run_detection(file: UploadFile, raw_image: bytes) -> dict[str, Any]:
    last_error: Exception | None = None
    response: requests.Response | None = None

    for attempt in range(1, 4):
        try:
            response = requests.post(
                AI_BACKEND_URL,
                files={
                    "file": (
                        file.filename or "upload.jpg",
                        raw_image,
                        file.content_type or "application/octet-stream",
                    )
                },
                timeout=180,
            )
            break
        except requests.RequestException as exc:
            last_error = exc
            if attempt < 3:
                # AI service can need additional startup time on first model download.
                time.sleep(2)

    if response is None:
        raise HTTPException(status_code=502, detail=f"AI backend unavailable: {last_error}") from last_error

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"AI backend error: {response.text}",
        )

    return response.json()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"result": None, "error": None},
    )


@app.post("/detect")
async def detect(file: UploadFile = File(...)) -> JSONResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are supported")

    raw_image = await file.read()
    result = _run_detection(file, raw_image)
    image_filename, json_filename = _persist_outputs(result)

    response_payload = {
        k: v for k, v in result.items() if k != "annotated_image_base64"
    }
    response_payload["saved_outputs"] = {
        "annotated_image": image_filename,
        "json_file": json_filename,
    }
    return JSONResponse(content=response_payload)


@app.post("/detect-ui", response_class=HTMLResponse)
async def detect_ui(request: Request, file: UploadFile = File(...)) -> HTMLResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"result": None, "error": "Please upload an image file."},
        )

    try:
        raw_image = await file.read()
        result = _run_detection(file, raw_image)
        image_filename, json_filename = _persist_outputs(result)

        template_result = {
            "input_filename": result.get("input_filename"),
            "model": result.get("model"),
            "device": result.get("device"),
            "detections_count": result.get("detections_count", 0),
            "detections": result.get("detections", []),
            "annotated_image_base64": result.get("annotated_image_base64", ""),
            "saved_outputs": {
                "annotated_image": image_filename,
                "json_file": json_filename,
            },
        }

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"result": template_result, "error": None},
        )
    except HTTPException as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"result": None, "error": str(exc.detail)},
        )
