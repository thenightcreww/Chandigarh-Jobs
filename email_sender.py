# -*- coding: utf-8 -*-
"""
Email Sender with PDF Resume - FIXED VERSION
Updated for new column structure with Phone Number
Works with: Company | Role | Location | URL | Email | Phone | Status | Date
"""

import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import time

# Gmail API Scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET_NAME = "Job Application Tracker"
RESUME_PATH = "Manpreet Singh.pdf"

def get_gmail_service():
    """Authenticate and return Gmail API service"""
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('gmail', 'v1', credentials=creds)
    return service

def get_sheets_service():
    """Connect to Google Sheets"""
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    client = gspread.authorize(creds)
    
    # Try opening by key first, then by name
    try:
        sheet = client.open_by_key("1lX1T2Cufa-V1ulBYri_FFDgUXGii4GWgJEWkF_IuAXk")
    except:
        sheet = client.open(SHEET_NAME)
    
    return sheet

def get_config_from_sheet(sheet):
    """Get user configuration from Config tab"""
    try:
        config_ws = sheet.worksheet("Config")
        config_data = config_ws.get_all_values()
        
        config = {}
        for row in config_data[1:]:
            if len(row) >= 2:
                config[row[0]] = row[1]
        
        return config
    except Exception as e:
        print(f"   [!] Could not load config from sheet: {e}")
        # Fallback to hardcoded values
        return {
            'Your Name': 'Manpreet Singh',
            'Your Email': 'dimplebrar13@gmail.com',
            'Phone': '+91-9115813846',
            'Resume Link': 'https://drive.google.com/file/d/1cGvDyKaODzyySItWSPonjysKpYtviGrW/view?usp=sharing',
            'GitHub Link': 'https://github.com/manpreet1singh2',
            'Portfolio Link': 'https://v0-portfolio-project-idea-lake.vercel.app/',
            'LinkedIn Link': 'https://www.linkedin.com/in/manpreet-singh-84750627a/'
        }

def create_email_template(company, role, config):
    """Create personalized email for Manpreet Singh"""
    
    template = f"""Dear Hiring Manager,

I hope this email finds you well. I am writing to express my strong interest in the {role} position at {company}.

I am a Full Stack Developer with 9 months of hands-on professional experience, having worked with TryCyfer Technologies and Exotica IT Solutions. In these roles, I gained practical exposure to building production-ready applications and automation solutions in real business environments.

My experience includes:
• Developing responsive and scalable web applications using React.js, JavaScript, HTML, CSS, Bootstrap, and Tailwind CSS
• Integrating REST APIs and optimizing MySQL queries for performance
• Building automation workflows and AI-driven solutions using Python, Selenium, N8N, Make, and API integrations
• Delivering real-world projects such as Wheelstovet, mytr.ai, and AP Associate

WHY THE SWITCH:
Over the last 9 months, I have built a strong foundation while working across two companies. I am now seeking a long-term opportunity in a structured MNC environment where I can work on larger-scale systems, follow mature engineering processes, and grow consistently as a software professional.

TECHNICAL SKILLS:
• Frontend: React.js, JavaScript, HTML5, CSS3, Bootstrap, Tailwind CSS
• Backend: Python, Django, REST APIs
• Automation & AI: Python automation, Selenium, N8N, Make, AI integrations
• Database: MySQL
• Tools & Platforms: Git, GitHub, AWS (Basics), Vercel, Figma

I am particularly excited about {company}'s work and believe my combination of development skills and automation expertise would be valuable to your team.

Resume: Attached (also available at {config.get('Resume Link', 'N/A')})
GitHub: {config.get('GitHub Link', 'N/A')}
LinkedIn: {config.get('LinkedIn Link', 'N/A')}
Portfolio: {config.get('Portfolio Link', 'N/A')}

I would welcome the opportunity to discuss how my skills align with {company}'s needs. I am available for an interview at your earliest convenience.

Thank you for considering my application. I look forward to hearing from you.

Best regards,
{config.get('Your Name', 'Manpreet Singh')}
{config.get('Phone', '+91-9115813846')}
{config.get('Your Email', 'dimplebrar13@gmail.com')}

---
If you would prefer not to receive applications via this email, please reply with "UNSUBSCRIBE".
"""
    
    return template

