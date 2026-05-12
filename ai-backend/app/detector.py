import base64
import os
from threading import Lock
from typing import Any

import cv2
import numpy as np
from ultralytics import YOLO


class ObjectDetector:
    def __init__(self) -> None:
        self.model_name = os.getenv("MODEL_NAME", "yolov3u.pt")
        self.device = os.getenv("DEVICE", "cpu")
        self.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.25"))
        self._model_lock = Lock()
        self._model = YOLO(self.model_name)

    def detect(self, image_bytes: bytes) -> dict[str, Any]:
        image_np = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Invalid image file")

        with self._model_lock:
            results = self._model.predict(
                source=image,
                conf=self.confidence_threshold,
                device=self.device,
                verbose=False,
            )

        result = results[0]
        detections: list[dict[str, Any]] = []

        for box in result.boxes:
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
            confidence = float(box.conf[0].item())
            class_id = int(box.cls[0].item())
            label = result.names[class_id]

            detections.append(
                {
                    "label": label,
                    "class_id": class_id,
                    "confidence": round(confidence, 4),
                    "bbox": {
                        "x1": round(x1, 2),
                        "y1": round(y1, 2),
                        "x2": round(x2, 2),
                        "y2": round(y2, 2),
                    },
                }
            )

        annotated = result.plot()
        ok, encoded = cv2.imencode(".jpg", annotated)
        if not ok:
            raise RuntimeError("Failed to encode annotated image")

        annotated_b64 = base64.b64encode(encoded.tobytes()).decode("utf-8")

        return {
            "model": self.model_name,
            "device": self.device,
            "image": {
                "width": int(image.shape[1]),
                "height": int(image.shape[0]),
            },
            "detections_count": len(detections),
            "detections": detections,
            "annotated_image_base64": annotated_b64,
        }
