from app_write import AppwriteClient
from appwrite.query import Query
from log import logger

appwrite_client = AppwriteClient()

async def get_all_users():
    """
    Get all users from Appwrite

    Args:
        limit: Maximum number of users to return (default: 100)
    """
    try:
        # List users with pagination
        users = appwrite_client.users.list()

        return users["users"]  # Returns list of user objects

    except Exception as e:
        print(f"Error getting users: {str(e)}")
        raise


def get_user_resume(userId: str):
    try:
        result = appwrite_client.database.list_documents(
            collection_id="cv_metadata",
            database_id=appwrite_client.database_id,
            queries=[Query.equal("user_id", userId)],
        )
    except Exception as e:
        logger.error(f"Error fetching resumes: {e}")

    if result and result.get("documents"):
        return result["documents"][0].get("text", "")

