# Job Application Automation - Chandigarh/Mohali

A comprehensive, automated job scraping and application system designed specifically for Chandigarh/Mohali region. This tool scrapes job postings, extracts company contact details, and sends personalized email applications with resume attachments.

## Overview

This project combines web scraping, Google Sheets integration, and Gmail API to automate the job application process. It finds relevant job postings, extracts genuine company contact information, and sends professional applications directly to companies.

### Key Features

✅ **Location-Specific Scraping** - Targets only Chandigarh, Mohali, and surrounding areas  
✅ **Deep Contact Extraction** - Scrapes company "Contact Us" pages for real phone & email  
✅ **Google Sheets Integration** - Automatically tracks all applications in a spreadsheet  
✅ **Gmail Integration** - Sends personalized emails with your resume  
✅ **Smart Verification** - Validates and updates email addresses for accuracy  
✅ **One-Click Operation** - Simple batch file or Python runner for complete workflow  

## Project Structure

```
chandigarh jobsscraper/
├── 1_job_scraper.py          # Main job scraping engine
├── email_sender.py           # Gmail email sending system
├── email_verifier.py         # Email validation & update tool
├── 0_setup_checker.py        # Pre-flight verification script
├── check_sheet.py            # Google Sheet diagnostic tool
├── run.py                    # Python script runner
├── RUN.bat                   # One-click Windows batch runner
├── credentials.json          # Google API credentials (you provide)
├── token.pickle              # OAuth token cache (auto-generated)
├── COMPLETE SETUP GUIDE/     # Detailed setup instructions
└── venv/                     # Python virtual environment
```

## System Components

### 1. Job Scraper (`1_job_scraper.py`)
The core scraping engine that:
- Searches for job postings (Prompt Engineer, AI Developer, Full Stack, Python, Backend, Project Coordinator)
- Filters by location (Chandigarh, Mohali, Tricity, Punjab, Panchkula, Zirakpur)
- Extracts company details from job listings
- Scrapes company websites for contact information
- Updates Google Sheets with findings
- Uses Selenium WebDriver for dynamic page loading

**Target Job Titles:**
- Prompt Engineer
- AI Automation Developer
- Full Stack Developer
- Python Developer
- Backend Developer
- Project Coordinator

**Target Locations:**
- Chandigarh
- Mohali
- Tricity
- Punjab
- Panchkula
- Zirakpur

### 2. Email Sender (`email_sender.py`)
Automated email application system:
- Connects to Gmail API for secure sending
- Personalizes emails with company/role information
- Attaches your resume (PDF format)
- Tracks email status in Google Sheets
- Handles authentication and token refresh
- Manages application history

### 3. Email Verifier (`email_verifier.py`)
Maintenance and validation tool:
- Finds and updates incorrect email addresses
- Scrapes company websites for verified contact info
- Updates existing Google Sheet entries
- Identifies and fixes bad emails before sending
- Improves delivery rates

### 4. Setup Checker (`0_setup_checker.py`)
Pre-flight verification utility:
- Validates Python installation
- Checks required dependencies
- Verifies file structure
- Confirms API credentials
- Identifies missing packages

### 5. Google Sheet Diagnostic (`check_sheet.py`)
Troubleshooting tool:
- Displays current sheet structure
- Shows column headers
- Lists all entries
- Identifies formatting issues
- Provides diagnostic information

## Setup Requirements

### Prerequisites
- **Python 3.8+** installed on Windows
- **Google Account** with API access enabled
- **Gmail Account** (can be same as Google Account)
- **Resume** in PDF format
- **Internet Connection**

### Dependencies

The project requires these Python packages:

```
selenium              # Web browser automation
webdriver-manager    # Automatic Chrome driver management
gspread             # Google Sheets API client
google-auth-oauthlib # Google authentication
google-auth-httplib2 # Google HTTP support
google-api-client   # Google API client library
beautifulsoup4      # HTML parsing
requests            # HTTP requests
```

## Installation & Setup

### Step 1: Extract and Navigate
```bash
# Navigate to the project directory
cd "c:\Users\acer\Documents\chandigarh jobsscraper"
```

### Step 2: Create Virtual Environment
```bash
# Create Python virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
# Install all required packages
pip install selenium webdriver-manager gspread google-auth-oauthlib google-auth-httplib2 google-api-client beautifulsoup4 requests
```

### Step 4: Google API Setup

**A. Enable APIs:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Google Sheets API**
4. Enable **Gmail API**
5. Enable **Google Drive API**

**B. Create OAuth Credentials:**
1. Go to **Credentials** section
2. Click **Create Credentials** → **OAuth 2.0 Client ID**
3. Choose **Desktop Application**
4. Download JSON and save as `credentials.json` in project folder

**C. Prepare Resume:**
1. Save your resume as `Manpreet Singh.pdf` in the project folder
   (Or edit `email_sender.py` line ~25 to use your resume filename)

### Step 5: Run Setup Checker
```bash
# Verify everything is configured correctly
python 0_setup_checker.py
```

## Usage

### Method 1: One-Click Windows Batch File (Easiest)
```bash
# Double-click RUN.bat in File Explorer
# Or run in terminal:
RUN.bat
```

This will:
1. Verify Python installation
2. Check for credentials.json
3. Run job scraper
4. Wait 10 seconds
5. Send emails

### Method 2: Python Script Runner
```bash
python run.py
```

Interactive menu for running scripts sequentially with error handling.

### Method 3: Individual Scripts
```bash
# Step 1: Scrape jobs
python 1_job_scraper.py

# Step 2: Send emails
python email_sender.py
```

### Utility Scripts

