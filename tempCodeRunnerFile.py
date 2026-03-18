# -*- coding: utf-8 -*-
"""
ULTRA Job Scraper - Gets REAL Company Contact Details
Deeply scrapes Contact Us pages for genuine phone & email
Chandigarh/Mohali Only
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

SHEET_NAME = "Job Application Tracker"

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

TARGET_LOCATIONS = ['chandigarh', 'mohali', 'tricity', 'punjab', 'panchkula', 'zirakpur']

JOB_TITLES = [
    "Prompt Engineer",
    "AI Automation Developer", 
    "Full Stack Developer",
    "Python Developer",
    "Backend Developer",
    "Project Coordinator"
]


class UltraContactFinder:
    """Ultra-powerful contact finder - gets REAL contact details"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    
    def find_company_website(self, company_name):
        """Find company website - tries multiple variations"""
        try:
            # Clean company name thoroughly
            clean = company_name.strip().lower()
            
            # Remove common business terms
            remove_words = ['pvt', 'ltd', 'limited', 'pvtltd', 'private', 'inc', 'llc', 
                          'technologies', 'technology', 'tech', 'solutions', 'services',
                          'india', 'group', 'company', 'corporation', 'corp']
            
            for word in remove_words:
                clean = re.sub(rf'\b{word}\b', '', clean, flags=re.IGNORECASE)
            
            clean = re.sub(r'[^a-z0-9]', '', clean).strip()
            
            # Try multiple domain variations
            domains = [
                f"https://www.{clean}.com",
                f"https://{clean}.com",
                f"https://www.{clean}.in",
                f"https://{clean}.in",
                f"https://www.{clean}.co.in",
                f"https://{clean}.co.in",
                f"https://www.{clean}.org",
                f"https://{clean}.io",
            ]
            
            print(f"      [*] Trying {len(domains)} domain variations...")
            
            for domain in domains:
                try:
                    response = requests.head(domain, headers=self.headers, timeout=5, allow_redirects=True)
                    if response.status_code < 400:
                        final_url = response.url
                        print(f"      [+] Found: {final_url}")
                        return final_url
                except:
                    continue
            
            print(f"      [!] No website found")
            return None
            
        except Exception as e:
            print(f"      [X] Error finding website: {e}")
            return None
    
    def deep_scrape_contact_page(self, url):
        """Deep scrape - extracts ALL contact info from page"""
        emails = set()
        phones = set()
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            html = response.text
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # =================== EMAIL EXTRACTION ===================
            
            # Pattern 1: Standard emails
            email_pattern = r'\b[A-Za-z0-9][\w\.-]*@[A-Za-z0-9][\w\.-]+\.[A-Za-z]{2,}\b'
            found_emails = re.findall(email_pattern, html)
            emails.update(found_emails)
            
            # Pattern 2: Emails with 'at' instead of @
            at_emails = re.findall(r'\b[\w\.-]+\s*\[?at\]?\s*[\w\.-]+\.\w+\b', text, re.IGNORECASE)
            for em in at_emails:
                clean_em = re.sub(r'\s*\[?at\]?\s*', '@', em, flags=re.IGNORECASE)
                if '@' in clean_em:
                    emails.add(clean_em)
            
            # Pattern 3: Emails with 'dot' instead of .
            dot_emails = re.findall(r'\b[\w-]+@[\w-]+\s+dot\s+\w+\b', text, re.IGNORECASE)
            for em in dot_emails:
                clean_em = re.sub(r'\s+dot\s+', '.', em, flags=re.IGNORECASE)
                emails.add(clean_em)
            
            # Pattern 4: mailto links
            mailto_links = soup.find_all('a', href=re.compile(r'^mailto:', re.IGNORECASE))
            for link in mailto_links:
                email = link['href'].replace('mailto:', '').split('?')[0].strip()
                emails.add(email)
            
            # Pattern 5: Check meta tags
            meta_emails = soup.find_all('meta', attrs={'content': re.compile(r'@')})
            for meta in meta_emails:
                content = meta.get('content', '')
                found = re.findall(email_pattern, content)
                emails.update(found)
            
            # =================== PHONE EXTRACTION ===================
            
            # Pattern 1: Indian numbers with +91
            phones.update(re.findall(r'\+91[-\s]?\d{10}', text))
            phones.update(re.findall(r'\+91[-\s]?\d{5}[-\s]?\d{5}', text))
            
            # Pattern 2: Landline numbers (0XXX-XXXXXXX)
            phones.update(re.findall(r'\b0\d{2,4}[-\s]?\d{6,8}\b', text))
            
            # Pattern 3: 10-digit mobile numbers
            phones.update(re.findall(r'\b[6-9]\d{9}\b', text))
            
            # Pattern 4: Numbers with parentheses
            phones.update(re.findall(r'\(\+?91\)?[-\s]?\d{10}', text))
            phones.update(re.findall(r'\(0\d{2,4}\)[-\s]?\d{6,8}', text))
            
            # Pattern 5: tel: links
            tel_links = soup.find_all('a', href=re.compile(r'^tel:', re.IGNORECASE))
            for link in tel_links:
                phone = link['href'].replace('tel:', '').strip()
                phone = re.sub(r'[^\d+\-\s()]', '', phone)
                if phone:
                    phones.add(phone)
            
            # Pattern 6: Look for phone in specific areas
            contact_sections = soup.find_all(['div', 'section', 'footer'], 
                                           class_=re.compile(r'contact|footer|phone|call', re.IGNORECASE))
            for section in contact_sections:
                section_text = section.get_text()
                phones.update(re.findall(r'\+91[-\s]?\d{10}', section_text))
                phones.update(re.findall(r'\b0\d{2,4}[-\s]?\d{6,8}\b', section_text))
                phones.update(re.findall(r'\b[6-9]\d{9}\b', section_text))
            
        except Exception as e:
            print(f"      [!] Scrape error: {e}")
        
        return list(emails), list(phones)
    
    def find_contact_pages(self, base_url):
        """Find ALL possible contact pages"""
        if not base_url:
            return []
        
        # Comprehensive list of contact page patterns
        patterns = [
            '/contact', '/contact-us', '/contactus', '/contact_us',
            '/reach-us', '/get-in-touch', '/contact.html', '/contact.php',
            '/careers', '/career', '/jobs', '/hiring',
            '/about', '/about-us', '/aboutus', '/about_us',
            '/locations', '/office', '/offices',
            '/support', '/help', '/customer-service',
            '/footer', '/sitemap'
        ]
        
        pages = []
        base_domain = urlparse(base_url).netloc
        
        for pattern in patterns:
            url = urljoin(base_url, pattern)
            try:
                response = requests.head(url, headers=self.headers, timeout=5, allow_redirects=True)
                if response.status_code < 400:
                    # Make sure we're still on same domain
                    if urlparse(response.url).netloc == base_domain:
                        pages.append(response.url)
                        print(f"      [+] Found page: {pattern}")
            except:
                continue
        
        return pages
    
    def filter_best_email(self, emails):
        """Get best HR/career email with priority"""
        if not emails:
            return None
        
        # Clean emails
        clean_emails = []
        for email in emails:
            email = email.lower().strip()
            # Remove common false positives
            if any(x in email for x in ['example.com', 'domain.com', 'yourcompany', 'image', 'png', 'jpg']):
                continue
            if email.count('@') == 1 and '.' in email.split('@')[1]:
                clean_emails.append(email)
        
        if not clean_emails:
            return None
        
        # Priority tiers
        tier1 = ['career', 'careers', 'hr', 'humanresource']
        tier2 = ['job', 'jobs', 'recruit', 'recruitment', 'hiring', 'talent']
        tier3 = ['contact', 'info', 'hello', 'reach']
        
        # Exclude these
        exclude = ['noreply', 'no-reply', 'donotreply', 'marketing', 'sales', 'support']
        
        # Tier 1: Career emails
        for email in clean_emails:
            if any(x in email.lower() for x in exclude):
                continue
            if any(x in email.lower() for x in tier1):
                return email
        
        # Tier 2: Job-related emails
        for email in clean_emails:
            if any(x in email.lower() for x in exclude):
                continue
            if any(x in email.lower() for x in tier2):
                return email
        
        # Tier 3: General contact
        for email in clean_emails:
            if any(x in email.lower() for x in exclude):
                continue
            if any(x in email.lower() for x in tier3):
                return email
        
        # Last resort: first clean email
        for email in clean_emails:
            if not any(x in email.lower() for x in exclude):
                return email
        
        return clean_emails[0] if clean_emails else None
    
    def filter_best_phone(self, phones):
        """Get best phone number"""
        if not phones:
            return None
        
        # Clean and validate phones
        clean_phones = []
        for phone in phones:
            # Remove extra spaces and special chars except +, -, ()
            clean = re.sub(r'[^\d+\-\s()]', '', phone).strip()
            
            # Extract just digits
            digits = re.sub(r'[^\d]', '', clean)
            
            # Valid if has 10+ digits
            if len(digits) >= 10:
                clean_phones.append((phone, digits))
        
        if not clean_phones:
            return None
        
        # Prefer numbers with +91
        for phone, digits in clean_phones:
            if '+91' in phone or phone.startswith('91'):
                return phone
        
        # Prefer landline (starts with 0)
        for phone, digits in clean_phones:
            if phone.strip().startswith('0') or digits.startswith('0'):
                return phone
        
        # Return first valid mobile
        for phone, digits in clean_phones:
            if digits[0] in '6789':  # Indian mobile starts with 6-9
                return phone
        
        # Return first clean phone
        return clean_phones[0][0]
    
    def generate_fallback_email(self, company_name):
        """Generate fallback email"""
        clean = re.sub(r'[^a-z0-9]', '', company_name.lower())
        for word in ['pvtltd', 'pvt', 'ltd', 'limited', 'inc', 'technologies', 'tech', 'solutions']:
            clean = clean.replace(word, '')
        return f"careers@{clean.strip()}.com"
    
    def find_contact(self, company_name, job_url=None):
        """MAIN METHOD - Ultra deep contact finding"""
        print(f"      [*] Ultra search for: {company_name}")
        
        all_emails = set()
        all_phones = set()
        
        # Step 1: Scrape job URL if provided
        if job_url:
            print(f"      [*] Checking job posting...")
            emails, phones = self.deep_scrape_contact_page(job_url)
            all_emails.update(emails)
            all_phones.update(phones)
        
        # Step 2: Find company website
        website = self.find_company_website(company_name)
        
        if website:
            # Step 3: Find all contact-related pages
            print(f"      [*] Searching contact pages...")
            contact_pages = self.find_contact_pages(website)
            
            if contact_pages:
                print(f"      [+] Found {len(contact_pages)} contact pages")
                
                # Step 4: Deep scrape each contact page
                for i, page in enumerate(contact_pages[:5], 1):  # Check top 5 pages
                    print(f"      [*] Scraping page {i}/{min(len(contact_pages), 5)}...")
                    emails, phones = self.deep_scrape_contact_page(page)
                    all_emails.update(emails)
                    all_phones.update(phones)
                    time.sleep(1.5)  # Be respectful
            else:
                print(f"      [!] No contact pages found, trying homepage...")
                emails, phones = self.deep_scrape_contact_page(website)
                all_emails.update(emails)
                all_phones.update(phones)
        
        # Step 5: Filter and select best
        best_email = self.filter_best_email(list(all_emails))
        best_phone = self.filter_best_phone(list(all_phones))
        
        # Step 6: Results
        if not best_email:
            best_email = self.generate_fallback_email(company_name)
            print(f"      [!] Using pattern: {best_email}")
        else:
            print(f"      [++] REAL Email: {best_email}")
        
        if best_phone:
            print(f"      [++] REAL Phone: {best_phone}")
        else:
            print(f"      [!] No phone found")
        
        if all_emails:
            print(f"      [i] Found {len(all_emails)} total emails")
        if all_phones:
            print(f"      [i] Found {len(all_phones)} total phones")
        
        return best_email, best_phone


