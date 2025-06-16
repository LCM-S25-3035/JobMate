"""
Background tasks for JobMate application using Celery
"""

from celery import Celery
from flask import current_app

def make_celery(app):
    """Create Celery instance for Flask app"""
    celery = Celery(
        app.import_name,
        backend=app.config.get('CELERY_RESULT_BACKEND'),
        broker=app.config.get('CELERY_BROKER_URL')
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Initialize celery with basic config for imports
celery = Celery('app')
celery.config_from_object({
    'broker_url': 'redis://redis:6379/0',
    'result_backend': 'redis://redis:6379/0',
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True,
})

def init_celery(app):
    """Initialize Celery with Flask app"""
    global celery
    celery = make_celery(app)
    return celery

# Example tasks
@celery.task
def send_email_task(to, subject, body):
    """Send email in background"""
    try:
        # Email sending logic would go here
        print(f"Sending email to {to}: {subject}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@celery.task  
def process_resume_task(resume_id):
    """Process resume in background"""
    try:
        # Resume processing logic would go here
        print(f"Processing resume {resume_id}")
        return True
    except Exception as e:
        print(f"Error processing resume: {e}")
        return False

@celery.task
def match_candidates_task(job_id):
    """Match candidates to job in background"""
    try:
        # Candidate matching logic would go here
        print(f"Matching candidates for job {job_id}")
        return True
    except Exception as e:
        print(f"Error matching candidates: {e}")
        return False 