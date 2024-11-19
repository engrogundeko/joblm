import asyncio
import os
import shutil
import tempfile
from datetime import datetime
from contextlib import asynccontextmanager
from dotenv import load_dotenv


from log import logger  # Import the configured logger
from queue_util.manager_queue import queue_manager

from agent.scraper import ScraperAgent
from scrape.service import scrape_service
from appwrite.query import Query

import httpx
from uvicorn import run
from fastapi import FastAPI, UploadFile, File
from app_write import AppwriteClient

appwrite_client = AppwriteClient()


app = FastAPI()
load_dotenv()
scraper_agent = ScraperAgent()
APP_ENDPOINT = os.getenv("JOBLM_ENDPOINT")

@app.get("/ping")
def home():
    logger.info("Home endpoint accessed.")
    return "refreshed successfully"




async def ping_server():
    endpoint = APP_ENDPOINT + "/ping"
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(endpoint)
            logger.info(f"Pinged {endpoint} - Status Code: {res.status_code}")
        except Exception as e:
            logger.error(f"Failed to ping {endpoint}: {e}")
    return res


async def periodic_ping():
    while True:
        await ping_server()
        await asyncio.sleep(600)


async def start_queues():
    logger.info("Starting all queue tasks.")
    asyncio.create_task(queue_manager.run_all())


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


async def start_tasks():
    while True:
        await asyncio.sleep(5)
        logger.info("Starting resume scraping and job invocation.")

        # Fetch resumes
        try:
            users = await get_all_users()
            logger.info(f"Fetched {len(users)} resumes from user collection.")
        except Exception as e:
            logger.error(f"Error fetching resumes: {e}")
            continue  # Skip to the next iteration if fetching resumes fails

        # Process each resume
        if users:
            for user in users:
                userId = user["$id"]
                print("================================")
                resume_txt = get_user_resume(userId)
                print("================================")
                if resume_txt:
                    await scraper_agent.process_job_info(resume_txt, user["email"])
                    print("================================")

                else:
                    logger.error(f"No resume found for user {userId}")

        logger.info("Completed one iteration of resume processing.")
        # Sleep for 24 hours before next batch
        await asyncio.sleep(24 * 60 * 60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting lifespan tasks.")

    try:
        ping_task = asyncio.create_task(periodic_ping())
        queue_task = asyncio.create_task(start_queues())
        start_task = asyncio.create_task(start_tasks())

    except Exception as e:
        logger.error(f"Error during startup: {e}")
        # Cancel tasks if an error occurs during startup
        ping_task.cancel()
        queue_task.cancel()
        start_task.cancel()

    yield

    # Clean up by cancelling the tasks on shutdown
    ping_task.cancel()
    queue_task.cancel()
    start_task.cancel()
    await asyncio.gather(ping_task, queue_task, start_task, return_exceptions=True)

    logger.info("Lifespan tasks cancelled on shutdown.")


app.router.lifespan_context = lifespan

if __name__ == "__main__":
    logger.info("Starting FastAPI server.")
    run(app, host="0.0.0.0", port=8000)