def setup_driver():
    """Setup Chrome driver"""
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def connect_to_sheet():
    """Connect to Google Sheets"""
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME)


def is_target_location(location):
    """Check if location matches target"""
    location_lower = location.lower()
    return any(target in location_lower for target in TARGET_LOCATIONS)


def scrape_naukri_location_specific(job_title, driver, max_jobs=12):
    """Scrape Naukri"""
    jobs = []
    search_query = job_title.replace(' ', '-').lower()
    url = f"https://www.naukri.com/{search_query}-jobs-in-chandigarh"
    
    try:
        print(f"   [*] Naukri: {url}")
        driver.get(url)
        time.sleep(3)
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "srp-jobtuple-wrapper")))
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(2)
        
        job_cards = driver.find_elements(By.CLASS_NAME, "srp-jobtuple-wrapper")
        
        for card in job_cards[:max_jobs]:
            try:
                try:
                    company = card.find_element(By.CLASS_NAME, "comp-name").text.strip()
                except:
                    company = card.find_element(By.CLASS_NAME, "companyInfo").text.strip().split('\n')[0]
                
                try:
                    role = card.find_element(By.CLASS_NAME, "title").text.strip()
                except:
                    role = job_title
                
                try:
                    job_url = card.find_element(By.CSS_SELECTOR, "a.title").get_attribute('href')
                except:
                    job_url = url
                
                try:
                    location = card.find_element(By.CLASS_NAME, "locWdth").text.strip()
                except:
                    location = "Chandigarh"
                
                if company and role and is_target_location(location):
                    jobs.append({
                        'company': company,
                        'role': role,
                        'location': location,
                        'url': job_url,
                        'source': 'Naukri'
                    })
                    print(f"   [+] {company} - {role}")
            except:
                continue
        
    except Exception as e:
        print(f"   [X] Error: {e}")
    
    return jobs


