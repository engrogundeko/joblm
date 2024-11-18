from typing import Optional, Dict, Any, List
import os
from datetime import datetime
from app_write import AppwriteClient
from appwrite.query import Query


class UserService(AppwriteClient):
    def __init__(
        self,
        collection_id: str = "user",
        bucket_id: str = os.getenv("APPWRITE_CV_BUCKET_ID"),
        **kwargs,
    ):
        """
        Initialize User service

        Args:
            collection_id: Collection ID for user profiles
            bucket_id: Bucket ID for CV storage
            **kwargs: Additional arguments passed to AppwriteClient
        """
        super().__init__(**kwargs)
        self.collection_id = collection_id
        self.bucket_id = bucket_id

    def _extract_text_from_cv(self, file_path: str) -> str:
        from parser.cv_parser import parse_cv

        try:
            return parse_cv(file_path)

        except Exception as e:
            # logging.error(f"Error extracting text from CV: {str(e)}")
            raise ValueError(f"Failed to extract text from CV file: {str(e)}")

    async def create_user(self, email: str, password: str, firstName: str, lastName: str) -> Dict[str, Any]:
        try:
            full_name = f"{firstName} {lastName}"
            # Create Appwrite user account
            user = await self.create_user(
                email=email, password=password, name=full_name
            )

            # Create initial profile document
            profile_data = {
                "userId": user["$id"],
                "email": email,
                "fullName": full_name,
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
            }

            profile = await self.create_document(
                collection_id=self.collection_id,
                data=profile_data,
            )

            return {
                "user": user,
                "profile": profile,
            }
        except Exception as e:
            print(f"Error creating user: {e}")
            raise

    def update_user_profile(
        self,
        user_id: str,
        phone: Optional[str] = None,
        cv_file_path: Optional[str] = None,
        preferred_locations: List[str] = None,
        job_preferences: Dict[str, Any] = None,
        permissions: List[str] = None,
    ) -> Dict[str, Any]:
        """Update user profile with additional information"""
        try:
            # Initialize CV-related variables
            resume_metadata = None
            cv_metadata = None
            cv_upload = None

            if cv_file_path:
                # Extract text from CV
                cv_metadata = self._extract_text_from_cv(cv_file_path)

                # Upload CV file
                cv_upload = self.upload_file(
                    bucket_id=self.bucket_id,
                    file_path=cv_file_path,
                    permissions=permissions,
                )
                
                # Store CV metadata
                resume_metadata = {
                    "fileId": cv_upload.get("$id"),
                    "fileName": cv_metadata["file_name"],
                    "fileType": cv_metadata["file_type"],
                    "fileSize": cv_metadata["file_size"],
                    "uploadedAt": datetime.now().isoformat(),
                }

            # Get existing profile
            profile = self.list_documents(
                collection_id=self.collection_id,
                queries=[Query.equal("userId", user_id)],
                limit=1
            )

            if not profile["documents"]:
                raise ValueError("User profile not found")

            profile_id = profile["documents"][0]["$id"]

            # Update profile data
            update_data = {
                "phone": phone,
                "cvFile": resume_metadata,
                "cvText": cv_metadata["text"] if cv_metadata else None,
                "preferredLocations": preferred_locations or [],
                "jobPreferences": job_preferences or {},
                "updatedAt": datetime.now().isoformat(),
            }

            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}

            updated_profile = self.update_document(
                collection_id=self.collection_id,
                document_id=profile_id,
                data=update_data,
                permissions=permissions,
            )

            return {
                "profile": updated_profile,
                "cv_upload": cv_upload
            }
        except Exception as e:
            print(f"Error updating profile: {e}")
            raise

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        results = self.query_documents(
            collection_id=self.collection_id,
            filters=[{"field": "userId", "operator": "equal", "value": user_id}],
            limit=1,
        )

        if not results.get("documents"):
            raise ValueError(f"No profile found for user ID: {user_id}")

        return results["documents"][0]

    async def delete_user_profile(self, user_id: str) -> Dict[str, Any]:
        try:
            # Get profile
            profile = await self.get_user_profile(user_id)

            # Delete CV if exists
            if profile.get("cvFileId"):
                await self.delete_file(self.bucket_id, profile["cvFileId"])

            # Delete profile document
            await self.delete_document(
                collection_id=self.collection_id, document_id=profile["$id"]
            )

            # Delete user account
            await self.users.delete(user_id)

            return {"success": True, "message": "User profile deleted successfully"}

        except Exception as e:
            raise

    async def search_users(
        self,
        skills: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        experience_years: Optional[int] = None,
        keywords: Optional[List[str]] = None,
        limit: int = 25,
    ) -> List[Dict[str, Any]]:
        """
        Search user profiles based on criteria
        """
        filters = []

        if skills:
            for skill in skills:
                filters.append(
                    {"field": "skills", "operator": "contains", "value": skill}
                )

        if locations:
            for location in locations:
                filters.append(
                    {
                        "field": "preferredLocations",
                        "operator": "contains",
                        "value": location,
                    }
                )

        if experience_years is not None:
            filters.append(
                {
                    "field": "experience",
                    "operator": "greater",
                    "value": experience_years,
                }
            )

        if keywords:
            for keyword in keywords:
                filters.append(
                    {"field": "fullName", "operator": "contains", "value": keyword}
                )

        return await self.query_documents(
            collection_id=self.collection_id, filters=filters, limit=limit
        )

    async def batch_update_profiles(
        self, updates: List[Dict[str, Any]], batch_size: int = 100, max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Batch update user profiles

        Args:
            updates: List of profile updates with user IDs
            batch_size: Number of updates per batch
            max_retries: Maximum retry attempts
        """
        return await self.bulk_update(
            collection_id=self.collection_id,
            documents=updates,
            batch_size=batch_size,
            max_retries=max_retries,
        )
