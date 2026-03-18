@echo off
REM Job Application Automation - One-Click Runner
REM Double-click this file to run complete workflow

cd /d "%~dp0"

echo ============================================================
echo JOB APPLICATION AUTOMATION - ONE CLICK
echo Chandigarh/Mohali Jobs Only
echo ============================================================
echo.

REM Set UTF-8 encoding
chcp 65001 >nul 2>nul

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] ERROR: Python not found!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [+] Python found
echo.

REM Check for required files
if not exist "credentials.json" (
    echo [X] ERROR: credentials.json not found!
    echo Please download from Google Cloud Console
    pause
    exit /b 1
)

echo [+] credentials.json found
echo.

REM Step 1: Run Job Scraper
if exist "1_job_scraper.py" (
    echo ============================================================
    echo STEP 1/2: SCRAPING JOBS (Chandigarh/Mohali Only)
    echo ============================================================
    echo.
    python 1_job_scraper.py
    
    if errorlevel 1 (
        echo.
        echo [X] Job scraping failed!
        pause
        exit /b 1
    )
    
    echo.
    echo [+] Job scraping completed successfully!
    echo.
) else (
    echo [X] ERROR: 1_job_scraper.py not found!
    pause
    exit /b 1
)

REM Wait between steps
echo [*] Waiting 10 seconds before sending emails...
timeout /t 10 /nobreak >nul

REM Step 2: Send Emails
if exist "2_email_sender.py" (
    echo ============================================================
    echo STEP 2/2: SENDING EMAILS
    echo ============================================================
    echo.
    python 2_email_sender.py
    
    if errorlevel 1 (
        echo.
        echo [!] Some emails may have failed
    ) else (
        echo.
        echo [+] Email sending completed!
    )
) else (
    echo [X] ERROR: 2_email_sender.py not found!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo WORKFLOW COMPLETE!
echo ============================================================
echo.
echo [*] Check your Google Sheet "Job Application Tracker"
echo [*] Check your Gmail "Sent" folder
echo.
echo All jobs from Chandigarh and Mohali only!
echo.
pause