def scrape_linkedin_location_specific(job_title, driver, max_jobs=5):
    """Scrape LinkedIn"""
    jobs = []
    search_query = job_title.replace(' ', '%20')
    url = f"https://www.linkedin.com/jobs/search?keywords={search_query}&location=Chandigarh%2C%20India"
    
    try:
        print(f"   [*] LinkedIn")
        driver.get(url)
        time.sleep(4)
        
        for _ in range(2):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
        
        job_cards = driver.find_elements(By.CLASS_NAME, "base-card")
        
        for card in job_cards[:max_jobs]:
            try:
                company = card.find_element(By.CLASS_NAME, "base-search-card__subtitle").text.strip()
                role = card.find_element(By.CLASS_NAME, "base-search-card__title").text.strip()
                job_url = card.find_element(By.CSS_SELECTOR, "a.base-card__full-link").get_attribute('href')
                
                try:
                    location = card.find_element(By.CLASS_NAME, "job-search-card__location").text.strip()
                except:
                    location = "Chandigarh"
                
                if is_target_location(location):
                    jobs.append({
                        'company': company,
                        'role': role,
                        'location': location,
                        'url': job_url,
                        'source': 'LinkedIn'
                    })
                    print(f"   [+] {company} - {role}")
            except:
                continue
    except Exception as e:
        print(f"   [X] Error: {e}")
    
    return jobs


