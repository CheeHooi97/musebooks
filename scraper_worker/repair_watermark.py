"""OCR and inpaint helper for archived listing-image watermark repair.

The Go maintenance command keeps database and R2 access in one place and
communicates with this process through JSON lines. Keeping OCR in the existing
virtual environment avoids adding a second OCR runtime to the application.
"""

from __future__ import annotations

import base64
import contextlib
import io
import json
import logging
import re
import sys
from typing import Any

import cv2
import numpy as np


def _load_ocr():
    # RapidOCR logs model loading to stdout on some releases. Hide that output
    # so stdout remains a machine-readable JSON-lines protocol.
    from rapidocr import RapidOCR

    logging.disable(logging.CRITICAL)
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return RapidOCR()


OCR = _load_ocr()
MIN_PINK_CANDIDATE_PIXELS = 1000


def _compact(value: str) -> str:
    value = value.lower().replace("1", "l").replace("0", "o")
    return re.sub(r"[^a-z0-9]", "", value)


def _is_target(value: str) -> bool:
    compact = _compact(value)
    if "eshoplab" in compact:
        return True
    # OCR sometimes inserts a stray character or splits the watermark into
    # separate tokens. Keep the fallback narrow enough to avoid matching
    # ordinary listing text containing only one of the words.
    lowered = re.sub(r"[^a-z]+", " ", value.lower()).strip()
    if re.search(r"\be\s*shop\s*lab\b", lowered):
        return True
    return compact.startswith("eshop") and compact.endswith("lab") and len(compact) <= 11


def _pink_pixel_count(image: np.ndarray) -> int:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    pink = (
        (hsv[:, :, 0] >= 130)
        & (hsv[:, :, 0] <= 179)
        & (hsv[:, :, 1] >= 80)
        & (hsv[:, :, 2] >= 80)
    )
    return int(np.count_nonzero(pink))


def _box_to_list(box: Any) -> list[list[float]]:
    return [[float(point[0]), float(point[1])] for point in box]


def process(request: dict[str, Any]) -> dict[str, Any]:
    encoded = request.get("image")
    if not isinstance(encoded, str) or not encoded:
        raise ValueError("image is required")
    raw = base64.b64decode(encoded)
    array = np.frombuffer(raw, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("image could not be decoded")

    if request.get("prefilter") and _pink_pixel_count(image) < MIN_PINK_CANDIDATE_PIXELS:
        return {"matches": [], "width": int(image.shape[1]), "height": int(image.shape[0]), "fallback": "no-pink-candidate"}

    try:
        output = OCR(image, return_word_box=True, text_score=float(request.get("text_score", 0.2)))
    except Exception as error:
        # RapidOCR's detector can reject an otherwise decodable image when a
        # native resize rounds one side to zero. The only target watermark seen
        # in this archive is saturated magenta; for a failed OCR call with no
        # such pixels, safely treat it as a non-candidate. Magenta candidates
        # are rethrown so the Go runner can restart the native worker and retry.
        if "ResizeImgError" in type(error).__name__ and _pink_pixel_count(image) < MIN_PINK_CANDIDATE_PIXELS:
            return {"matches": [], "width": int(image.shape[1]), "height": int(image.shape[0]), "fallback": "no-pink-candidate"}
        raise
    boxes = getattr(output, "boxes", None)
    if boxes is None:
        boxes = []
    texts = getattr(output, "txts", None)
    if texts is None:
        texts = []
    scores = getattr(output, "scores", None)
    if scores is None:
        scores = []
    matches: list[dict[str, Any]] = []
    for index, text in enumerate(texts):
        text = str(text)
        if not _is_target(text):
            continue
        box = boxes[index] if index < len(boxes) else []
        score = float(scores[index]) if index < len(scores) else 0.0
        matches.append({"text": text, "score": score, "box": _box_to_list(box)})

    # A watermark can be returned as two or three adjacent OCR tokens. Search
    # short reading-order windows so only the target phrase gets masked.
    if not matches and texts:
        values = [str(text) for text in texts]
        for start in range(len(values)):
            for end in range(start + 2, min(len(values), start + 5) + 1):
                phrase = " ".join(values[start:end])
                if not _is_target(phrase):
                    continue
                for index in range(start, end):
                    box = boxes[index] if index < len(boxes) else []
                    score = float(scores[index]) if index < len(scores) else 0.0
                    matches.append({"text": values[index], "score": score, "box": _box_to_list(box)})
                break
            if matches:
                break

    response: dict[str, Any] = {"matches": matches, "width": int(image.shape[1]), "height": int(image.shape[0])}
    if not matches or not request.get("rewrite"):
        return response

    roi_mask = np.zeros(image.shape[:2], dtype=np.uint8)
    for match in matches:
        polygon = np.array(match["box"], dtype=np.int32)
        if polygon.size:
            cv2.fillPoly(roi_mask, [polygon], 255)

    height, width = image.shape[:2]
    # The e-shop-lab artwork is a saturated pink/magenta overlay. Masking the
    # whole OCR quadrilateral would blur the card or photograph underneath it,
    # so prefer just the colored glyph pixels and let Navier-Stokes inpainting
    # bridge those narrow strokes. Other watermark colors use the conservative
    # quadrilateral fallback.
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    pink = (
        (hsv[:, :, 0] >= 130)
        & (hsv[:, :, 0] <= 179)
        & (hsv[:, :, 1] >= 80)
        & (hsv[:, :, 2] >= 80)
        & (roi_mask > 0)
    )
    colored_mask = pink.astype(np.uint8) * 255
    colored_pixels = int(np.count_nonzero(colored_mask))
    roi_pixels = int(np.count_nonzero(roi_mask))
    if colored_pixels >= max(80, int(roi_pixels * 0.002)):
        # Keep the dilation tight. A large kernel is prone to pulling dark
        # card edges into the inpainted area when a watermark crosses a photo
        # boundary.
        expansion = 1
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (expansion * 2 + 1, expansion * 2 + 1))
        mask = cv2.dilate(colored_mask, kernel, iterations=1)
        radius = max(2, min(5, expansion + 2))
    else:
        expansion = max(2, min(12, int(round(min(height, width) * 0.012))))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (expansion * 2 + 1, expansion * 2 + 1))
        mask = cv2.dilate(roi_mask, kernel, iterations=1)
        radius = max(3, min(9, expansion + 2))
    repaired = cv2.inpaint(image, mask, radius, cv2.INPAINT_NS)

    extension = str(request.get("extension") or ".jpg").lower()
    if extension not in {".jpg", ".jpeg", ".png", ".webp"}:
        extension = ".jpg"
    params: list[int] = []
    if extension in {".jpg", ".jpeg"}:
        params = [cv2.IMWRITE_JPEG_QUALITY, 95]
    elif extension == ".webp":
        params = [cv2.IMWRITE_WEBP_QUALITY, 95]
    ok, encoded_image = cv2.imencode(extension, repaired, params)
    if not ok:
        raise ValueError(f"could not encode repaired image as {extension}")
    response["image"] = base64.b64encode(encoded_image.tobytes()).decode("ascii")
    response["content_type"] = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}[extension]
    return response


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = process(request)
            response["ok"] = True
        except Exception as error:  # keep the daemon alive for the next image
            response = {"ok": False, "error": f"{type(error).__name__}: {error}"}
        sys.stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
