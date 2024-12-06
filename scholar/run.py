import os
import asyncio

from .discoveryhub import DiscoveryHubScraper
from .graduate_programs import GraduateScraper, InternshipScraper
from .scholar4dev import Scholarship4Dev
from .scraper import ScholarshipScraper
from .mailer import (
    get_multiple_scholarships_template,
    get_scholarship_subject, 
    get_internship_subject
)
from utils.email_utils import send_email
from app_write import AppwriteClient
from log import logger

from dotenv import load_dotenv
from time import sleep
load_dotenv()

to_bcc = os.getenv("TO_BCC", "").split(",")
# Remove any empty strings and strip whitespace
to_bcc = [email.strip() for email in to_bcc if email.strip()]
# print(to_bcc)


__all__ = [
    "DiscoveryHubScraper",
    "GraduateScraper",
    "InternshipScraper",
    "Scholarship4Dev",
    "ScholarshipScraper",
]

db = AppwriteClient()


# async def send() -> None:
#     scholarships = await db.list_documents(
#         collection_id="internships",
#         queries=[],
#     )
#     scholars = []
#     count = 0
#     for scholarship in scholarships["documents"]:
#         scholars.append(scholarship)
#         count += 1
#         if count % 10 == 0:
#             sleep(10)
#             template = get_multiple_scholarships_template(scholars)
#             subject = get_scholarship_subject(len(scholars))
#             send_email(
#                 to_email="ecorporation903@gmail.com", 
#                 subject=subject, 
#                 content=template, 
#                 recipients=to_bcc
#             )
#             print(f"Email successfully sent with {len(scholars)} scholarships")
#             scholars = []

#     if scholars:
#         sleep(10)
#         template = get_multiple_scholarships_template(scholars)
#         subject = get_internship_subject(len(scholars))
#         send_email(
#             to_email="ecorporation903@gmail.com",
#             subject=subject,
#             content=template,
#             recipients=to_bcc
#         )
#         print(f"Final batch: Email sent with {len(scholars)} scholarships")
    
        
async def check_new_scholarships():
    scholarships = []
    s = Scholarship4Dev()
    r =await s.check_new_scholarships()

    if r:
        scholarships.extend(r)

    d = DiscoveryHubScraper()
    r = await d.check_new_scholarships()

    if r:
        scholarships.extend(r)

    if scholarships:
        if len(scholarships) > 10:
            scholarships = scholarships[:10]
        logger.info(f"Found {len(scholarships)} scholarships")
        template = get_multiple_scholarships_template(scholarships)
        subject = get_scholarship_subject(len(scholarships))
        send_email(
            to_email="ecorporation903@gmail.com",
            subject=subject,
            content=template,
            recipients=to_bcc
        )
        logger.info(f"Final batch: Email sent with {len(scholarships)} scholarships")

async def check_new_intership():
    internships = []
    g = GraduateScraper()
    r = await g.check_new_scholarships()
    if r:
        internships.extend(r)

    i = InternshipScraper()
    r = await i.check_new_scholarships()
    if r:
        internships.extend(r)

    if internships:
        if len(internships) > 10:
            internships = internships[:10]

        logger.info(f"Found {len(internships)} internships")
        template = get_multiple_scholarships_template(internships, type="internship")
        subject = get_internship_subject(len(internships))
        send_email(
            to_email="ecorporation903@gmail.com",
            subject=subject,
            content=template,
            recipients=to_bcc
        )
        logger.info(f"Final batch: Email sent with {len(internships)} internships")

async def start_checking_new_offer():
    await asyncio.gather(
        check_new_scholarships(),
        check_new_intership()
    )