def create_email_with_attachment(to_email, subject, body, sender_email, resume_path):
    """Create email message with PDF attachment"""
    try:
        message = MIMEMultipart()
        message['to'] = to_email
        message['from'] = sender_email
        message['subject'] = subject
        
        msg_body = MIMEText(body, 'plain')
        message.attach(msg_body)
        
        if os.path.exists(resume_path):
            with open(resume_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            
            filename = os.path.basename(resume_path)
            part.add_header('Content-Disposition', f'attachment; filename= {filename}')
            
            message.attach(part)
            print(f"   [+] Resume attached: {filename}")
        else:
            print(f"   [!] Warning: Resume not found at {resume_path}")
            print(f"   [*] Sending email without attachment")
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw}
        
    except Exception as e:
        print(f"   [X] Error creating email: {e}")
        return None

def send_email(service, to_email, subject, body, sender_email, resume_path):
    """Send email with PDF attachment using Gmail API"""
    try:
        message = create_email_with_attachment(to_email, subject, body, sender_email, resume_path)
        
        if not message:
            return False, "Failed to create email"
        
        sent_message = service.users().messages().send(userId='me', body=message).execute()
        
        return True, "Sent successfully"
        
    except Exception as e:
        return False, str(e)

def log_email_to_sheet(sheet, company, role, email, status, error=""):
    """Log email status to Google Sheets"""
    try:
        log_ws = sheet.worksheet("Email Log")
        
        now = datetime.now()
        
        row = [
            now.strftime('%Y-%m-%d'),
            now.strftime('%H:%M:%S'),
            company,
            role,
            email,
            status,
            error
        ]
        
        log_ws.append_row(row, value_input_option="USER_ENTERED")
    except Exception as e:
        print(f"   [!] Could not log to sheet: {e}")

def update_job_status(sheet, company, status):
    """Update job status in Job Listings tab - COLUMN 7 (G)"""
    try:
        listings_ws = sheet.worksheet("Job Listings")
        
        companies = listings_ws.col_values(1)
        
        if company in companies:
            row_index = companies.index(company) + 1
            # FIXED: Column 7 (G) is Status column with Phone Number added
            listings_ws.update_cell(row_index, 7, status)
            print(f"   [+] Updated status to: {status}")
    except Exception as e:
        print(f"   [!] Could not update status: {e}")

