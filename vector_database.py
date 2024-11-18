import os
from typing import Dict, List
from uuid import uuid4
import asyncio

from dotenv import load_dotenv
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from embed import EmbeddingService, EmbeddingModels

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")


class VectorDatabase:
    def __init__(
        self,
        index_name: str,
        batch_size: int = 1000,
        embedding_model: str = EmbeddingModels.COHERE_ENGLISH_V3
    ):
        self.db = []
        self._current_id = 0
        self.index_name = index_name
        self.batch_size = batch_size
        self.embedding_service = EmbeddingService(model=embedding_model)
        self.init_pinecone()

    def init_pinecone(self):
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        if not self.pc.has_index(self.index_name):
            self.pc.create_index(
                name=self.index_name,
                dimension=self.embedding_service.embedding_dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
        self.index = self.pc.Index(self.index_name)

    async def get_embeddings(self, tx: list[str]):
        try:
            if not tx or any(not isinstance(t, str) for t in tx):
                print(f"Invalid text input: {tx}")
                raise ValueError("Input must be a non-empty list of strings")

            embeddings = await self.embedding_service.batch_embed_documents(tx)

            if embeddings is None:
                print("Warning: Embeddings returned None")
                raise ValueError("Embedding generation failed")

            embeddings = [embedding["embedding"] for embedding in embeddings]
            return embeddings

        except Exception as e:
            print(f"Error generating embeddings: {e}")
            raise

    @property
    def next_id(self):
        self._current_id += 1
        return self._current_id

    def sanitize_metadata(self, metadata: dict) -> dict:
        """Convert metadata values to Pinecone-compatible types"""
        sanitized = {}
        for key, value in metadata.items():
            # Convert to string if not a basic type
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, (list, dict)):
                # Skip complex objects for now
                continue
            else:
                sanitized[key] = str(value)
        return sanitized

    async def structure_data(self, data: List[Dict] | tuple[str, dict]):
        """Structure data for Pinecone format"""
        try:
            if isinstance(data, tuple):
                text = data[0]
                metadata = self.sanitize_metadata(data[1])
                embeddings = await self.get_embeddings([text])
                return [{"id": str(uuid4()), "values": embeddings[0], "metadata": metadata}]
            else:
                text = [d["text"] for d in data]
                embeddings = await self.get_embeddings(text)
                return [
                    {
                        "id": str(uuid4()),
                        "values": embedding,
                        "metadata": self.sanitize_metadata(d["metadata"])
                    }
                    for embedding, d in zip(embeddings, data)
                ]

        except Exception as e:
            print(f"Error structuring data: {e}")
            return None

    async def upsert(
        self,
        data: List[tuple[str, dict]] | tuple[str, dict],
        force_flush: bool = False,
        namespace: str = None,
    ):
        """
        Upsert data to the database buffer
        
        Args:
            data: Either a single tuple (text, metadata) or list of tuples
            force_flush: Whether to force flush the buffer
            namespace: Namespace for the data
        """
        if isinstance(data, tuple):
            self.db.append((data, namespace))
        elif isinstance(data, list):
            self.db.extend([(d, namespace) for d in data])

        if len(self.db) >= self.batch_size or force_flush:
            await self.flush()

    def __del__(self):
        """Ensure any remaining data is flushed when the object is destroyed"""
        if self.db:
            # Create a new event loop for cleanup if necessary
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the flush operation
            loop.run_until_complete(self.flush())

    async def flush(self):
        """Flush current buffer to Pinecone if there's any data"""
        if not self.db:
            return

        try:
            namespace_groups = {}
            for data, namespace in self.db:
                if namespace not in namespace_groups:
                    namespace_groups[namespace] = []
                structured_data = await self.structure_data(data)
                if structured_data:
                    namespace_groups[namespace].extend(structured_data)

            for namespace, vectors in namespace_groups.items():
                if vectors:
                    self.index.upsert(vectors=vectors, namespace=namespace)

            self.db = []
        except Exception as e:
            print(f"Error flushing to Pinecone: {e}")
            raise

    async def query_embeddings(self, query: str):
        return await self.embedding_service.query_embeddings(query)

    async def query(
        self,
        query: str,
        top_k: int = 3,
        namespace: str = None,
        include_values: bool = False,
        include_metadata: bool = True,
        filter: dict = None,
    ):
        query_vector = self.query_embeddings(query)[0]
        return self.index.query(
            vector=query_vector,
            top_k=top_k,
            namespace=namespace,
            include_values=include_values,
            include_metadata=include_metadata,
            filter=filter,
        )


vector_db = VectorDatabase("joblm-index", batch_size=5)
# job_vector_db = VectorDatabase("job-index", batch_size=5)
# resume_vector_db = VectorDatabase("resume-index")
