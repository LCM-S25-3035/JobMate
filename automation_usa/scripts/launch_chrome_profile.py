import subprocess
import time

def open_job_in_chrome(job_url: str):
    subprocess.run([
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "--profile-directory=Profile 19",
        job_url
    ])
    time.sleep(9)