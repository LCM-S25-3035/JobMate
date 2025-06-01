# hybrid_ghost_detector.py
import joblib
from datetime import datetime
from collections import defaultdict
from difflib import SequenceMatcher
import statistics
import re
import pandas as pd

# Load ML model & vectorizer
model = joblib.load("models/logistic_model.pkl")
vectorizer = joblib.load("models/tfidf_vectorizer.pkl")

# Rule-based threshold
GHOST_SCORE_THRESHOLD = 0.7

def is_broken_link(url):
    return any(term in url.lower() for term in ['404', 'expired', 'invalid', '.xyz'])

def is_placeholder(text):
    return not text.strip() or 'lorem' in text.lower() or 'sample' in text.lower()

def is_unrealistic_salary(salary, mean, std):
    try:
        salary = float(salary)
        return salary < (mean - 2 * std) or salary > (mean + 2 * std)
    except:
        return True

def has_generic_keywords(description):
    keywords = ['earn money', 'work from home', 'quick cash', 'no experience']
    return any(kw in description.lower() for kw in keywords)

def is_duplicate_content(job, job_list):
    for other in job_list:
        if other['url'] != job['url']:
            sim = SequenceMatcher(None, job['description'], other['description']).ratio()
            if sim > 0.95:
                return True
    return False

def rule_based_score(job, stats, url_post_dates, content_map, job_list):
    score = 0
    title = job['title']
    desc = job['description']
    url = job['url']
    salary = job.get('salary')
    company = job.get('company', '')
    contact = job.get('contact_email', '')

    dates = url_post_dates[url]
    if len(dates) > 5 and all(abs((d - dates[0]).days) < 10 for d in dates):
        score += 0.3
    if is_broken_link(url):
        score += 0.2
    if is_placeholder(title) or is_placeholder(desc):
        score += 0.2
    if is_unrealistic_salary(salary, stats['mean'], stats['std']):
        score += 0.2
    if not company or not contact:
        score += 0.2
    if len(content_map[(title, desc)]) > 3:
        score += 0.2
    if has_generic_keywords(desc):
        score += 0.2
    if is_duplicate_content(job, job_list):
        score += 0.2

    return score

def predict_ml(job):
    text = f"{job['title']} {job['company']}"
    X = vectorizer.transform([text])
    pred = model.predict(X)[0]
    prob = model.predict_proba(X)[0][1]
    return pred, prob

def hybrid_detect_ghost_jobs(jobs):
    salaries = [float(j['salary']) for j in jobs if isinstance(j.get('salary'), (int, float))]
    stats = {
        'mean': statistics.mean(salaries),
        'std': statistics.stdev(salaries)
    }
    url_post_dates = defaultdict(list)
    content_map = defaultdict(set)
    for job in jobs:
        url_post_dates[job['url']].append(datetime.fromisoformat(job['posted_at']))
        content_map[(job['title'], job['description'])].add(job['company'])

    results = []
    for job in jobs:
        rule_score = rule_based_score(job, stats, url_post_dates, content_map, jobs)
        ml_pred, ml_prob = predict_ml(job)
        is_ghost = rule_score >= GHOST_SCORE_THRESHOLD or (ml_pred == 1 and ml_prob > 0.75)
        results.append({
            'url': job['url'],
            'rule_score': round(rule_score, 2),
            'ml_prob': round(ml_prob, 2),
            'is_ghost': is_ghost,
            'title': job['title'],
            'company': job['company'],
            'posted_at': job['posted_at']
        })
    return results
