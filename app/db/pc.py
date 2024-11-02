
from pinecone import Pinecone


class VectorDB:

    def __init__(self) -> None:
        self.pc = Pinecone(api_key="2f068841-49a0-4cf7-879c-e67be425859b")
        self.index = self.pc.Index("sachin")
    
    def insert(self, vectors):
        if isinstance(vectors, list):
            self.index.upsert(vectors=vectors)
        elif isinstance(vectors, dict):
            self.index.upsert(vectors=[vectors])
        else:
            raise ValueError("Please send as list or dict format")
    
    def search(self, vectors, top_k=5, filters={}):
        # print(vectors)
        return self.index.query(
            vector=vectors,
            top_k=top_k,
            # include_values=True,
            include_metadata=True,
        )

vector_db = VectorDB()
