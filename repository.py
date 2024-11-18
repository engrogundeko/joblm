from pymongo import MongoClient
import asyncio

# from queue_util.manager_queue import queue_manager
from vector_database import vector_db


class MongoDBRepository:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 27017,
        db_name: str = "jobLM",
    ):
        self.operations = []
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]

    # def _enqueue(self, collection_name, operation_type, operation):
    #     # Enqueue operation details
    #     id = datetime.now().strftime("%H:%M:%S")
    #     task_data = {
    #         "collection_name": collection_name,
    #         "operation": operation,
    #     }
    #     queue_manager.enqueue(id, task_type="db", task_data=task_data)

    def insert_one(self, collection_name, document, operation_type="insert"):
        # Insert a single document into a collection
        operation = dict(type=operation_type, data=document)
        self._enqueue(collection_name, operation)

    async def find_query(self, collection_name, query, projection=None):
        # Find documents based on a query
        print(collection_name)
        self.collection = self.db[collection_name]
        qs = self.collection.find(query, projection=projection)
        return qs

    def update_one(self, collection_name, query, operation_type="update"):
        # Update a single document based on a query
        operation = dict(type=operation_type, data=query)
        self._enqueue(collection_name, operation)

    def delete_one(self, collection_name, query, operation_type="delete"):
        # Delete a single document based on a query
        operation = dict(type=operation_type, data=query)
        self._enqueue(collection_name, operation)

    async def bulk_write(self, collection_name, operations):
        # Perform multiple write operations (insert, update, delete) in bulk
        self.collection = self.db[collection_name]
        bulk_operations = [operation for operation in operations]
        self.collection.bulk_write(bulk_operations)

        # Enqueue the bulk operation details
        # self._enqueue(collection_name, "bulk_write", bulk_operations)


# Example Usage
repository = MongoDBRepository()


# async def test_pinecone_sync(collection_name: str = "job"):
#     """Test function to verify Pinecone connection and data sync"""
#     try:
#         cursor = await repository.find_query(collection_name, {})
#         doc = cursor.next()
#         if not doc:
#             print("No documents found in MongoDB")
#             return

#         # Get first 20 words
#         text = " ".join(doc.get("job_description", "").split()[:20])
        
#         # Only include simple types in metadata
#         safe_metadata = {
#             "id": str(doc.get("_id", "")),
#             "title": str(doc.get("title", "")),
#             "company": str(doc.get("company", "")),
#             # Add other fields as needed, ensuring they're simple types
#         }

#         vector_db.upsert((text, safe_metadata), namespace="test")
#         vector_db.flush()
#         print("Pinecone test successful")

#     except Exception as e:
#         print(f"Pinecone test failed: {e}")
#         raise


# asyncio.run(test_pinecone_sync())
