from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import fitz


def _normalize_text(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned


def extract_text_and_chunks(
    pdf_path: Path,
    chunk_size: int = 900,
    overlap: int = 150,
) -> tuple[str, list[dict[str, Any]]]:
    """Extract text from each page and create retrieval-friendly overlapping chunks."""
    document = fitz.open(pdf_path)
    page_records: list[dict[str, Any]] = []
    full_text_segments: list[str] = []

    for page_index in range(len(document)):
        page = document.load_page(page_index)
        page_text = _normalize_text(page.get_text("text"))
        if not page_text:
            continue

        full_text_segments.append(page_text)
        page_records.append({"page": page_index + 1, "text": page_text})

    combined_text = "\n".join(full_text_segments)
    chunks = _build_chunks(page_records, chunk_size=chunk_size, overlap=overlap)
    return combined_text, chunks


def _build_chunks(
    page_records: list[dict[str, Any]],
    chunk_size: int,
    overlap: int,
) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    chunk_id = 1

    for record in page_records:
        text = record["text"]
        page = record["page"]

        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end]
            if chunk_text.strip():
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "page": page,
                        "text": chunk_text.strip(),
                    }
                )
                chunk_id += 1

            if end == len(text):
                break
            start = max(end - overlap, start + 1)

    return chunks


def extract_figures(
    pdf_path: Path,
    output_root: Path,
    doc_id: str,
    max_pages: int = 40,
    max_figures_per_page: int = 3,
) -> list[dict[str, Any]]:
    """Extract embedded images from PDF and save them as PNG files."""
    output_dir = output_root / doc_id
    output_dir.mkdir(parents=True, exist_ok=True)

    document = fitz.open(pdf_path)
    figures: list[dict[str, Any]] = []
    figure_index = 1

    pages_to_process = min(len(document), max_pages)

    for page_index in range(pages_to_process):
        page = document.load_page(page_index)
        image_infos = page.get_images(full=True)

        if not image_infos:
            continue

        for image_info in image_infos[:max_figures_per_page]:
            xref = image_info[0]
            pix = fitz.Pixmap(document, xref)
            if pix.n - pix.alpha > 3:
                pix = fitz.Pixmap(fitz.csRGB, pix)

            filename = f"figure_{figure_index:03d}.png"
            file_path = output_dir / filename
            pix.save(file_path)
            pix = None

            figures.append(
                {
                    "figure_id": figure_index,
                    "page": page_index + 1,
                    "filename": filename,
                    "path": str(file_path),
                }
            )
            figure_index += 1

    return figures
