from fastapi import FastAPI, File, HTTPException, UploadFile

from .detector import ObjectDetector

app = FastAPI(title="AI Backend Service", version="1.0.0")
detector = ObjectDetector()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/detect")
async def detect(file: UploadFile = File(...)) -> dict:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are supported")

    try:
        image_bytes = await file.read()
        result = detector.detect(image_bytes)
        result["input_filename"] = file.filename
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Detection failed: {exc}") from exc
