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
        user_list = []
        limit = 100
        offset = 0
        queries = [
            Query.limit(limit)
        ]
        # List users with pagination
        users = appwrite_client.users.list(queries=queries)
        # while True:
        #     users = appwrite_client.users.list(queries=queries)
        #     queries[1] = Query.offset(offset)
        #     offset += limit
        #     if len(users['users']) == 0:
        #         break

        #     user_list.extend(users["users"])

        # print(f"Total Users {len(user_list)}")
        return users['users']

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

