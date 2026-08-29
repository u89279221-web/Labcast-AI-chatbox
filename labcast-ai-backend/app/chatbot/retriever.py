from abc import ABC, abstractmethod
import numpy as np

class Retriever(ABC):
    @abstractmethod
    def embed_and_index(self, machine_id: str, texts: list[str]) -> None:
        pass

    @abstractmethod
    def search(self, machine_id: str, query: str, top_k: int = 3) -> list[str]:
        pass

class InMemoryRetriever(Retriever):
    def __init__(self):
        self.index = {} # mapping machine_id -> {"texts": list[str], "embeddings": np.ndarray}
        self.model = None

    def _get_model(self):
        if self.model is None:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        return self.model

    def embed_and_index(self, machine_id: str, texts: list[str]) -> None:
        if not texts:
            return
        model = self._get_model()
        embeddings = model.encode(texts, convert_to_numpy=True)
        self.index[machine_id] = {
            "texts": texts,
            "embeddings": embeddings
        }

    def search(self, machine_id: str, query: str, top_k: int = 3) -> list[str]:
        if machine_id not in self.index or not self.index[machine_id]["texts"]:
            return []
        
        model = self._get_model()
        query_emb = model.encode([query], convert_to_numpy=True)[0]
        
        doc_embs = self.index[machine_id]["embeddings"]
        norms = np.linalg.norm(doc_embs, axis=1) * np.linalg.norm(query_emb)
        # Avoid division by zero
        norms[norms == 0] = 1e-10
        similarities = np.dot(doc_embs, query_emb) / norms
        
        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [self.index[machine_id]["texts"][i] for i in top_indices]

# Global singleton instance for retrieval
retriever = InMemoryRetriever()
