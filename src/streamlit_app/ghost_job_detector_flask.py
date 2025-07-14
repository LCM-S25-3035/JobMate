# ghost_job_detector_flask.py
from flask import Blueprint, render_template
from pymongo import MongoClient
import os
from datetime import datetime
from ghost_job_detector import detect_ghost_jobs  # Import advanced logic

bp = Blueprint('ghost', __name__, template_folder='templates')

def connect_to_mongo():
    uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
    client = MongoClient(uri)
    db = client[os.getenv("MONGO_DB", "autoapply")]
    return db[os.getenv("MONGO_COLLECTION", "resumes")]

@bp.route("/ghost-jobs")
def show():
    collection = connect_to_mongo()
    jobs = list(collection.find().sort("date", -1).limit(100))
    # Convert MongoDB's '_id' and 'date' fields if needed
    for job in jobs:
        if "date" in job and not isinstance(job["date"], str):
            # Convert to ISO format string if not already
            job["posted_at"] = job["date"].isoformat()
        elif "posted_at" not in job:
            job["posted_at"] = datetime.utcnow().isoformat()
        # Ensure all required fields exist for detector
        job.setdefault("title", "")
        job.setdefault("company", "")
        job.setdefault("description", "")
        job.setdefault("salary", "0")
        job.setdefault("url", "")
        job.setdefault("contact_email", "")
    ghost_jobs = detect_ghost_jobs(jobs)
    return render_template("ghost_job.html", ghost_jobs)