def scrape_unstop(job_title, driver, max_jobs=6):
    """Scrape Unstop"""
    jobs = []
    search_query = job_title.replace(' ', '%20')
    url = f"https://unstop.com/jobs?search={search_query}"
    
    try:
        print(f"   [*] Unstop")
        driver.get(url)
        time.sleep(4)
        
        for _ in range(2):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        job_cards = driver.find_elements(By.CSS_SELECTOR, "[class*='card']")
        
        for card in job_cards[:max_jobs]:
            try:
                company = card.find_element(By.CSS_SELECTOR, "[class*='company']").text.strip()
                role = card.find_element(By.CSS_SELECTOR, "[class*='title']").text.strip()
                job_url = card.find_element(By.TAG_NAME, "a").get_attribute('href')
                
                jobs.append({
                    'company': company,
                    'role': role,
                    'location': 'Chandigarh',
                    'url': job_url,
                    'source': 'Unstop'
                })
                print(f"   [+] {company} - {role}")
            except:
                continue
    except:
        pass
    
    return jobs


def save_jobs_to_sheet(jobs, contact_finder):
    """Save with REAL contact details"""
    if not jobs:
        print("\n[!] No jobs to save!")
        return 0
    
    try:
        sheet = connect_to_sheet()
        worksheet = sheet.worksheet("Job Listings")
        
        existing_data = worksheet.get_all_values()
        existing_companies = [row[0].lower() for row in existing_data[1:] if row]
        
        new_jobs = 0
        for job in jobs:
            if job['company'].lower() in existing_companies:
                print(f"\n   [>] Duplicate: {job['company']}")
                continue
            
            print(f"\n{'='*70}")
            # Ultra deep contact search
            email, phone = contact_finder.find_contact(job['company'], job.get('url'))
            
            row = [
                job['company'],
                job['role'],
                job['location'],
                job['url'],
                email or '',
                phone or 'N/A',
                'Pending',
                datetime.now().strftime('%Y-%m-%d')
            ]
            
            worksheet.append_row(row, value_input_option="USER_ENTERED")
            new_jobs += 1
            print(f"   [+++] SAVED: {job['company']}")
            print(f"   Email: {email}")
            print(f"   Phone: {phone or 'Not found'}")
            
            time.sleep(3)  # Longer delay for deep scraping
        
        print(f"\n[*] New jobs added: {new_jobs}")
        return new_jobs
    except Exception as e:
        print(f"\n[X] Error: {e}")
        import traceback
        traceback.print_exc()
        return 0


