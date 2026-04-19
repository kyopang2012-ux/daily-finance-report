import schedule
import time
import os
import subprocess
from manager_agent import run_task

def job():
    print(f"\n--- Starting Scheduled Run at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    report_path = run_task()
    
    # Optionally open the report in Safari/Chrome automatically on Mac
    if report_path and os.path.exists(report_path):
        subprocess.run(["open", report_path])
        print("Opened the new report in the default browser.")

if __name__ == "__main__":
    print("Fund Manager Scheduler is initializing...")
    print("The AI report job is scheduled to run every day at 08:00 AM.")
    print("Keep this terminal open, or it will stop.")

    # Schedule the job to run every day
    schedule.every().day.at("08:00").do(job)

    # For testing, we also run it once immediately if user uncomments the line below:
    # print("Testing a run immediately...")
    # job()

    # Keep script running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nScheduler stopped by user.")
