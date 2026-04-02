from __future__ import annotations

from pathlib import Path

import fitz


def extract_pdf_text(file_path: str) -> tuple[str | None, str, int, float | None]:
    path = Path(file_path)
    if not path.exists():
        return None, "failed", 0, None

    try:
        with fitz.open(path) as document:
            chunks = []
            for page in document:
                chunks.append(page.get_text("text"))
    except Exception:
        return None, "failed", 0, None

    text = "\n".join(chunks).strip()
    text_length = len(text)
    if text_length < 200:
        return text or None, "low_text", text_length, 0.30
    return text, "success", text_length, 0.92