def main():
    """Main function"""
    print("="*70)
    print("ULTRA JOB SCRAPER - REAL CONTACT DETAILS")
    print("Deep Scraping for Genuine Emails & Phone Numbers")
    print("="*70)
    
    print(f"\n[*] Locations: {', '.join(TARGET_LOCATIONS)}")
    print(f"[*] Job Titles: {len(JOB_TITLES)}")
    print(f"[*] Platforms: Naukri + LinkedIn + Unstop")
    print(f"[*] Deep Contact Scraping: ENABLED")
    
    print("\n[*] Setting up browser...")
    driver = setup_driver()
    
    print("[*] Initializing Ultra Contact Finder...")
    contact_finder = UltraContactFinder()
    
    all_jobs = []
    
    try:
        for title in JOB_TITLES:
            print(f"\n{'='*70}")
            print(f"[*] Searching: {title}")
            print(f"{'='*70}")
            
            naukri_jobs = scrape_naukri_location_specific(title, driver, max_jobs=10)
            time.sleep(2)
            
            linkedin_jobs = scrape_linkedin_location_specific(title, driver, max_jobs=4)
            time.sleep(2)
            
            unstop_jobs = scrape_unstop(title, driver, max_jobs=4)
            time.sleep(2)
            
            all_jobs.extend(naukri_jobs)
            all_jobs.extend(linkedin_jobs)
            all_jobs.extend(unstop_jobs)
            
            print(f"\n[*] Naukri: {len(naukri_jobs)}")
            print(f"[*] LinkedIn: {len(linkedin_jobs)}")
            print(f"[*] Unstop: {len(unstop_jobs)}")
        
        print(f"\n{'='*70}")
        print(f"[*] TOTAL JOBS: {len(all_jobs)}")
        print(f"{'='*70}")
        
        if all_jobs:
            print("\n[*] Starting ULTRA DEEP contact extraction...")
            print("[!] This will take 15-30 minutes (thorough scraping)...\n")
            
            new_count = save_jobs_to_sheet(all_jobs, contact_finder)
            print(f"\n[+++] SUCCESS! Saved {new_count} jobs with REAL contacts!")
        else:
            print("\n[!] No jobs found")
    
    except Exception as e:
        print(f"\n[X] Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n[*] Closing browser...")
        driver.quit()
    
    print("\n[+++] Scraping completed!")
    print("="*70)


if __name__ == "__main__":
    main()