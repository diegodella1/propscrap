from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile

from app.config import get_settings


def ocr_health_status() -> dict[str, bool]:
    return {
        "pdftoppm_available": shutil.which("pdftoppm") is not None,
        "tesseract_available": shutil.which("tesseract") is not None,
    }


def run_pdf_ocr(file_path: str) -> tuple[str | None, str, int, float | None]:
    settings = get_settings()
    if shutil.which("pdftoppm") is None or shutil.which("tesseract") is None:
        return None, "ocr_unavailable", 0, None

    pdf_path = Path(file_path)
    if not pdf_path.exists():
        return None, "ocr_missing_file", 0, None

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_prefix = Path(tmp_dir) / "page"
        try:
            subprocess.run(
                ["pdftoppm", "-png", str(pdf_path), str(tmp_prefix)],
                check=True,
                capture_output=True,
                text=True,
                timeout=settings.ocr_pdftoppm_timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            return None, "ocr_pdftoppm_timeout", 0, None
        except subprocess.CalledProcessError:
            return None, "ocr_render_failed", 0, None

        page_texts: list[str] = []
        for image_path in sorted(Path(tmp_dir).glob("page-*.png"))[:10]:
            text = _run_tesseract(image_path)
            if text:
                page_texts.append(text)

        full_text = "\n".join(page_texts).strip()
        if not full_text:
            return None, "ocr_empty", 0, 0.20

        text_length = len(full_text)
        status = "success" if text_length >= 200 else "low_text"
        confidence = 0.62 if status == "success" else 0.35
        return full_text, status, text_length, confidence


def _run_tesseract(image_path: Path) -> str:
    settings = get_settings()
    command_options = [
        ["tesseract", str(image_path), "stdout", "-l", "spa+eng"],
        ["tesseract", str(image_path), "stdout"],
    ]
    for command in command_options:
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=settings.ocr_tesseract_timeout_seconds,
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            continue
        except subprocess.CalledProcessError:
            continue
    return ""