def send_pending_emails(max_emails=10):
    """Send emails to pending companies with resume attached"""
    print("="*70)
    print("EMAIL SENDER - STARTING")
    print("="*70)
    
    # Check if resume exists
    if not os.path.exists(RESUME_PATH):
        print(f"\n[!] WARNING: Resume not found at: {RESUME_PATH}")
        print(f"   Please place 'Manpreet Singh.pdf' in the same folder as this script")
        response = input("\n   Continue without resume? (y/n): ")
        if response.lower() != 'y':
            print("\n[X] Aborting. Please add resume and try again.")
            return
    
    # Connect to services
    print("\n[*] Authenticating with Google...")
    gmail_service = get_gmail_service()
    sheet = get_sheets_service()
    config = get_config_from_sheet(sheet)
    
    print("[+] Authentication successful!")
    
    # Get pending jobs
    print("\n[*] Loading pending job applications...")
    listings_ws = sheet.worksheet("Job Listings")
    all_data = listings_ws.get_all_values()
    
    print(f"[*] Total rows in sheet: {len(all_data)}")
    
    # Debug: Show column structure
    if len(all_data) > 0:
        headers = all_data[0]
        print(f"[*] Column headers: {headers}")
        print(f"[*] Number of columns: {len(headers)}")
    
    sender_email = config.get('Your Email', 'dimplebrar13@gmail.com')
    emails_sent = 0
    emails_failed = 0
    
    print(f"\n[*] Sending as: {config.get('Your Name', 'Manpreet Singh')} <{sender_email}>")
    print(f"[*] Resume: {RESUME_PATH}")
    print(f"[*] Max emails this run: {max_emails}")
    print(f"\n{'='*70}")
    
    # FIXED: Status is now at index 6 (column G, 0-indexed)
    # Column structure: A=Company, B=Role, C=Location, D=URL, E=Email, F=Phone, G=Status, H=Date
    pending_jobs = []
    for row in all_data[1:]:  # Skip header
        if len(row) >= 7:  # Need at least 7 columns
            status = row[6].lower() if len(row) > 6 else ''  # Column G (index 6)
            if status == 'pending':
                pending_jobs.append(row)
    
    print(f"\n[+] Found {len(pending_jobs)} pending applications")
    
    if not pending_jobs:
        print("\n[!] No pending jobs found!")
        print("   Possible reasons:")
        print("   1. No jobs in sheet with Status = 'Pending'")
        print("   2. Run the job scraper first: python 1_job_scraper.py")
        print("   3. Check that column G (7th column) contains 'Pending'")
        
        # Show first few rows for debugging
        if len(all_data) > 1:
            print("\n[*] First job in sheet:")
            first_job = all_data[1]
            if len(first_job) >= 7:
                print(f"   Company: {first_job[0]}")
                print(f"   Role: {first_job[1]}")
                print(f"   Email: {first_job[4] if len(first_job) > 4 else 'N/A'}")
                print(f"   Status: {first_job[6] if len(first_job) > 6 else 'N/A'}")
        
        return
    
    for i, row in enumerate(pending_jobs, 1):
        if emails_sent >= max_emails:
            print(f"\n[!] Reached daily limit of {max_emails} emails")
            break
        
        company = row[0]
        role = row[1]
        to_email = row[4] if len(row) > 4 else ''  # Column E (Email)
        
        if not to_email or '@' not in to_email:
            print(f"\n{i}. [>] Skipping {company} - Invalid email: {to_email}")
            continue
        
        print(f"\n{i}. [*] Sending to: {company}")
        print(f"   Role: {role}")
        print(f"   Email: {to_email}")
        
        # Create personalized email
        email_content = create_email_template(company, role, config)
        subject = f"Application for {role} Position - {config.get('Your Name', 'Manpreet Singh')}"
        
        # Send email with resume
        success, message = send_email(
            gmail_service,
            to_email,
            subject,
            email_content,
            sender_email,
            RESUME_PATH
        )
        
        if success:
            print(f"   [+] Email sent successfully!")
            log_email_to_sheet(sheet, company, role, to_email, "Sent")
            update_job_status(sheet, company, "Email Sent")
            emails_sent += 1
        else:
            print(f"   [X] Failed: {message}")
            log_email_to_sheet(sheet, company, role, to_email, "Failed", message)
            update_job_status(sheet, company, "Failed")
            emails_failed += 1
        
        # Delay to avoid Gmail rate limits
        if emails_sent < max_emails:
            print(f"   [*] Waiting 5 seconds...")
            time.sleep(5)
    
    print(f"\n{'='*70}")
    print("EMAIL SENDING SUMMARY")
    print(f"{'='*70}")
    print(f"[+] Successfully sent: {emails_sent}")
    print(f"[X] Failed: {emails_failed}")
    print(f"[*] Total processed: {emails_sent + emails_failed}")
    print(f"{'='*70}")
    
    if emails_sent > 0:
        print(f"\n[+] Great! Check your Gmail 'Sent' folder to verify emails were sent.")
        print(f"[*] Check Google Sheet 'Email Log' tab for detailed records.")
    
    print("\n[+] Email sending completed!")

def main():
    """Run the email sender"""
    send_pending_emails(max_emails=10)

if __name__ == "__main__":
    main()