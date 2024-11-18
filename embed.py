from enum import Enum
import cohere
from typing import List, Dict
import os
from dotenv import load_dotenv
from asyncio_throttle import Throttler
import logging
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()


class EmbeddingModels(str, Enum):
    """Available embedding models and their dimensions"""

    COHERE_ENGLISH_V3 = "embed-english-v3.0"  # 1024 dimensions
    COHERE_ENGLISH_LIGHT_V3 = "embed-english-light-v3.0"  # 384 dimensions
    COHERE_MULTILINGUAL_V3 = "embed-multilingual-v3.0"  # 1024 dimensions


class RateLimiter:
    def __init__(self, calls_per_minute: int = 50, calls_per_month: int = 1000):
        # Minute rate limiter: 50 calls per minute = 1 call per 1.2 seconds
        self.minute_throttler = Throttler(rate_limit=calls_per_minute, period=60)

        # Monthly rate limiter
        self.month_throttler = Throttler(
            rate_limit=calls_per_month, period=60 * 60 * 24 * 30
        )

        # Track API calls
        self.monthly_calls = 0
        self.last_reset = datetime.now()

        self.logger = logging.getLogger(__name__)

    async def acquire(self):
        """Acquire both rate limiters"""
        # Reset monthly counter if needed
        if datetime.now() - self.last_reset > timedelta(days=30):
            self.monthly_calls = 0
            self.last_reset = datetime.now()

        # Check monthly limit
        if self.monthly_calls >= 1000:
            raise Exception("Monthly API call limit reached")

        async with self.minute_throttler:
            async with self.month_throttler:
                self.monthly_calls += 1
                remaining_calls = 1000 - self.monthly_calls
                if remaining_calls < 100:
                    self.logger.warning(
                        f"Only {remaining_calls} API calls remaining this month"
                    )
                return True


class EmbeddingService:
    def __init__(
        self,
        api_key: str = os.getenv("COHERE_API_KEY"),
        model: str = EmbeddingModels.COHERE_ENGLISH_V3,
        calls_per_minute: int = 50,
        calls_per_month: int = 1000,
        max_retries: int = 3,
    ):
        self.client = cohere.Client(api_key)
        self.model = model
        self.dimension = 1024 if "light" not in model else 384
        self.rate_limiter = RateLimiter(calls_per_minute, calls_per_month)
        self.logger = logging.getLogger(__name__)
        self.max_retries = max_retries

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    async def _make_embed_call(self, texts, input_type: str):
        """Helper method to make API calls with retry logic"""
        await self.rate_limiter.acquire()
        return self.client.embed(texts=texts, model=self.model, input_type=input_type)

    async def batch_embed_documents(
        self, documents: List[str], batch_size: int = 96
    ) -> List[Dict]:
        """
        Embeds documents in batches with rate limiting

        Args:
            documents: List of texts to embed
            batch_size: Maximum number of texts per API call
        """
        embedded_documents = []
        total_batches = (len(documents) + batch_size - 1) // batch_size

        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            current_batch = (i // batch_size) + 1

            try:
                # Acquire rate limiter
                await self.rate_limiter.acquire()

                self.logger.info(f"Processing batch {current_batch}/{total_batches}")
                response = await self._make_embed_call(batch, "search_document")

                for j, embedding in enumerate(response.embeddings):
                    embedded_documents.append(
                        {
                            "text": batch[j],
                            "embedding": embedding,
                        }
                    )

                self.logger.info(f"Completed batch {current_batch}/{total_batches}")

            except Exception as e:
                self.logger.error(f"Error in batch {current_batch}: {e}")
                # Optionally retry or handle specific errors
                raise

        return embedded_documents

    async def query_embeddings(self, query: str | List[str], batch_size: int = 96):
        """
        Generate embeddings for queries with rate limiting

        Args:
            query: Single string or list of strings to embed
            batch_size: Maximum number of texts per API call
        """
        queries = [query] if isinstance(query, str) else query
        all_embeddings = []
        total_batches = (len(queries) + batch_size - 1) // batch_size

        for i in range(0, len(queries), batch_size):
            batch = queries[i : i + batch_size]
            current_batch = (i // batch_size) + 1

            try:
                # Acquire rate limiter
                await self.rate_limiter.acquire()

                self.logger.info(
                    f"Processing query batch {current_batch}/{total_batches}"
                )
                response = await self._make_embed_call(batch, "search_query")
                all_embeddings.extend(response.embeddings)

                self.logger.info(
                    f"Completed query batch {current_batch}/{total_batches}"
                )

            except Exception as e:
                self.logger.error(f"Error in query batch {current_batch}: {e}")
                raise

        return all_embeddings[0] if isinstance(query, str) else all_embeddings

    @property
    def embedding_dimension(self) -> int:
        """Get the dimension of the current embedding model"""
        return self.dimension

    def get_usage_stats(self) -> Dict:
        """Get current API usage statistics"""
        return {
            "monthly_calls": self.rate_limiter.monthly_calls,
            "remaining_calls": 1000 - self.rate_limiter.monthly_calls,
            "last_reset": self.rate_limiter.last_reset.isoformat(),
            "next_reset": (
                self.rate_limiter.last_reset + timedelta(days=30)
            ).isoformat(),
        }
