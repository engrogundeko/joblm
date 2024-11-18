import asyncio
from utils.email_utils import send_email

def test_email():
    to_email = "azeezogundeko19@gmail.com"  # Replace with test email address
    subject = "Test Email - Job Listings"
    
    # Sample job data
    test_jobs = [
        {
            "job_title": "Senior Python Developer",
            "company_info": "Tech Corp - Leading Software Company",
            "job_description": "We are seeking an experienced Python developer to join our team...",
            "required_skills": [
                "Python",
                "Django",
                "FastAPI",
                "PostgreSQL",
                "Docker"
            ],
            "responsibilities": [
                "Develop and maintain Python applications",
                "Write clean, maintainable code",
                "Collaborate with cross-functional teams",
                "Participate in code reviews"
            ],
            "qualifications": [
                "5+ years Python experience",
                "Bachelor's degree in Computer Science",
                "Strong problem-solving skills"
            ],
            "location": "Remote",
            "salary_range": "$120,000 - $150,000",
            "keywords": ["Python", "Django", "Remote", "Senior", "Backend"]
        },
        {
            "job_title": "Frontend React Developer",
            "company_info": "WebTech Solutions - Fast-growing Startup",
            "job_description": "Looking for a talented React developer to build modern web applications...",
            "required_skills": [
                "React",
                "JavaScript",
                "TypeScript",
                "HTML/CSS",
                "Redux"
            ],
            "responsibilities": [
                "Build responsive web applications",
                "Implement UI/UX designs",
                "Optimize application performance",
                "Write unit tests"
            ],
            "qualifications": [
                "3+ years React experience",
                "Strong JavaScript fundamentals",
                "Experience with modern frontend tools"
            ],
            "location": "Hybrid - New York",
            "salary_range": "$90,000 - $120,000",
            "keywords": ["React", "Frontend", "JavaScript", "TypeScript", "Redux"]
        }
    ]
    

    
    try:
        send_email(
            to_email=to_email,
            subject=subject,
            jobs_list=test_jobs,
            attachments=None
        )
        print("✅ Test email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending test email: {e}")

if __name__ == "__main__":
    test_email()
    import traceback
    print(traceback.format_exc()) 