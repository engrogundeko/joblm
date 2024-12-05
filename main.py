from datetime import datetime
import os
import asyncio
from contextlib import asynccontextmanager
import tempfile
from dotenv import load_dotenv


from log import logger  # Import the configured logger
from queue_util.manager_queue import queue_manager
from agent.scraper import ScraperAgent
from schemas.model import UserModel
from services import get_all_users, get_user_resume


import httpx
from uvicorn import run
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app_write import AppwriteClient

appwrite_client = AppwriteClient()


app = FastAPI()
load_dotenv()
scraper_agent = ScraperAgent()
APP_ENDPOINT = os.getenv("JOBLM_ENDPOINT")
port = int(os.environ.get("PORT", 8000))


@app.get("/ping")
def home():
    logger.info("Home endpoint accessed.")
    return "refreshed successfully"
 
@app.get("/success", response_class=HTMLResponse)
async def serve_success_page():
    with open("success.html", "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.get("/error", response_class=HTMLResponse)
async def serve_error_page():
    with open("error.html", "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.get("/signup", response_class=HTMLResponse)
async def serve_signup_page():
    with open("signup.html", "r") as f:
        content = f.read()
    return HTMLResponse(content=content)


@app.post("/signup")
async def signup(email: str = Form(...), pdf: UploadFile = File(...)):
    try:
        print(pdf)
         # Create a unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{email}_{timestamp}.pdf"
        
        # Create file path in system's temp directory
        file_path = os.path.join(tempfile.gettempdir(), filename)
        
        # Read and save the file
        content = await pdf.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        print(f"File saved to: {file_path}")
            
        user = UserModel(email=email, file_path=file_path)
        await queue_manager.enqueue(user.to_dict)
        return RedirectResponse(url="/success", status_code=303)
    except Exception as e:
        logger.error(f"Error during signup: {str(e)}")
        return RedirectResponse(url="/error", status_code=303)


async def ping_server():
    endpoint = "https://joblm.onrender.com/ping"
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
        await asyncio.sleep(180)


async def start_queues():
    logger.info("Starting all queue tasks.")
    asyncio.create_task(queue_manager.run_all())

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
                print("===========================")
                resume_txt = get_user_resume(userId)
                if resume_txt:
                    try:
                        await scraper_agent.process_job_info(resume_txt, user["email"])
                    except Exception as e:
                        print(str(e))
                        continue

                    print("===========================")
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
    run(app, host="0.0.0.0", port=port)
