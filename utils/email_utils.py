import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

load_dotenv()

from_email = os.getenv("FROM_EMAIL")
smtp_password = os.getenv("SMTP_PASSWORD")
from_email = os.environ.get("FROM_EMAIL")
smtp_password = os.environ.get("SMTP_PASSWORD")
smtp_server = "smtp.gmail.com"
smtp_port = 465


def send_job_email(
    to_email,
    jobs_list,
):
    content = create_job_html_template(jobs_list, to_email)
    subject = get_email_subject(len(jobs_list))
    send_email(to_email, content, subject   )

def send_email(
    to_email,
    content,
    subject=None,
    attachments=None,
):
    # Create a MIMEMultipart message
    message = MIMEMultipart("alternative")
    message["To"] = to_email
    message["Subject"] = subject
    message["From"] = from_email

    # Add additional headers that can improve deliverability
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain=from_email.split("@")[1])
    message["MIME-Version"] = "1.0"
    message["X-Priority"] = "3"  # Normal priority
    message["X-Mailer"] = "Python Email Client"

    # Optional but recommended headers
    message["Reply-To"] = from_email
    message["Return-Path"] = from_email

    # Attach plain text and HTML versions of the message
    # message.attach(MIMEText(text_content, "plain"))
    message.attach(MIMEText(content, "html"))

    # Attach files if any
    if attachments:
        for attachment in attachments:
            filename = attachment.filename
            try:
                attachment_data = attachment.file.read()
            except Exception as e:
                print(f"Error reading attachment: {e}")
                continue  # Skip this attachment on error
            else:
                attachment_mime = MIMEApplication(attachment_data)
                attachment_mime.add_header(
                    "Content-Disposition", f"attachment; filename={filename}"
                )
                message.attach(attachment_mime)

    # Modified SMTP connection and sending with more detailed error handling
    try:
        smtp = smtplib.SMTP_SSL(smtp_server, smtp_port)
        smtp.login(from_email, smtp_password)
        smtp.send_message(message)

    except Exception as e:
        print(f"Failed to send email: {e}")
        raise
    finally:
        smtp.quit()

def get_email_subject(jobs_count):
    """Generate a random, engaging subject line based on the number of jobs"""
    
    subjects = {
        "standard": [
            f"🎯 {jobs_count} Job Opportunities Matched Your Profile",
            f"📋 Your Personalized Job Matches ({jobs_count} New Positions)",
            f"✨ {jobs_count} New Job Opportunities Just for You",
            "🚀 Your Curated Job Recommendations Are Here",
            "💼 Today's Handpicked Job Opportunities",
            f"📊 {jobs_count} Jobs That Match Your Expertise",
            "🌟 Your Daily Career Opportunities",
            f"💡 {jobs_count} Positions You Might Be Interested In",
            "🎪 Fresh Job Matches Just Arrived",
            "📬 Your Personalized Job Alert"
        ],
        "urgent": [
            "🔥 Hot Job Opportunities - Perfect Matches Found",
            "⚡ Immediate Job Openings Matching Your Skills",
            "🎯 Prime Job Matches - Quick Application Recommended",
            "⏰ Time-Sensitive Opportunities Available Now"
        ],
        "weekly": [
            "📊 Your Weekly Job Market Update",
            f"📈 This Week's Top {jobs_count} Job Matches",
            "🗓️ Your Weekly Career Opportunities Digest",
            "📅 Weekly Job Roundup Just for You"
        ]
    }
    
    # Combine all subject types with weights
    # Standard subjects have higher chance of being selected
    weighted_subjects = (
        subjects["standard"] * 3 +  # More weight to standard subjects
        subjects["urgent"] +        # Less weight to urgent
        subjects["weekly"]         # Less weight to weekly
    )
    
    return random.choice(weighted_subjects)


