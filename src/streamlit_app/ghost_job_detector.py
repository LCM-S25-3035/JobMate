
from datetime import datetime
from collections import defaultdict
from difflib import SequenceMatcher
import statistics
import re

GHOST_SCORE_THRESHOLD = 0.7

def is_broken_link(url):
    return any(term in url.lower() for term in ['404', 'expired', 'invalid', '.xyz'])

def is_placeholder(text):
    return not text.strip() or 'lorem' in text.lower() or 'sample' in text.lower()

def is_unrealistic_salary(salary, mean_salary, std_salary):
    try:
        salary = float(salary)
        return salary < (mean_salary - 2 * std_salary) or salary > (mean_salary + 2 * std_salary)
    except:
        return True

def has_generic_keywords(description):
    common_spammy_keywords = ['earn money', 'work from home', 'quick cash', 'no experience']
    desc = description.lower()
    return any(keyword in desc for keyword in common_spammy_keywords)

def is_duplicate_content(job, job_list):
    title, desc = job['title'], job['description']
    for other in job_list:
        if other['url'] != job['url']:
            similarity = SequenceMatcher(None, desc, other['description']).ratio()
            if similarity > 0.95:
                return True
    return False

def detect_ghost_jobs(jobs):
    salaries = [float(j['salary']) for j in jobs if isinstance(j.get('salary'), (int, float))]
    mean_salary = statistics.mean(salaries)
    std_salary = statistics.stdev(salaries)

    url_post_dates = defaultdict(list)
    content_map = defaultdict(set)

    for job in jobs:
        url_post_dates[job['url']].append(datetime.fromisoformat(job['posted_at']))
        content_map[(job['title'], job['description'])].add(job['company'])

    results = []
    for job in jobs:
        score = 0
        url = job['url']
        title = job['title']
        description = job['description']
        salary = job.get('salary', None)
        company = job.get('company', '')
        contact = job.get('contact_email', '')

        dates = url_post_dates[url]
        if len(dates) > 5 and all(abs((d - dates[0]).days) < 10 for d in dates):
            score += 0.3

        if is_broken_link(url):
            score += 0.2

        if is_placeholder(title) or is_placeholder(description):
            score += 0.2

        if is_unrealistic_salary(salary, mean_salary, std_salary):
            score += 0.2

        if not company or not contact:
            score += 0.2

        if len(content_map[(title, description)]) > 3:
            score += 0.2

        if has_generic_keywords(description):
            score += 0.2

        if is_duplicate_content(job, jobs):
            score += 0.2

        results.append({
            'url': url,
            'score': round(score, 2),
            'is_ghost': score >= GHOST_SCORE_THRESHOLD,
            'title': title,
            'company': company,
            'posted_at': job['posted_at']
        })

    return results
