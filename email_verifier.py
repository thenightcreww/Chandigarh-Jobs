# -*- coding: utf-8 -*-
"""
Email Verifier & Updater
Updates existing Google Sheet with better emails
Run this to fix old/bad emails!
"""

import gspread
from google.oauth2.credentials import Credentials
import pickle
import os
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import time

SHEET_NAME = "Job Application Tracker"

class EmailFinder:
    """Finds real company emails"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def find_company_website(self, company_name):
        """Find company website"""
        try:
            clean_name = company_name.strip().lower().replace(' ', '')
            
            domains = [
                f"https://www.{clean_name}.com",
                f"https://{clean_name}.com",
                f"https://www.{clean_name}.in",
                f"https://{clean_name}.in",
            ]
            
            for domain in domains:
                try:
                    r = requests.head(domain, headers=self.headers, timeout=5, allow_redirects=True)
                    if r.status_code < 400:
                        print(f"      [+] Found website: {domain}")
                        return domain
                except:
                    continue
            
            return None
        except:
            return None
    
    def scrape_emails(self, url):
        """Get emails from URL"""
        emails = set()
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            found = re.findall(email_pattern, response.text)
            emails.update(found)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                if 'mailto:' in link['href']:
                    email = link['href'].replace('mailto:', '').split('?')[0]
                    emails.add(email)
        except:
            pass
        
        return list(emails)
    
    def find_career_pages(self, base_url):
        """Find career pages"""
        if not base_url:
            return []
        
        patterns = ['/careers', '/career', '/jobs', '/contact', '/contact-us']
        pages = []
        
        for pattern in patterns:
            url = urljoin(base_url, pattern)
            try:
                r = requests.head(url, headers=self.headers, timeout=5)
                if r.status_code < 400:
                    pages.append(url)
            except:
                continue
        
        return pages
    
    def filter_career_email(self, emails):
        """Get best career email"""
        if not emails:
            return None
        
        priority = ['career', 'careers', 'hr', 'job', 'jobs', 'recruit', 'talent']
        exclude = ['noreply', 'no-reply', 'marketing', 'sales', 'support', 'info', 'hello']
        
        for email in emails:
            email_lower = email.lower()
            if any(word in email_lower for word in exclude):
                continue
            if any(word in email_lower for word in priority):
                return email
        
        for email in emails:
            if not any(word in email.lower() for word in exclude):
                return email
        
        return None
    
    def find_email(self, company_name):
        """Find email for company"""
        print(f"   [*] Searching email for: {company_name}")
        
        all_emails = set()
        
        website = self.find_company_website(company_name)
        
        if website:
            career_pages = self.find_career_pages(website)
            
            for page in career_pages[:2]:
                emails = self.scrape_emails(page)
                all_emails.update(emails)
                time.sleep(1)
            
            emails = self.scrape_emails(website)
            all_emails.update(emails)
        
        career_email = self.filter_career_email(list(all_emails))
        
        if career_email:
            print(f"      [+] FOUND: {career_email}")
            return career_email, "VERIFIED"
        
        print(f"      [!] No email found")
        return None, "NOT_FOUND"


def connect_to_sheet():
    """Connect to Google Sheets"""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME)
    return sheet


def update_emails_in_sheet():
    """Update all emails in Google Sheet"""
    print("="*70)
    print("EMAIL VERIFIER & UPDATER")
    print("="*70)
    
    print("\n[*] Connecting to Google Sheets...")
    sheet = connect_to_sheet()
    worksheet = sheet.worksheet("Job Listings")
    
    print("[*] Loading existing jobs...")
    all_data = worksheet.get_all_values()
    
    if len(all_data) <= 1:
        print("[!] No jobs found in sheet!")
        return
    
    print(f"[*] Found {len(all_data)-1} jobs")
    
    # Ask user what to update
    print("\n" + "="*70)
    print("What do you want to update?")
    print("1. Only emails with generic patterns (careers@company.com)")
    print("2. All emails (complete refresh)")
    print("3. Only 'Pending' jobs")
    print("="*70)
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    email_finder = EmailFinder()
    updated_count = 0
    verified_count = 0
    
    # Skip header row
    for i, row in enumerate(all_data[1:], start=2):
        if len(row) < 6:
            continue
        
        company = row[0]
        current_email = row[4] if len(row) > 4 else ""
        status = row[5] if len(row) > 5 else ""
        
        # Decide whether to update based on choice
        should_update = False
        
        if choice == "1":
            # Only update generic patterns
            if "careers@" in current_email or "hr@" in current_email:
                should_update = True
        elif choice == "2":
            # Update all
            should_update = True
        elif choice == "3":
            # Only pending jobs
            if status.lower() == "pending":
                should_update = True
        
        if not should_update:
            continue
        
        print(f"\n[{i-1}/{len(all_data)-1}] {company}")
        print(f"   Current: {current_email}")
        
        # Find better email
        new_email, status = email_finder.find_email(company)
        
        if new_email and new_email != current_email:
            print(f"   New: {new_email}")
            
            # Update in sheet
            worksheet.update_cell(i, 5, new_email)  # Column E = email
            
            if status == "VERIFIED":
                verified_count += 1
            
            updated_count += 1
            print(f"   [+] Updated!")
        else:
            print(f"   [=] No change")
        
        time.sleep(2)  # Rate limiting
    
    print("\n" + "="*70)
    print("UPDATE SUMMARY")
    print("="*70)
    print(f"[*] Total jobs checked: {len(all_data)-1}")
    print(f"[+] Emails updated: {updated_count}")
    print(f"[+] Verified real emails: {verified_count}")
    print("="*70)
    
    print("\n[+] Email verification completed!")
    print("[*] Check your Google Sheet for updated emails")


def verify_single_company():
    """Test email finder for a single company"""
    print("="*70)
    print("SINGLE COMPANY EMAIL FINDER")
    print("="*70)
    
    company_name = input("\nEnter company name: ").strip()
    
    if not company_name:
        print("[!] No company name provided")
        return
    
    email_finder = EmailFinder()
    email, status = email_finder.find_email(company_name)
    
    print(f"\n{'='*70}")
    print(f"Company: {company_name}")
    print(f"Email: {email if email else 'NOT FOUND'}")
    print(f"Status: {status}")
    print("="*70)


def main():
    """Main menu"""
    print("\n" + "="*70)
    print("EMAIL VERIFIER TOOL")
    print("="*70)
    print("\nOptions:")
    print("1. Update emails in Google Sheet")
    print("2. Test single company")
    print("3. Exit")
    print("="*70)
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        update_emails_in_sheet()
    elif choice == "2":
        verify_single_company()
    elif choice == "3":
        print("\n[*] Goodbye!")
    else:
        print("[!] Invalid choice")


if __name__ == "__main__":
    main()