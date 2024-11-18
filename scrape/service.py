from app_write import AppwriteClient
from typing import Dict, List, Any
from datetime import datetime
from appwrite.id import ID


class ScraperService(AppwriteClient):
    def __init__(self, collection_id: str = "scraper", **kwargs):
        """
        Initialize Scraper client

        Args:
            collection_id: Default collection ID for job listings
            **kwargs: Additional arguments passed to AppwriteClient
        """
        super().__init__(**kwargs)
        self.collection_id = collection_id

    def create_job_listing(
        self,
        job_title: str,
        job_description: str,
        required_skills: List[str] = None,
        responsibilities: List[str] = None,
        qualifications: List[str] = None,
        location: str = None,
        salary_range: str = None,
        company_info: str = None,
        keywords: List[str] = None,
        email: str = None,
        permissions: List[str] = None,
    ) -> Dict:
        """
        Create a new job listing

        Args:
            job_title: Title of the job
            job_description: Full job description
            required_skills: List of required skills
            responsibilities: List of job responsibilities
            qualifications: List of required qualifications
            location: Job location
            salary_range: Salary range
            company_info: Company information
            keywords: List of keywords
            email: Contact email
            permissions: Document permissions
        """
        data = {
            "jobTitle": job_title,
            "jobDescription": job_description,
            "requiredSkills": required_skills or [],
            "responsibilities": responsibilities or [],
            "qualifications": qualifications or [],
            "location": location,
            "salaryRange": salary_range,
            "companyInfo": company_info,
            "keywords": keywords or [],
            "email": email,
            "createdAt": datetime.now().isoformat(),
        }

        return self.create_document(
            collection_id=self.collection_id, data=data, permissions=permissions
        )

    async def get_job_listing(self, job_id: str) -> Dict:
        """
        Get a job listing by ID

        Args:
            job_id: Job listing ID
        """
        return await self.get_document(
            collection_id=self.collection_id, document_id=job_id
        )

    async def update_job_listing(
        self,
        job_id: str,
        job_title: str = None,
        job_description: str = None,
        required_skills: List[str] = None,
        responsibilities: List[str] = None,
        qualifications: List[str] = None,
        location: str = None,
        salary_range: str = None,
        company_info: str = None,
        keywords: List[str] = None,
        email: str = None,
        permissions: List[str] = None,
    ) -> Dict:
        """
        Update an existing job listing

        Args:
            job_id: Job listing ID
            job_title: Updated title
            job_description: Updated description
            required_skills: Updated required skills
            responsibilities: Updated responsibilities
            qualifications: Updated qualifications
            location: Updated location
            salary_range: Updated salary range
            company_info: Updated company info
            keywords: Updated keywords
            email: Updated email
            permissions: Updated permissions
        """
        data = {}
        if job_title is not None:
            data["jobTitle"] = job_title
        if job_description is not None:
            data["jobDescription"] = job_description
        if required_skills is not None:
            data["requiredSkills"] = required_skills
        if responsibilities is not None:
            data["responsibilities"] = responsibilities
        if qualifications is not None:
            data["qualifications"] = qualifications
        if location is not None:
            data["location"] = location
        if salary_range is not None:
            data["salaryRange"] = salary_range
        if company_info is not None:
            data["companyInfo"] = company_info
        if keywords is not None:
            data["keywords"] = keywords
        if email is not None:
            data["email"] = email

        data["updatedAt"] = datetime.now().isoformat()

        return await self.update_document(
            collection_id=self.collection_id,
            document_id=job_id,
            data=data,
            permissions=permissions,
        )

    async def delete_job_listing(self, job_id: str) -> Dict:
        """
        Delete a job listing

        Args:
            job_id: Job listing ID
        """
        return await self.delete_document(
            collection_id=self.collection_id, document_id=job_id
        )

    async def list_job_listings(
        self,
        queries: List[str] = None,
        limit: int = 25,
        offset: int = 0,
        order_by: str = "createdAt",
        order_type: str = "DESC",
    ) -> Dict:
        """
        List job listings with optional filtering

        Args:
            queries: List of query strings
            limit: Number of listings to return
            offset: Number of listings to skip
            order_by: Field to order by
            order_type: Order direction (ASC/DESC)
        """
        return await self.list_documents(
            collection_id=self.collection_id,
            queries=queries,
            limit=limit,
            offset=offset,
            order_attributes=[order_by],
            order_types=[order_type],
        )

    async def search_job_listings(
        self,
        keyword: str = None,
        location: str = None,
        skills: List[str] = None,
        limit: int = 25,
    ) -> List[Dict]:
        """
        Search job listings with filters

        Args:
            keyword: Keyword to search in title and description
            location: Location filter
            skills: Required skills filter
            limit: Number of results to return
        """
        filters = []

        if keyword:
            filters.extend(
                [
                    {"field": "jobTitle", "operator": "contains", "value": keyword},
                    {
                        "field": "jobDescription",
                        "operator": "contains",
                        "value": keyword,
                    },
                ]
            )

        if location:
            filters.append(
                {"field": "location", "operator": "equal", "value": location}
            )

        if skills:
            for skill in skills:
                filters.append(
                    {"field": "requiredSkills", "operator": "contains", "value": skill}
                )

        return await self.query_documents(
            collection_id=self.collection_id, filters=filters, limit=limit
        )

    async def batch_create_job_listings(
        self,
        jobs: List[Dict[str, Any]],
        batch_size: int = 100,
        max_retries: int = 3,
        permissions: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Batch create multiple job listings

        Args:
            jobs: List of job listing data dictionaries
            batch_size: Number of jobs to process per batch
            max_retries: Maximum number of retry attempts
            permissions: Document permissions

        Returns:
            Dict containing results and operation statistics
        """
        # Validate and format job data
        formatted_jobs = []
        for job in jobs:
            formatted_job = {
                "jobTitle": job.get("jobTitle") or job.get("job_title"),
                "jobDescription": job.get("jobDescription")
                or job.get("job_description"),
                "requiredSkills": job.get("requiredSkills")
                or job.get("required_skills", []),
                "responsibilities": job.get("responsibilities", []),
                "qualifications": job.get("qualifications", []),
                "location": job.get("location"),
                "salaryRange": job.get("salaryRange") or job.get("salary_range"),
                "companyInfo": job.get("companyInfo") or job.get("company_info"),
                "keywords": job.get("keywords", []),
                "email": job.get("email"),
                "createdAt": datetime.now().isoformat(),
            }
            formatted_jobs.append(formatted_job)

        return await self.bulk_create(
            collection_id=self.collection_id,
            documents=formatted_jobs,
            batch_size=batch_size,
            max_retries=max_retries,
            permissions=permissions,
        )

    def check_collection(self, collection_ids: List[str]):
        try:
            all_collections = self.database.list_collections(self.database_id)
            print(all_collections)
        except Exception as e:
            print(e)
        for collection_id in collection_ids:
            if collection_id not in all_collections:
                self.database.create_collection(collection_id)
                
    def bulk_write(
        self, 
        collection_id: str, 
        operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform bulk write operations on Appwrite documents
        """
        results = {
            "successful": [],
            "failed": [],
            "total": len(operations),
            "success_count": 0,
            "failure_count": 0
        }

        for operation in operations:
            try:
                op_type = operation.get("operation_type")
                data = operation.get("data", {})
                
                if op_type == "insert":
                    # Generate a unique ID for new documents
                    doc_id = ID.unique()  # Import ID from appwrite.id import ID
                    response = self.create_document(
                        collection_id=collection_id,
                        document_id=doc_id,  # Required in Appwrite
                        data=data
                    )
                    results["successful"].append({
                        "type": "insert",
                        "document_id": response["$id"]
                    })
                    results["success_count"] += 1

                elif op_type == "update":
                    doc_id = operation.get("document_id")
                    if not doc_id:
                        raise ValueError("document_id is required for update operations")
                        
                    response = self.update_document(
                        collection_id=collection_id,
                        document_id=doc_id,
                        data=data
                    )
                    results["successful"].append({
                        "type": "update",
                        "document_id": doc_id
                    })
                    results["success_count"] += 1

                elif op_type == "delete":
                    doc_id = operation.get("document_id")
                    if not doc_id:
                        raise ValueError("document_id is required for delete operations")
                        
                    self.delete_document(
                        collection_id=collection_id,
                        document_id=doc_id
                    )
                    results["successful"].append({
                        "type": "delete",
                        "document_id": doc_id
                    })
                    results["success_count"] += 1

                else:
                    raise ValueError(f"Invalid operation type: {op_type}")

            except Exception as e:
                results["failed"].append({
                    "operation": operation,
                    "error": str(e)
                })
                results["failure_count"] += 1
                
        return results

scrape_service = ScraperService(collection_id="jobs")
