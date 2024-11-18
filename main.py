import asyncio
import shutil
import tempfile
from datetime import datetime
from contextlib import asynccontextmanager

from repository import repository
from agent.agent import job_chain, to_dict
from log import logger  # Import the configured logger
from queue_util.manager_queue import queue_manager
from schemas.model import ScrapeModel
from agent.scraper import ScraperAgent
from scrape.service import scrape_service

import httpx
from uvicorn import run
from fastapi import FastAPI, UploadFile, File


app = FastAPI()
scraper_agent = ScraperAgent()


@app.get("/")
def home():
    logger.info("Home endpoint accessed.")
    return "refreshed successfully"


@app.post("/user")
async def create_new_user(username: str, email: str, pdf: UploadFile = File(...)):
    # Generate a unique ID for the job
    job_id = datetime.now().strftime("%H:%M:%S")
    logger.info(f"Received request to create new user: {username} with email: {email}")

    # Create a temporary file to save the uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        shutil.copyfileobj(pdf.file, temp_file)
        temp_file_path = temp_file.name  # Get the path of the temporary file
    logger.info(f"Temporary file created at {temp_file_path} for user: {username}")

    # Enqueue the job with the temporary file path
    task = {
        "id": job_id,
        "task_type": "user",
        "task": {"user_name": username, "path": temp_file_path, "email": email},
    }
    await queue_manager.enqueue(task)
    logger.info(f"Job {job_id} enqueued for user creation.")

    return {
        "status": "Job enqueued",
        "job_id": job_id,
        "temp_file_path": temp_file_path,
    }


async def ping_server():
    endpoint = "http://127.0.0.1:8000"
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


async def start_tasks():
    while True:
        await asyncio.sleep(5)
        logger.info("Starting resume scraping and job invocation.")

        # Fetch resumes
        try:
            resumes_data = await repository.find_query("user", {})
            users = [data for data in resumes_data]
            logger.info(f"Fetched {len(users)} resumes from user collection.")
        except Exception as e:
            logger.error(f"Error fetching resumes: {e}")
            continue  # Skip to the next iteration if fetching resumes fails

        # Process each resume
        if users:
            for user in users:
                resume_txt = user["cv"]["text"]
                username = user["username"]
                await scraper_agent.process_job_info(resume_txt, user["email"])
                # logger.info(f"Processing resume for user: {username}")
                # print(f"Resume text: {resume_txt}")

                # # Try invoking job chain for each resume
                # try:
                #     job = await job_chain.ainvoke({"resume_text": resume_txt})
                #     job_task = to_dict(job)
                #     logger.info(f"Job result: {job_task}")
                # except Exception as e:
                #     logger.error(f"Error invoking job chain for {username}: {e}")
                #     continue  # Skip to the next resume if invocation fails

                # # Enqueue job for further processing
                # try:
                #     task = ScrapeModel(data=job_task["jobschema"])
                #     logger.info(f"Job {task.id} enqueued for resume scraping.")
                #     await queue_manager.enqueue(task.to_dict)
                # except Exception as e:
                #     logger.error(f"Error enqueuing job for {username}: {e}")

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
    run(app)