**Verify your Google Sheet setup:**
```bash
python check_sheet.py
```

**Find and fix bad emails:**
```bash
python email_verifier.py
```

**Verify all prerequisites:**
```bash
python 0_setup_checker.py
```

## Google Sheet Format

The tool automatically creates/uses a sheet named "Job Application Tracker" with these columns:

| Column | Description |
|--------|-------------|
| Company | Company name |
| Role | Job position applied for |
| Location | City/Region |
| URL | Job posting URL |
| Email | Company contact email |
| Phone | Company contact phone |
| Status | Application status |
| Date | Date applied |

## Common Issues & Troubleshooting

### "credentials.json not found"
**Solution:** Download from Google Cloud Console and place in project folder

### "Module not found" errors
**Solution:** Install dependencies:
```bash
pip install selenium webdriver-manager gspread google-auth-oauthlib google-auth-httplib2 google-api-client beautifulsoup4 requests
```

### Chrome driver issues
**Solution:** Project uses webdriver-manager for automatic driver setup. Update Chrome browser to latest version.

### Email sending fails
**Solution:** 
- Verify Gmail API is enabled in Google Cloud Console
- Allow Less Secure Apps (if not using OAuth properly)
- Check 2FA is set up correctly

### "Can't find job postings"
**Solution:** 
- Check internet connection
- Verify location targeting in job_scraper.py
- Wait for Chrome to fully load pages (selenium waits included)

### Sheet not updating
**Solution:**
- Run `check_sheet.py` to verify sheet connection
- Ensure sheet is named exactly "Job Application Tracker"
- Check Google Sheets API is enabled
- Verify gspread has correct permissions

## Customization

### Change Job Titles
Edit `1_job_scraper.py` line ~40:
```python
JOB_TITLES = [
    "Your Job Title Here",
    "Another Title"
]
```

### Change Locations
Edit `1_job_scraper.py` line ~36:
```python
TARGET_LOCATIONS = ['chandigarh', 'mohali', 'your-location']
```

### Change Resume File
Edit `email_sender.py` line ~25:
```python
RESUME_PATH = "Your Resume File.pdf"
```

### Change Sheet Name
Update `SHEET_NAME` constant in each script (currently "Job Application Tracker")

## Workflow

```
┌─────────────────────────────────────────────────────┐
│         1_job_scraper.py Execution                  │
├─────────────────────────────────────────────────────┤
│ 1. Authenticate with Google Sheets                  │
│ 2. Search for jobs by title + location              │
│ 3. Extract company info from job listings           │
│ 4. Scrape company websites for contact details      │
│ 5. Validate emails and phone numbers                │
│ 6. Update Google Sheet with findings                │
│ 7. Mark status as "Pending Email"                   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│         email_sender.py Execution                   │
├─────────────────────────────────────────────────────┤
│ 1. Authenticate with Gmail API                      │
│ 2. Read pending applications from Google Sheet      │
│ 3. Create personalized email for each entry         │
│ 4. Attach resume PDF                                │
│ 5. Send via Gmail                                   │
│ 6. Update status to "Email Sent"                    │
│ 7. Log timestamp                                    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
         Google Sheet Updated ✓
         Emails Delivered ✓
```

## Performance Notes

- **Job Scraping:** 5-15 minutes depending on job availability
- **Chrome Driver:** Auto-managed by webdriver-manager
- **Email Sending:** ~5 seconds per company
- **Google Sheets:** Real-time updates via gspread

## Security Considerations

⚠️ **Important:**
- Never commit `credentials.json` to version control
- Don't share `token.pickle` file
- Keep API credentials private
- Review emails before sending (optional: add confirmation prompt)
- Use application-specific passwords for Gmail if 2FA enabled

## File Descriptions

| File | Purpose |
|------|---------|
| `1_job_scraper.py` | Main scraper - searches jobs, extracts contacts |
| `email_sender.py` | Sends applications via Gmail with resume |
| `email_verifier.py` | Validates and updates email addresses |
| `0_setup_checker.py` | Verifies installation and prerequisites |
| `check_sheet.py` | Diagnostic tool for Google Sheet issues |
| `run.py` | Sequential script runner with error handling |
| `RUN.bat` | Windows batch file for one-click execution |
| `credentials.json` | OAuth credentials (you provide) |
| `token.pickle` | OAuth token cache (auto-generated) |

## Future Enhancements

Potential features for future versions:
- LinkedIn job posting integration
- Phone call notifications
- Application status tracking dashboard
- Resume customization by role
- Interview scheduling automation
- Salary requirement filtering
- Multi-location support (other cities)
- Database storage option
- Email template customization
- Rate limiting for API calls

## API Quotas

**Google Sheets API:** 300 requests/minute  
**Gmail API:** 250 MB/day, 2 billion queries/day  

For large-scale deployments, implement request batching and rate limiting.

## Support & Debugging

**Enable Debug Mode:**
Add this at the top of scripts:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Check Logs:**
- Browser console: Check Chrome developer tools
- Python output: Watch terminal during execution
- Sheet updates: Use `check_sheet.py` to verify

**Common Commands:**
```bash
# Check Python version
python --version

# Verify pip installed
pip --version

# List installed packages
pip list | findstr selenium

# Test Google connection
python -c "import gspread; print('gspread OK')"
```

## License

This project is created for personal job application automation. Modify as needed for your use case.

## Author

Developed for Chandigarh/Mohali job market automation.

---

**Version:** 1.0  
**Last Updated:** January 2026  
**Status:** Production Ready

For issues or questions, refer to the "COMPLETE SETUP GUIDE - Chandigarh/Mohali" folder for detailed step-by-step instructions.
