import os
from .discoveryhub import DiscoveryHubScraper
from .graduate_programs import GraduateScraper, InternshipScraper
from .scholar4dev import Scholarship4Dev
from .scraper import ScholarshipScraper
from .mailer import get_multiple_scholarships_template
from utils.email_utils import send_email
from app_write import AppwriteClient
import random

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

def get_scholarship_subject(count):
    """Generate a random, engaging subject line for scholarship notifications"""
    
    subjects = {
        "standard": [
            f"🎓 {count} New Scholarship Opportunities for You!",
            f"💰 {count} Scholarships Available - Apply Now!",
            f"✨ {count} Fresh Scholarship Opportunities Just Added",
            "🚀 Your Personalized Scholarship Matches Are Here",
            "🌟 Today's Featured Scholarship Opportunities",
            f"📚 {count} Scholarships That Match Your Profile",
            "🎯 Your Daily Scholarship Digest",
            f"💡 {count} Scholarships You Won't Want to Miss",
            "🌍 Global Scholarship Opportunities Alert",
            "📬 Your Customized Scholarship Update",
        ],
        "urgent": [
            "⚡ Urgent: Scholarship Deadlines Approaching",
            "🔥 Hot Scholarship Opportunities - Apply Today",
            "⏰ Time-Sensitive Scholarships Available Now",
            "🎯 Premium Scholarships with Upcoming Deadlines",
        ],
        "featured": [
            "🏆 Featured Full-Ride Scholarships Available",
            f"💫 This Week's Top {count} Scholarship Programs",
            "🌟 Elite Scholarship Opportunities Alert",
            "🎓 Premium International Scholarship Programs",
        ],
    }

    # Combine all subject types with weights
    weighted_subjects = (
        subjects["standard"] * 3  # More weight to standard subjects
        + subjects["urgent"]      # Less weight to urgent
        + subjects["featured"]    # Less weight to featured
    )

    return random.choice(weighted_subjects)

async def send() -> None:
    scholarships = await db.list_documents(
        collection_id="scholarships",
        queries=[],
    )
    scholars = []
    count = 0
    for scholarship in scholarships["documents"]:
        scholars.append(scholarship)
        count += 1
        if count % 10 == 0:
            sleep(10)
            template = get_multiple_scholarships_template(scholars)
            subject = get_scholarship_subject(len(scholars))
            send_email(
                to_email="ecorporation903@gmail.com", 
                subject=subject, 
                content=template, 
                recipients=to_bcc
            )
            print(f"Email successfully sent with {len(scholars)} scholarships")
            scholars = []

    if scholars:
        sleep(10)
        template = get_multiple_scholarships_template(scholars)
        subject = get_scholarship_subject(len(scholars))
        send_email(
            to_email="ecorporation903@gmail.com",
            subject=subject,
            content=template,
            recipients=to_bcc
        )
        print(f"Final batch: Email sent with {len(scholars)} scholarships")
    
        
async def check_new_scholarships():
    s = Scholarship4Dev()
    await s.check_new_scholarships()

    g = GraduateScraper()
    await g.check_new_scholarships()

    i = InternshipScraper()
    await i.check_new_scholarships()

    d = DiscoveryHubScraper()
    await d.check_new_scholarships()