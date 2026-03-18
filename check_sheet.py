# -*- coding: utf-8 -*-
"""
Google Sheet Diagnostic Tool
Checks your sheet structure and shows what's wrong
"""

import gspread
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

SHEET_NAME = "Job Application Tracker"

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
    
    try:
        sheet = client.open_by_key("1lX1T2Cufa-V1ulBYri_FFDgUXGii4GWgJEWkF_IuAXk")
    except:
        sheet = client.open(SHEET_NAME)
    
    return sheet

def main():
    print("="*70)
    print("GOOGLE SHEET DIAGNOSTIC TOOL")
    print("="*70)
    
    try:
        print("\n[*] Connecting to Google Sheets...")
        sheet = connect_to_sheet()
        print(f"[+] Connected to: {sheet.title}")
        
        # Check Job Listings tab
        print("\n" + "="*70)
        print("CHECKING 'Job Listings' TAB")
        print("="*70)
        
        try:
            worksheet = sheet.worksheet("Job Listings")
            all_data = worksheet.get_all_values()
            
            print(f"\n[+] Total rows: {len(all_data)}")
            
            if len(all_data) == 0:
                print("[X] ERROR: Sheet is empty!")
                return
            
            # Show headers
            headers = all_data[0]
            print(f"\n[*] Headers ({len(headers)} columns):")
            for i, header in enumerate(headers, 1):
                print(f"   Column {i} ({chr(64+i)}): {header}")
            
            # Expected structure
            expected = ['Company', 'Role', 'Location', 'Job URL', 'Career Email', 'Phone Number', 'Status', 'Date Added']
            
            print(f"\n[*] Expected structure:")
            for i, exp in enumerate(expected, 1):
                print(f"   Column {i} ({chr(64+i)}): {exp}")
            
            # Check if structure matches
            print(f"\n[*] Structure check:")
            if len(headers) < 7:
                print(f"[X] ERROR: Need at least 7 columns, found {len(headers)}")
                print(f"[!] Missing: Phone Number column?")
            elif len(headers) >= 8:
                print(f"[+] Has {len(headers)} columns - looks good!")
            else:
                print(f"[!] Warning: Only {len(headers)} columns")
            
            # Show data rows
            data_rows = all_data[1:]
            print(f"\n[*] Data rows: {len(data_rows)}")
            
            if len(data_rows) == 0:
                print("[X] ERROR: No data! Run the job scraper first.")
                return
            
            # Show first 3 rows
            print(f"\n[*] First {min(3, len(data_rows))} jobs:")
            for i, row in enumerate(data_rows[:3], 1):
                print(f"\n   Job {i}:")
                print(f"   Company: {row[0] if len(row) > 0 else 'N/A'}")
                print(f"   Role: {row[1] if len(row) > 1 else 'N/A'}")
                print(f"   Location: {row[2] if len(row) > 2 else 'N/A'}")
                print(f"   Email: {row[4] if len(row) > 4 else 'N/A'}")
                print(f"   Phone: {row[5] if len(row) > 5 else 'N/A'}")
                print(f"   Status: {row[6] if len(row) > 6 else 'N/A'}")
            
            # Count by status
            print(f"\n[*] Status breakdown:")
            status_counts = {}
            for row in data_rows:
                if len(row) > 6:
                    status = row[6]
                    status_counts[status] = status_counts.get(status, 0) + 1
            
            for status, count in status_counts.items():
                print(f"   {status}: {count}")
            
            # Check for pending jobs
            pending_count = status_counts.get('Pending', 0) + status_counts.get('pending', 0)
            
            if pending_count == 0:
                print(f"\n[X] NO PENDING JOBS!")
                print(f"[!] This is why email sender found 0 pending applications")
                print(f"\n[*] Solutions:")
                print(f"   1. Run: python 1_job_scraper.py")
                print(f"   2. Or manually change Status to 'Pending' in sheet")
            else:
                print(f"\n[+] Found {pending_count} pending jobs - GOOD!")
                print(f"[+] Email sender should work now")
            
        except Exception as e:
            print(f"[X] Error accessing Job Listings: {e}")
        
        # Check Email Log tab
        print("\n" + "="*70)
        print("CHECKING 'Email Log' TAB")
        print("="*70)
        
        try:
            log_ws = sheet.worksheet("Email Log")
            log_data = log_ws.get_all_values()
            print(f"\n[+] Total entries: {len(log_data)-1}")
            
            if len(log_data) > 1:
                print(f"\n[*] Last 3 emails sent:")
                for row in log_data[-3:]:
                    if len(row) >= 4:
                        print(f"   {row[0]} {row[1]} - {row[2]} - {row[5]}")
        except:
            print(f"[!] Email Log tab not found or empty")
        
        # Check Config tab
        print("\n" + "="*70)
        print("CHECKING 'Config' TAB")
        print("="*70)
        
        try:
            config_ws = sheet.worksheet("Config")
            config_data = config_ws.get_all_values()
            
            print(f"\n[*] Your configuration:")
            for row in config_data[1:]:
                if len(row) >= 2:
                    print(f"   {row[0]}: {row[1]}")
        except:
            print(f"[!] Config tab not found")
        
        # Final summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        
        if pending_count > 0:
            print(f"\n[+] READY TO SEND EMAILS!")
            print(f"[+] {pending_count} pending jobs found")
            print(f"\n[*] Run: python 2_email_sender.py")
        else:
            print(f"\n[X] NOT READY")
            print(f"[!] No pending jobs in sheet")
            print(f"\n[*] Run: python 1_job_scraper.py first")
        
    except Exception as e:
        print(f"\n[X] Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()