# -*- coding: utf-8 -*-
"""
Setup Checker - Verify everything is ready
Run this FIRST before using the automation
"""

import os
import sys

def check_file(filename, required=True):
    """Check if file exists"""
    exists = os.path.exists(filename)
    size = os.path.getsize(filename) if exists else 0
    
    if exists:
        print(f"[+] {filename:30} - Found ({size:,} bytes)")
        return True
    else:
        symbol = "[X]" if required else "[!]"
        status = "REQUIRED" if required else "OPTIONAL"
        print(f"{symbol} {filename:30} - NOT FOUND ({status})")
        return False

def check_module(module_name):
    """Check if Python module is installed"""
    try:
        __import__(module_name)
        print(f"[+] {module_name:25} - Installed")
        return True
    except ImportError:
        print(f"[X] {module_name:25} - NOT INSTALLED")
        return False

def main():
    print("="*70)
    print("SETUP VERIFICATION FOR JOB AUTOMATION")
    print("Chandigarh/Mohali Location-Specific Version")
    print("="*70)
    
    print(f"\n[*] Working Directory: {os.getcwd()}")
    print(f"[*] Python Version: {sys.version}")
    print(f"[*] Python Path: {sys.executable}")
    
    # Check files
    print("\n" + "="*70)
    print("CHECKING FILES:")
    print("="*70)
    
    files_ok = True
    
    # Required files
    files_ok &= check_file('credentials.json', required=True)
    files_ok &= check_file('1_job_scraper.py', required=True)
    files_ok &= check_file('2_email_sender.py', required=True)
    
    # Optional files
    check_file('Manpreet Singh.pdf', required=False)
    check_file('token.pickle', required=False)
    check_file('RUN.bat', required=False)
    check_file('3_email_verifier.py', required=False)
    
    # Check Python packages
    print("\n" + "="*70)
    print("CHECKING PYTHON PACKAGES:")
    print("="*70)
    
    packages_ok = True
    
    packages = [
        'gspread',
        'google.auth',
        'google_auth_oauthlib',
        'googleapiclient',
        'selenium',
        'webdriver_manager',
        'requests',
        'bs4',  # BeautifulSoup
    ]
    
    for pkg in packages:
        packages_ok &= check_module(pkg)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)
    
    if not files_ok:
        print("\n[X] MISSING REQUIRED FILES!")
        print("\n[*] Required files:")
        print("    - credentials.json (from Google Cloud Console)")
        print("    - 1_job_scraper.py (scraper script)")
        print("    - 2_email_sender.py (email sender script)")
    else:
        print("\n[+] All required files found!")
    
    if not packages_ok:
        print("\n[X] MISSING PYTHON PACKAGES!")
        print("\n[*] Install missing packages:")
        print("    pip install gspread google-auth google-auth-oauthlib")
        print("    pip install google-api-python-client selenium webdriver-manager")
        print("    pip install requests beautifulsoup4")
    else:
        print("\n[+] All required packages installed!")
    
    # Check Google Sheet
    print("\n" + "="*70)
    print("GOOGLE SHEET REQUIREMENTS:")
    print("="*70)
    print("\n[*] You need a Google Sheet named: 'Job Application Tracker'")
    print("[*] With these tabs:")
    print("    1. Job Listings")
    print("    2. Email Log")
    print("    3. Config")
    
    # Configuration
    print("\n" + "="*70)
    print("CONFIGURATION:")
    print("="*70)
    print("\n[*] Target Locations:")
    print("    - Chandigarh")
    print("    - Mohali")
    print("    - Punjab (Tricity)")
    
    print("\n[*] Job Titles:")
    print("    - Prompt Engineer")
    print("    - AI Automation Developer")
    print("    - Full Stack Developer")
    print("    - Python Developer")
    print("    - Backend Developer")
    print("    - Project Coordinator")
    
    # Final Status
    print("\n" + "="*70)
    print("READY TO START?")
    print("="*70)
    
    if files_ok and packages_ok:
        print("\n[+] YES! Everything looks good!")
        print("\n[*] Next Steps:")
        print("    1. Double-click RUN.bat (or run: python 1_job_scraper.py)")
        print("    2. Wait for jobs to be scraped")
        print("    3. Emails will be sent automatically")
        print("\n[*] OR run individual scripts:")
        print("    - python 1_job_scraper.py (scrape jobs)")
        print("    - python 2_email_sender.py (send emails)")
    else:
        print("\n[X] NOT READY! Please fix the issues above.")
        print("\n[*] Common fixes:")
        if not files_ok:
            print("    - Download credentials.json from Google Cloud Console")
            print("    - Make sure all .py files are in this folder")
        if not packages_ok:
            print("    - Run: pip install -r requirements.txt")
    
    print("\n" + "="*70)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()