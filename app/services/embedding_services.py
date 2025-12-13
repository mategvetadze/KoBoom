import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')
        return cls._model

    @staticmethod
    def embed_text(text: str) -> np.ndarray:
        model = EmbeddingService.get_model()
        return model.encode(text, convert_to_numpy=True)

    @staticmethod
    def cosine_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

    @staticmethod
    def find_similar_problems(query_embedding: np.ndarray, candidate_problems) -> list:
        scores = []
        for problem in candidate_problems:
            problem_emb = EmbeddingService.deserialize_embedding(problem.embedding)
            sim = EmbeddingService.cosine_similarity(query_embedding, problem_emb)
            scores.append((problem, sim))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    @staticmethod
    def serialize_embedding(emb: np.ndarray) -> bytes:
        import pickle
        return pickle.dumps(emb)

    @staticmethod
    def deserialize_embedding(emb_bytes: bytes) -> np.ndarray:
        import pickle
        return pickle.loads(emb_bytes)

