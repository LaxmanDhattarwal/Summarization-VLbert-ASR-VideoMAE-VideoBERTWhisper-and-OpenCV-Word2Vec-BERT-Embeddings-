from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from config import DEFAULT_MODELS

logger = logging.getLogger(__name__)


class ModelManager:
    """Lazy model loader with robust fallbacks for low-resource environments."""

    def __init__(self) -> None:
        self._summarizer = None
        self._qa = None
        self._captioner = None
        self._embedder = None

    def _load_transformers_pipeline(self, task: str, model_name: str):
        from transformers import pipeline

        logger.info("Loading pipeline for task=%s model=%s", task, model_name)
        return pipeline(task, model=model_name)

    def get_summarizer(self):
        if self._summarizer is None:
            try:
                self._summarizer = self._load_transformers_pipeline(
                    "summarization", DEFAULT_MODELS["summarizer"]
                )
            except Exception as exc:
                logger.warning("Unable to load summarizer model: %s", exc)
                self._summarizer = False
        return self._summarizer

    def get_qa(self):
        if self._qa is None:
            try:
                self._qa = self._load_transformers_pipeline(
                    "question-answering", DEFAULT_MODELS["qa"]
                )
            except Exception as exc:
                logger.warning("Unable to load QA model: %s", exc)
                self._qa = False
        return self._qa

    def get_captioner(self):
        if self._captioner is None:
            try:
                self._captioner = self._load_transformers_pipeline(
                    "image-to-text", DEFAULT_MODELS["image_captioner"]
                )
            except Exception as exc:
                logger.warning("Unable to load caption model: %s", exc)
                self._captioner = False
        return self._captioner

    def get_embedder(self):
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer

                logger.info("Loading embedding model=%s", DEFAULT_MODELS["embedding"])
                self._embedder = SentenceTransformer(DEFAULT_MODELS["embedding"])
            except Exception as exc:
                logger.warning("Unable to load embedding model: %s", exc)
                self._embedder = False
        return self._embedder

    def generate_summary(self, text: str) -> str:
        if not text.strip():
            return "The uploaded paper did not contain enough extractable text for summarization."

        summarizer = self.get_summarizer()
        if summarizer:
            try:
                safe_text = text[:8000]
                output = summarizer(
                    safe_text,
                    max_length=220,
                    min_length=80,
                    do_sample=False,
                )
                if output and isinstance(output, list):
                    return output[0].get("summary_text", "").strip()
            except Exception as exc:
                logger.warning("Summarization failed. Falling back to heuristic summary. %s", exc)

        return self._fallback_summary(text)

    def answer_question(self, question: str, context: str) -> dict[str, Any]:
        qa_model = self.get_qa()
        if qa_model:
            try:
                output = qa_model(question=question, context=context)
                return {
                    "answer": output.get("answer", ""),
                    "score": float(output.get("score", 0.0)),
                }
            except Exception as exc:
                logger.warning("QA inference failed. Falling back to lexical answer. %s", exc)

        return self._fallback_answer(question, context)

    def caption_image(self, image_path: Path) -> str:
        captioner = self.get_captioner()
        if captioner:
            try:
                image = Image.open(image_path).convert("RGB")
                output = captioner(image)
                if output and isinstance(output, list):
                    first = output[0]
                    if isinstance(first, dict):
                        return first.get("generated_text", "").strip()
                return "Figure extracted from the paper."
            except Exception as exc:
                logger.warning("Image captioning failed. Using default figure description. %s", exc)

        return "Figure extracted from the paper; visual details are available in the image preview."

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 1), dtype=np.float32)

        embedder = self.get_embedder()
        if embedder:
            try:
                vectors = embedder.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
                return np.array(vectors, dtype=np.float32)
            except Exception as exc:
                logger.warning("Embedding generation failed, switching to fallback hashing. %s", exc)

        return self._hash_embeddings(texts)

    def embed_query(self, text: str) -> np.ndarray:
        vectors = self.embed_texts([text])
        return vectors[0]

    def _fallback_summary(self, text: str) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        selected = [s.strip() for s in sentences if s.strip()][:6]
        if not selected:
            return text[:400]
        return " ".join(selected)

    def _fallback_answer(self, question: str, context: str) -> dict[str, Any]:
        question_tokens = [token.lower() for token in re.findall(r"\w+", question)]
        sentences = re.split(r"(?<=[.!?])\s+", context)

        best_sentence = "I could not find a confident answer in the retrieved sections."
        best_overlap = -1

        for sentence in sentences:
            sentence_tokens = set(token.lower() for token in re.findall(r"\w+", sentence))
            overlap = sum(token in sentence_tokens for token in question_tokens)
            if overlap > best_overlap:
                best_overlap = overlap
                best_sentence = sentence.strip()

        return {"answer": best_sentence, "score": 0.25}

    def _hash_embeddings(self, texts: list[str], dimensions: int = 256) -> np.ndarray:
        vectors = np.zeros((len(texts), dimensions), dtype=np.float32)
        for index, text in enumerate(texts):
            for token in re.findall(r"\w+", text.lower()):
                token_hash = hash(token) % dimensions
                vectors[index, token_hash] += 1.0
            norm = np.linalg.norm(vectors[index])
            if norm > 0:
                vectors[index] /= norm
        return vectors
