import requests
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.chat_message_log import ChatMessageLog

class RetrievalService:
    """Service for advanced semantic search over chat history."""
    
    OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
    EMBEDDING_MODEL = "nomic-embed-text"

    @staticmethod
    def get_embedding(text: str) -> List[float]:
        """Generates an embedding for the given text using Ollama."""
        try:
            response = requests.post(
                RetrievalService.OLLAMA_EMBED_URL,
                json={
                    "model": RetrievalService.EMBEDDING_MODEL,
                    "prompt": text
                },
                timeout=5
            )
            if response.status_code == 200:
                return response.json().get("embedding", [])
        except requests.RequestException:
            pass
        return []

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculates cosine similarity between two vectors."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        if magnitude1 * magnitude2 == 0:
            return 0.0
        return dot_product / (magnitude1 * magnitude2)

    @staticmethod
    def search_similar_messages(db: Session, chat_config_id: str, query: str, top_k: int = 5) -> List[ChatMessageLog]:
        """
        Searches for messages semantically similar to the query.
        Note: Currently uses in-memory cosine similarity for demonstration.
        In a production environment, this should use a Vector DB (like pgvector or sqlite-vss)
        and an 'embedding' column on the ChatMessageLog table.
        """
        query_embedding = RetrievalService.get_embedding(query)
        if not query_embedding:
            # Fallback to basic text search if embeddings fail
            return db.query(ChatMessageLog).filter(
                ChatMessageLog.chat_config_id == chat_config_id,
                ChatMessageLog.message_text.ilike(f"%{query}%")
            ).order_by(ChatMessageLog.created_at.desc()).limit(top_k).all()

        # Retrieve recent history (in-memory filtering due to lack of vector column)
        # We limit to last 1000 messages to prevent memory issues
        recent_messages = db.query(ChatMessageLog).filter(
            ChatMessageLog.chat_config_id == chat_config_id
        ).order_by(ChatMessageLog.created_at.desc()).limit(1000).all()

        results = []
        for msg in recent_messages:
            # In a real scenario, msg.embedding would be pre-computed and stored in DB
            msg_embedding = RetrievalService.get_embedding(msg.message_text)
            similarity = RetrievalService.cosine_similarity(query_embedding, msg_embedding)
            results.append((similarity, msg))

        # Sort by similarity descending
        results.sort(key=lambda x: x[0], reverse=True)
        return [msg for _, msg in results[:top_k]]
