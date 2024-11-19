import uuid
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage
from appwrite.services.users import Users
from appwrite.id import ID
from appwrite.query import Query
from typing import Dict, List, Optional, Union, Any
import os
from dotenv import load_dotenv
import asyncio
from appwrite.id import ID
from concurrent.futures import ThreadPoolExecutor
import logging
from datetime import datetime

load_dotenv()


class AppwriteClient:
    def __init__(
        self,
        project_id: str = os.getenv("APPWRITE_PROJECT_ID"),
        api_key: str = os.getenv("APP_WRITE_API_KEY"),
        endpoint: str = os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1"),
        database_id: str = os.getenv("APPWRITE_DATABASE_ID"),
    ):
        """
        Initialize Appwrite client with credentials

        Args:
            project_id: Appwrite project ID
            api_key: Appwrite API key
            endpoint: Appwrite endpoint URL
            database_id: Default database ID
        """
        self.client = Client()
        self.client.set_project(project_id)
        self.client.set_key(api_key)
        self.client.set_endpoint(endpoint)

        self.database = Databases(self.client)
        self.storage = Storage(self.client)
        self.users = Users(self.client)
        self.database_id = database_id
        self.initialize_collection(["jobs", "users", "cv_metadata"])

    def initialize_collection(self, collection_ids: List[str]):
        """
        Initialize basic collections if they don't exist
        """
        try:
            response = self.database.list_collections(self.database_id)
            existing_collections = [collection['$id'] for collection in response['collections']]
            
            for collection_id in collection_ids:
                if collection_id not in existing_collections:
                    try:
                        if collection_id == "jobs":
                            self.create_jobs_schema()
                        elif collection_id == "cv_metadata":
                            self.create_cv_metadata_schema()
                        else:
                            self.database.create_collection(
                                database_id=self.database_id,
                                collection_id=collection_id,
                                name=collection_id
                            )
                            print(f"Created collection: {collection_id}")
                    except Exception as e:
                        print(f"Error creating collection {collection_id}: {e}")
                        
        except Exception as e:
            print(f"Error listing collections: {e}")

    def create_jobs_schema(self):
        """
        Create jobs collection with proper schema for job listings
        """
        try:
            # Create jobs collection
            collection = self.database.create_collection(
                database_id=self.database_id,
                collection_id="jobs",
                name="jobs"
            )
            
            # Define job attributes
            attributes = [
                {"key": "job_title", "size": 255, "required": True},
                {"key": "job_description", "size": 65535, "required": True},
                {"key": "required_skills", "size": 65535, "required": False},  # Changed to text
                {"key": "responsibilities", "size": 65535, "required": False},  # Changed to text
                {"key": "qualifications", "size": 65535, "required": False},  # Changed to text
                {"key": "location", "size": 255, "required": False},
                {"key": "salary_range", "size": 255, "required": False},
                {"key": "company_info", "size": 65535, "required": False},
                {"key": "keywords", "size": 65535, "required": False},  # Changed to text
                {"key": "email", "size": 255, "required": False}
            ]
            
            # Create each attribute
            for attr in attributes:
                if attr.get("array", False):
                    self.database.create_string_attribute(
                        database_id=self.database_id,
                        collection_id="jobs",
                        key=attr["key"],
                        size=attr["size"],
                        required=attr["required"],
                        array=True
                    )
                else:
                    self.database.create_string_attribute(
                        database_id=self.database_id,
                        collection_id="jobs",
                        key=attr["key"],
                        size=attr["size"],
                        required=attr["required"]
                    )
                
                print(f"Created attribute: {attr['key']}")
                
            print("Successfully created jobs collection with schema")
            
        except Exception as e:
            print(f"Error creating jobs schema: {e}")
            

        """
        Create user collection with proper schema for user profiles
        """
        try:
            # Create user collection
            collection = self.database.create_collection(
                database_id=self.database_id,
                collection_id="users",
                name="users"
            )
            
            # Define user attributes
            attributes = [
                {"key": "username", "size": 255, "required": True},
                {"key": "email", "size": 255, "required": True},
                {"key": "file_name", "size": 255, "required": True},
                {"key": "file_type", "size": 255, "required": True},
                {"key": "file_size", "type": "integer", "required": True},
                {"key": "text", "size": 65535, "required": True}
            ]
            
            # Create each attribute
            for attr in attributes:
                if attr.get("type") == "object":
                    # Create object attribute
                    self.database.create_object_attribute(
                        database_id=self.database_id,
                        collection_id="users",
                        key=attr["key"],
                        required=attr["required"],
                        attributes=attr["attributes"]
                    )
                elif attr.get("type") == "integer":
                    # Create integer attribute
                    self.database.create_integer_attribute(
                        database_id=self.database_id,
                        collection_id="users",
                        key=attr["key"],
                        required=attr["required"]
                    )
                else:
                    # Create string attribute
                    self.database.create_string_attribute(
                        database_id=self.database_id,
                        collection_id="users",
                        key=attr["key"],
                        size=attr["size"],
                        required=attr["required"]
                    )
                
                # logger.info(f"Created attribute: {attr['key']}")
            
            # Create indexes
            indexes = [
                {
                    "key": "email_idx",
                    "type": "key",
                    "attributes": ["email"],
                    "orders": ["ASC"]
                },
                {
                    "key": "username_idx",
                    "type": "key", 
                    "attributes": ["username"],
                    "orders": ["ASC"]
                }
            ]
            
            for index in indexes:
                self.database.create_index(
                    database_id=self.database_id,
                    collection_id="users",
                    key=index["key"],
                    type=index["type"],
                    attributes=index["attributes"],
                    orders=index["orders"]
                )
            #     logger.info(f"Created index: {index['key']}")
            
            # logger.info("Successfully created users collection with schema")
            
        except Exception as e:
            # logger.error(f"Error creating users schema: {str(e)}")
            raise

    def get_unique_id(self):
        return ID.unique()

    def create_document(
        self,
        collection_id: str,
        data: Dict[str, Any],
        document_id: str = None,
        permissions: List[str] = None,
    ) -> Dict:
        """
        Create a new document in a collection

        Args:
            collection_id: Collection ID
            data: Document data
            permissions: Document permissions
        """
        try:
            return self.database.create_document(
                database_id=self.database_id,
                collection_id=collection_id,
                data=data,
                document_id=document_id,
                permissions=permissions,
            )
        except Exception as e:
            print(f"Error creating document: {e}")
            raise

    async def get_document(self, collection_id: str, document_id: str) -> Dict:
        """
        Get a document by ID

        Args:
            collection_id: Collection ID
            document_id: Document ID
        """
        try:
            return await self.database.get_document(
                database_id=self.database_id,
                collection_id=collection_id,
                document_id=document_id,
            )
        except Exception as e:
            print(f"Error getting document: {e}")
            raise

    async def update_document(
        self,
        collection_id: str,
        document_id: str,
        data: Dict[str, Any],
        permissions: List[str] = None,
    ) -> Dict:
        """
        Update an existing document

        Args:
            collection_id: Collection ID
            document_id: Document ID
            data: Updated document data
            permissions: Updated permissions
        """
        try:
            return await self.database.update_document(
                database_id=self.database_id,
                collection_id=collection_id,
                document_id=document_id,
                data=data,
                permissions=permissions,
            )
        except Exception as e:
            print(f"Error updating document: {e}")
            raise

    async def delete_document(self, collection_id: str, document_id: str) -> Dict:
        """
        Delete a document

        Args:
            collection_id: Collection ID
            document_id: Document ID
        """
        try:
            return await self.database.delete_document(
                database_id=self.database_id,
                collection_id=collection_id,
                document_id=document_id,
            )
        except Exception as e:
            print(f"Error deleting document: {e}")
            raise

    async def list_documents(
        self,
        collection_id: str,
        queries: List[str] = None,
        limit: int = 25,
        offset: int = 0,
        cursor: str = None,
        cursor_direction: str = None,
        order_attributes: List[str] = None,
        order_types: List[str] = None,
    ) -> Dict:
        """
        List documents with optional filtering

        Args:
            collection_id: Collection ID
            queries: List of query strings
            limit: Number of documents to return
            offset: Number of documents to skip
            cursor: ID of the document to start from
            cursor_direction: Direction of the cursor (before/after)
            order_attributes: Attributes to order by
            order_types: Order types (ASC/DESC)
        """
        try:
            return await self.database.list_documents(
                database_id=self.database_id,
                collection_id=collection_id,
                queries=queries,
                limit=limit,
                offset=offset,
                cursor=cursor,
                cursor_direction=cursor_direction,
                order_attributes=order_attributes,
                order_types=order_types,
            )
        except Exception as e:
            print(f"Error listing documents: {e}")
            raise

    async def query_documents(
        self, collection_id: str, filters: List[Dict[str, Any]], limit: int = 25
    ) -> List[Dict]:
        """
        Query documents with filters

        Args:
            collection_id: Collection ID
            filters: List of filter conditions
            limit: Number of documents to return

        Example filters:
            [
                {"field": "name", "operator": "equal", "value": "John"},
                {"field": "age", "operator": "greater", "value": 18}
            ]
        """
        try:
            queries = []
            for filter in filters:
                query = Query.equal(filter["field"], filter["value"])
                if filter["operator"] == "greater":
                    query = Query.greater(filter["field"], filter["value"])
                elif filter["operator"] == "less":
                    query = Query.lesser(filter["field"], filter["value"])
                elif filter["operator"] == "contains":
                    query = Query.search(filter["field"], filter["value"])
                queries.append(query)

            return await self.database.list_documents(
                database_id=self.database_id,
                collection_id=collection_id,
                queries=queries,
                limit=limit,
            )
        except Exception as e:
            print(f"Error querying documents: {e}")
            raise

    async def upload_file(
        self, bucket_id: str, file_path: str, permissions: List[str] = None
    ) -> Dict:
        """
        Upload a file to storage

        Args:
            bucket_id: Storage bucket ID
            file_path: Path to file
            permissions: File permissions
        """
        try:
            with open(file_path, "rb") as file:
                return await self.storage.create_file(
                    bucket_id=bucket_id, file=file, permissions=permissions
                )
        except Exception as e:
            print(f"Error uploading file: {e}")
            raise

    def get_file(
        self, bucket_id: str, file_id: str, permissions: List[str] = None
    ) -> Dict:
        try:
            return self.storage.get_file(bucket_id=bucket_id, file_id=file_id)
        except Exception as e:
            print(f"Error getting file: {e}")
            raise

    async def delete_file(self, bucket_id: str, file_id: str) -> Dict:
        """
        Delete a file from storage

        Args:
            bucket_id: Storage bucket ID
            file_id: File ID
        """
        try:
            return await self.storage.delete_file(bucket_id=bucket_id, file_id=file_id)
        except Exception as e:
            print(f"Error deleting file: {e}")
            raise

    def create_user(self, email: str, password: str, name: str = None) -> Dict:
        """
        Create a new user

        Args:
            email: User email
            password: User password
            name: User name (optional)
        """
        try:
            return self.users.create_bcrypt_user(
                user_id=str(uuid.uuid4()), email=email, password=password, name=name
            )
        except Exception as e:
            print(f"Error creating user: {e}")
            raise

    async def get_user(self, user_id: str) -> Dict:
        """
        Get user by ID

        Args:
            user_id: User ID
        """
        try:
            return await self.users.get(user_id)
        except Exception as e:
            print(f"Error getting user: {e}")
            raise

    async def bulk_create(
        self,
        collection_id: str,
        documents: List[Dict[str, Any]],
        batch_size: int = 100,
        max_retries: int = 3,
        permissions: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Bulk create documents with batching and retry logic

        Args:
            collection_id: Collection ID
            documents: List of documents to create
            batch_size: Number of documents per batch
            max_retries: Maximum number of retry attempts
            permissions: Document permissions

        Returns:
            Dict containing results and errors if any
        """
        results = {
            "successful": [],
            "failed": [],
            "total": len(documents),
            "start_time": datetime.now(),
        }

        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(documents) + batch_size - 1) // batch_size

            logging.info(f"Processing batch {batch_num}/{total_batches}")

            # Create tasks for concurrent processing
            tasks = []
            for doc in batch:
                task = self._create_with_retry(
                    collection_id=collection_id,
                    data=doc,
                    permissions=permissions,
                    max_retries=max_retries,
                )
                tasks.append(task)

            # Execute batch concurrently
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for doc, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    results["failed"].append({"document": doc, "error": str(result)})
                else:
                    results["successful"].append(result)

            logging.info(f"Completed batch {batch_num}/{total_batches}")

        # Add summary statistics
        results["end_time"] = datetime.now()
        results["duration"] = (
            results["end_time"] - results["start_time"]
        ).total_seconds()
        results["success_rate"] = len(results["successful"]) / results["total"] * 100

        return results

    async def _create_with_retry(
        self,
        collection_id: str,
        data: Dict[str, Any],
        permissions: List[str] = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
    ) -> Dict:
        """
        Create document with exponential backoff retry
        """
        for attempt in range(max_retries):
            try:
                return await self.create_document(
                    collection_id=collection_id, data=data, permissions=permissions
                )
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise

                # Exponential backoff
                delay = base_delay * (2**attempt)
                logging.warning(
                    f"Attempt {attempt + 1} failed for document {data.get('id', 'unknown')}: {str(e)}. "
                    f"Retrying in {delay} seconds..."
                )
                await asyncio.sleep(delay)

    async def bulk_update(
        self,
        collection_id: str,
        documents: List[Dict[str, Any]],
        batch_size: int = 100,
        max_retries: int = 3,
        permissions: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Bulk update documents

        Args:
            collection_id: Collection ID
            documents: List of documents with their IDs
            batch_size: Number of documents per batch
            max_retries: Maximum number of retry attempts
            permissions: Document permissions
        """
        results = {
            "successful": [],
            "failed": [],
            "total": len(documents),
            "start_time": datetime.now(),
        }

        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(documents) + batch_size - 1) // batch_size

            tasks = []
            for doc in batch:
                if "$id" not in doc and "id" not in doc:
                    results["failed"].append(
                        {"document": doc, "error": "Missing document ID"}
                    )
                    continue

                doc_id = doc.get("$id") or doc.get("id")
                task = self._update_with_retry(
                    collection_id=collection_id,
                    document_id=doc_id,
                    data=doc,
                    permissions=permissions,
                    max_retries=max_retries,
                )
                tasks.append(task)

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for doc, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    results["failed"].append({"document": doc, "error": str(result)})
                else:
                    results["successful"].append(result)

        results["end_time"] = datetime.now()
        results["duration"] = (
            results["end_time"] - results["start_time"]
        ).total_seconds()
        results["success_rate"] = len(results["successful"]) / results["total"] * 100

        return results

    async def _update_with_retry(
        self,
        collection_id: str,
        document_id: str,
        data: Dict[str, Any],
        permissions: List[str] = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
    ) -> Dict:
        """Update document with retry logic"""
        for attempt in range(max_retries):
            try:
                return await self.update_document(
                    collection_id=collection_id,
                    document_id=document_id,
                    data=data,
                    permissions=permissions,
                )
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                delay = base_delay * (2**attempt)
                await asyncio.sleep(delay)

    def create_cv_metadata_schema(self):
        """
        Create cv_metadata collection with schema for CV information and user reference
        """
        try:
            # Create cv_metadata collection
            self.database.create_collection(
                database_id=self.database_id,
                collection_id="cv_metadata",
                name="CV Metadata"
            )
            
            # Define CV metadata attributes
            attributes = [
                {"key": "file_name", "size": 255, "required": True},
                {"key": "file_type", "size": 255, "required": True},
                {"key": "file_size", "type": "integer", "required": True},
                {"key": "text", "size": 65535, "required": True},
                {"key": "user_id", "size": 255, "required": True},  # Reference to user
            ]
            
            # Create each attribute
            for attr in attributes:
                if attr.get("type") == "integer":
                    self.database.create_integer_attribute(
                        database_id=self.database_id,
                        collection_id="cv_metadata",
                        key=attr["key"],
                        required=attr["required"]
                    )
                else:
                    self.database.create_string_attribute(
                        database_id=self.database_id,
                        collection_id="cv_metadata",
                        key=attr["key"],
                        size=attr["size"],
                        required=attr["required"]
                    )

            # Create indexes for quick lookups
            indexes = [
                {
                    "key": "user_id_idx",
                    "type": "key",
                    "attributes": ["user_id"],
                    "orders": ["ASC"]
                },
            ]
            
            for index in indexes:
                self.database.create_index(
                    database_id=self.database_id,
                    collection_id="cv_metadata",
                    key=index["key"],
                    type=index["type"],
                    attributes=index["attributes"],
                    orders=index["orders"]
                )
            
            print("Successfully created cv_metadata collection with schema")
            
        except Exception as e:
            print(f"Error creating cv_metadata schema: {str(e)}")
            raise


# app_write_client = AppwriteClient()
