from __future__ import annotations

import logging
import uuid
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import ALLOWED_EXTENSIONS, CORS_ORIGINS, FIGURE_DIR, MAX_CONTENT_LENGTH, UPLOAD_DIR
from services.model_manager import ModelManager
from services.pdf_processor import extract_figures, extract_text_and_chunks
from services.retriever import InMemoryDocumentStore, StoredDocument

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

model_manager = ModelManager()
doc_store = InMemoryDocumentStore()


def _allowed_file(filename: str) -> bool:
    suffix = Path(filename).suffix.lower()
    return suffix in ALLOWED_EXTENSIONS


def _as_figure_response(doc_id: str, figure_record: dict) -> dict:
    return {
        "figureId": figure_record["figure_id"],
        "page": figure_record["page"],
        "caption": figure_record.get("caption", ""),
        "url": f"/api/figures/{doc_id}/{figure_record['filename']}",
    }


@app.get("/api/health")
def health() -> tuple:
    return jsonify({"status": "ok", "service": "Explainable Multimodal Research Assistant API"}), 200


@app.post("/api/upload")
def upload_pdf() -> tuple:
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded. Please attach a PDF file."}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename. Please select a PDF."}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are supported."}), 400

    document_id = str(uuid.uuid4())
    safe_name = secure_filename(file.filename)
    pdf_filename = f"{document_id}_{safe_name}"
    pdf_path = UPLOAD_DIR / pdf_filename
    file.save(pdf_path)

    logger.info("Processing uploaded paper: %s", pdf_path)
    full_text, chunks = extract_text_and_chunks(pdf_path)
    summary = model_manager.generate_summary(full_text)

    figures = extract_figures(pdf_path, FIGURE_DIR, document_id)
    for figure in figures:
        figure_path = FIGURE_DIR / document_id / figure["filename"]
        figure["caption"] = model_manager.caption_image(figure_path)

    chunk_texts = [chunk["text"] for chunk in chunks]
    embeddings = model_manager.embed_texts(chunk_texts)

    metadata = {
        "fileName": safe_name,
        "totalChunks": len(chunks),
        "totalFigures": len(figures),
        "textCharacters": len(full_text),
    }

    doc_store.add_document(
        StoredDocument(
            document_id=document_id,
            filename=safe_name,
            summary=summary,
            chunks=chunks,
            embeddings=embeddings,
            figures=figures,
            metadata=metadata,
        )
    )

    return (
        jsonify(
            {
                "documentId": document_id,
                "summary": summary,
                "metadata": metadata,
                "figures": [_as_figure_response(document_id, item) for item in figures],
            }
        ),
        200,
    )


@app.post("/api/ask")
def ask_question() -> tuple:
    payload = request.get_json(silent=True) or {}
    document_id = payload.get("documentId", "").strip()
    question = payload.get("question", "").strip()

    if not document_id or not question:
        return jsonify({"error": "documentId and question are required."}), 400

    document = doc_store.get_document(document_id)
    if not document:
        return jsonify({"error": "Unknown documentId. Please upload your paper again."}), 404

    query_embedding = model_manager.embed_query(question)
    top_chunks = doc_store.search_chunks(document_id, query_embedding=query_embedding, top_k=4)

    if not top_chunks:
        return (
            jsonify(
                {
                    "answer": "I could not retrieve relevant sections from this paper.",
                    "confidence": 0.0,
                    "reasoningTrace": [],
                }
            ),
            200,
        )

    context = "\n\n".join(f"Page {item['page']}: {item['text']}" for item in top_chunks)
    qa_output = model_manager.answer_question(question, context)

    reasoning_trace = [
        {
            "rank": item["rank"],
            "page": item["page"],
            "retrievalScore": item["score"],
            "evidence": item["text"][:320],
        }
        for item in top_chunks
    ]

    related_figures = [
        _as_figure_response(document_id, figure)
        for figure in document.figures[:3]
    ]

    return (
        jsonify(
            {
                "answer": qa_output.get("answer", ""),
                "confidence": round(float(qa_output.get("score", 0.0)), 4),
                "reasoningTrace": reasoning_trace,
                "relatedFigures": related_figures,
            }
        ),
        200,
    )


@app.get("/api/document/<document_id>")
def get_document(document_id: str) -> tuple:
    document = doc_store.get_document(document_id)
    if not document:
        return jsonify({"error": "Document not found."}), 404

    return (
        jsonify(
            {
                "documentId": document_id,
                "fileName": document.filename,
                "summary": document.summary,
                "metadata": document.metadata,
                "figures": [_as_figure_response(document_id, item) for item in document.figures],
            }
        ),
        200,
    )


@app.get("/api/figures/<document_id>/<filename>")
def serve_figure(document_id: str, filename: str):
    directory = FIGURE_DIR / document_id
    return send_from_directory(directory=directory, path=filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