def create_job_html_template(jobs_list, to_email):
    # Add more CSS styles
    styles = """
        <style>
            /* Existing styles... */
            
            /* New header and footer styles */
            .header {
                background-color: #2c3e50;
                color: white;
                padding: 30px 20px;
                text-align: center;
                border-radius: 8px 8px 0 0;
                margin-bottom: 30px;
            }
            .company-logo {
                max-width: 150px;
                margin-bottom: 15px;
            }
            .header h1 {
                margin: 0;
                color: white;
                font-size: 28px;
            }
            .header p {
                margin: 10px 0 0 0;
                color: #ecf0f1;
            }
            .footer {
                background-color: #34495e;
                color: white;
                padding: 30px 20px;
                text-align: center;
                border-radius: 0 0 8px 8px;
                margin-top: 30px;
            }
            .social-links {
                margin: 20px 0;
            }
            .social-links a {
                color: white;
                text-decoration: none;
                margin: 0 10px;
            }
            .footer-info {
                font-size: 12px;
                color: #bdc3c7;
            }
            .unsubscribe {
                color: #bdc3c7;
                text-decoration: none;
                font-size: 12px;
            }
            .unsubscribe:hover {
                color: white;
            }
        </style>
    """

    # Email template with header and footer
    html_content = f"""
    <html>
    <head>{styles}</head>
    <body style="margin: 0; padding: 20px; background-color: #f5f6fa; font-family: Arial, sans-serif;">
        <div style="max-width: 800px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
            <!-- Header -->
            <div class="header">
                <h1>Job Match Alert</h1>
                <p>We've found {len(jobs_list)} job opportunities matching your profile</p>
            </div>

            <!-- Main Content -->
            <div style="padding: 0 20px;">
                <p style="text-align: center; color: #7f8c8d; margin-bottom: 30px;">
                    Hello! Here are the latest job opportunities that match your skills and preferences.
                </p>
    """

    # Add jobs (existing code)
    for job in jobs_list:
        html_content += f"""
        <div class="job-container">
            <div class="job-title">
                <h2 style="margin: 0; color: #2c3e50;">{job['job_title']}</h2>
            </div>
            
            <div class="company-info" style="margin: 10px 0;">
                <i style="color: #7f8c8d;">{job['company_info']}</i>
            </div>
            
            <div class="location-salary" style="margin: 15px 0;">
                <span style="margin-right: 20px;">
                    <i class="fas fa-map-marker-alt"></i> Location: {job['location']}
                </span>
                <span>
                    <i class="fas fa-money-bill"></i> Salary: {job['salary_range']}
                </span>
            </div>

            <div class="section">
                <h3 style="color: #2980b9; margin: 15px 0 10px;">Job Description</h3>
                <p style="margin: 0; line-height: 1.6;">{job['job_description']}</p>
            </div>

            <div class="section">
                <h3 style="color: #2980b9; margin: 15px 0 10px;">Key Responsibilities</h3>
                <ul style="margin: 0; padding-left: 20px;">
                    {' '.join(f'<li style="margin: 5px 0;">{resp}</li>' for resp in job['responsibilities'])}
                </ul>
            </div>

            <div class="section">
                <h3 style="color: #2980b9; margin: 15px 0 10px;">Required Skills</h3>
                <ul style="margin: 0; padding-left: 20px;">
                    {' '.join(f'<li style="margin: 5px 0;">{skill}</li>' for skill in job['required_skills'])}
                </ul>
            </div>

            <div class="section">
                <h3 style="color: #2980b9; margin: 15px 0 10px;">Qualifications</h3>
                <ul style="margin: 0; padding-left: 20px;">
                    {' '.join(f'<li style="margin: 5px 0;">{qual}</li>' for qual in job['qualifications'])}
                </ul>
            </div>

            <div class="section">
                <h3 style="color: #2980b9; margin: 15px 0 10px;">Keywords</h3>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                    {' '.join(f'<span style="background-color: #e1f5fe; padding: 5px 10px; border-radius: 15px; font-size: 12px;">{keyword}</span>' for keyword in job['keywords'])}
                </div>
            </div>

            <div style="margin-top: 20px; text-align: center;">
                <a href="#" style="
                    display: inline-block;
                    background-color: #2980b9;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 10px;">
                    Apply Now
                </a>
            </div>

            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
        </div>
        """

    # Add footer
    html_content += f"""
            </div>
            <!-- Footer -->
            <div class="footer">
                <div style="margin-bottom: 20px;">
                    <strong style="font-size: 18px;">Stay Connected</strong>
                    <div class="social-links">
                        <a href="https://linkedin.com/company/your-company">LinkedIn</a> |
                        <a href="https://twitter.com/your-company">Twitter</a> |
                        <a href="https://your-company.com">Website</a>
                    </div>
                </div>
                
                <div class="footer-info">
                    <p>Solve Byte<br>
                    123 Lagos Nigeria<br>
                    solvebyet@gmail.com</p>
                    
                    <p>© 2024 Solve Byte. All rights reserved.</p>
                    
                    <p>This email was sent to {to_email} because you subscribed to job alerts.<br>
                    <a href="#" class="unsubscribe">Unsubscribe</a> | 
                    <a href="#" class="unsubscribe">Update Preferences</a></p>
                </div>
            </div>
        </div>
        
        <!-- Mobile responsiveness note -->
        <div style="text-align: center; margin-top: 20px; font-size: 12px; color: #7f8c8d;">
            This email looks better in your preferred email client.
        </div>
    </body>
    </html>
    """

    return html_content
