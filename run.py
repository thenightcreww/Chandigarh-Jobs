"""
Simple Script Runner - Run both scripts sequentially
Use this if main_automation.py doesn't work
"""

import os
import sys

def run_script(script_name):
    """Run a Python script in the same directory"""
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    if not os.path.exists(script_path):
        print(f"❌ Error: {script_name} not found!")
        return False
    
    print(f"\n{'='*70}")
    print(f"Running: {script_name}")
    print(f"{'='*70}\n")
    
    # Execute the script
    try:
        with open(script_path) as f:
            code = f.read()
        
        # Execute in current Python interpreter
        exec(compile(code, script_path, 'exec'), {'__name__': '__main__'})
        
        print(f"\n✅ {script_name} completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error in {script_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n🚀 JOB APPLICATION AUTOMATION - SIMPLE RUNNER")
    print("="*70)
    
    # Try different possible script names
    scraper_names = ['job_scraper.py', '1_job_scraper.py']
    sender_names = ['email_sender.py', '2_email_sender.py']
    
    # Find scraper
    scraper = None
    for name in scraper_names:
        if os.path.exists(name):
            scraper = name
            break
    
    # Find email sender
    sender = None
    for name in sender_names:
        if os.path.exists(name):
            sender = name
            break
    
    if not scraper:
        print(f"❌ Job scraper not found! Looking for: {scraper_names}")
        input("Press Enter to exit...")
        return
    
    if not sender:
        print(f"❌ Email sender not found! Looking for: {sender_names}")
        input("Press Enter to exit...")
        return
    
    print(f"✅ Found scraper: {scraper}")
    print(f"✅ Found sender: {sender}")
    
    # Run workflow
    print("\n📍 Step 1/2: Scraping jobs...")
    scraper_success = run_script(scraper)
    
    if scraper_success:
        print("\n⏳ Waiting 10 seconds...")
        import time
        time.sleep(10)
        
        print("\n📍 Step 2/2: Sending emails...")
        run_script(sender)
    else:
        print("\n⚠️  Scraper failed, skipping email sending")
    
    print("\n🏁 Workflow complete!")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user")