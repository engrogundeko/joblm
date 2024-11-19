import os
from typing import Dict
from app_write import AppwriteClient
from parser.cv_parser import parse_cv


client = AppwriteClient()


async def create_user_with_cv(
    email: str,
    cv_file_path: str,
) -> Dict:
    """
    Create a new user with CV information
    """
    cv = await parse_cv(cv_file_path)
    password = client.get_unique_id()
    try:
        file_name = cv["file_name"]
        file_type = cv["file_type"]
        file_size = cv["file_size"]
        text = cv["text"]

        # Create user first
        user_data = { 
            "user_id": client.get_unique_id(),
            "email": email,
            "password": password, 
        }
        user = client.users.create_bcrypt_user(**user_data)
        
        # Get user ID from response
        user_id = user['$id']  # Appwrite uses $id for document IDs

        # Create CV metadata with user reference
        cv_data = {
            "file_name": file_name,
            "file_type": file_type,
            "file_size": file_size,
            "text": text,
            "user_id": user_id,
        }

        # Create CV metadata document
        created_cv = client.database.create_document(
            database_id=client.database_id,
            collection_id="cv_metadata",
            document_id=client.get_unique_id(),
            data=cv_data,
        )

        return {
            "user": user,
            "cv_metadata": created_cv
        }

    except Exception as e:
        # If there's an error, try to clean up the created user
        if 'user_id' in locals():
            try:
                client.users.delete(user_id)
            except:
                pass
        raise


# create_user_with_cv(
#     "azeezogundeko19@gmail.com",
#     "Japico12@",
#     r"C:\Users\Admin\Desktop\SolveByte\jobLM\AZEEZ OGUNDEKO CV.pdf",
# )
