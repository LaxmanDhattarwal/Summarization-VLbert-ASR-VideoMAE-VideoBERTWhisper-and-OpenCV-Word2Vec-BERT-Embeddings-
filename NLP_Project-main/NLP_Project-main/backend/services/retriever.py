from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class StoredDocument:
    document_id: str
    filename: str
    summary: str
    chunks: list[dict[str, Any]]
    embeddings: np.ndarray
    figures: list[dict[str, Any]]
    metadata: dict[str, Any]


class InMemoryDocumentStore:
    def __init__(self) -> None:
        self._documents: dict[str, StoredDocument] = {}

    def add_document(self, document: StoredDocument) -> None:
        self._documents[document.document_id] = document

    def get_document(self, document_id: str) -> StoredDocument | None:
        return self._documents.get(document_id)

    def search_chunks(
        self,
        document_id: str,
        query_embedding: np.ndarray,
        top_k: int = 4,
    ) -> list[dict[str, Any]]:
        document = self.get_document(document_id)
        if not document:
            return []

        embeddings = document.embeddings
        chunks = document.chunks

        if embeddings.size == 0 or len(chunks) == 0:
            return []

        if query_embedding.ndim > 1:
            query_embedding = query_embedding.reshape(-1)

        query_norm = np.linalg.norm(query_embedding)
        if query_norm > 0:
            query_embedding = query_embedding / query_norm

        similarity_scores = embeddings @ query_embedding
        ranked_indices = np.argsort(similarity_scores)[::-1][:top_k]

        results: list[dict[str, Any]] = []
        for rank, idx in enumerate(ranked_indices, start=1):
            idx_int = int(idx)
            chunk = chunks[idx_int]
            score = float(similarity_scores[idx_int])
            results.append(
                {
                    "rank": rank,
                    "score": round(score, 4),
                    "chunk_id": chunk["chunk_id"],
                    "page": chunk["page"],
                    "text": chunk["text"],
                }
            )

        return results
