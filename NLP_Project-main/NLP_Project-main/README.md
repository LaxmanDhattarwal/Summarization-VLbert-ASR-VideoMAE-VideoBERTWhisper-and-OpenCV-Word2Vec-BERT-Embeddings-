# Explainable Multimodal Research Paper Assistant

A complete NLP + CV project with a React frontend and Flask backend.

## Core Idea

Upload a research paper PDF (text + figures) and get:
- concise paper summary
- figure-level descriptions from a ViT-based model
- question answering over paper content
- explainability output showing evidence sections used to generate each answer

## Problem Statement

Students and researchers spend significant time reading long papers and interpreting complex diagrams. Current tools usually summarize only plain text and do not clearly explain which part of the paper supports each answer.

This project asks:

How can we build a multimodal assistant that jointly understands paper text and figures and produces explainable answers with evidence traces?

## Models Used

- Figure understanding: nlpconnect/vit-gpt2-image-captioning (ViT encoder)
- Text summarization: facebook/bart-large-cnn
- Question answering: deepset/roberta-base-squad2
- Retrieval embeddings: sentence-transformers/all-MiniLM-L6-v2

## System Architecture

1. PDF upload
2. Text extraction and chunking
3. Figure extraction
4. ViT-based caption generation for figures
5. Text embedding and retrieval
6. QA with retrieved context
7. Explainability output (ranked evidence trace + page references)

## Project Structure

- backend: Flask API, model services, PDF processing
- frontend: React + Vite web UI

## Backend Setup (Windows PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Backend runs on: http://localhost:5000

## Frontend Setup (Windows PowerShell)

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Frontend runs on: http://localhost:5173

## API Endpoints

- GET /api/health
- POST /api/upload (multipart form field: file)
- POST /api/ask (JSON: documentId, question)
- GET /api/document/<document_id>
- GET /api/figures/<document_id>/<filename>

## Example Demo Flow

1. Upload a PDF paper.
2. Read generated summary and figure captions.
3. Ask: What is the main contribution of this paper?
4. Observe answer confidence and evidence trace with page references.

## Evaluation Direction

- Summarization quality: ROUGE, BLEU, METEOR
- QA quality: Exact Match, F1
- Explainability quality: human-judged evidence relevance

## Notes

- First run downloads Hugging Face models and may take time.
- If model download fails, backend falls back to lightweight heuristic behavior so the app still works.
- For large-scale deployment, replace in-memory storage with a database + vector store.
