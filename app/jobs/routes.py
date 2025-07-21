"""
Jobs Routes for JobMate
Handles job listing with faceting/filtering capabilities
"""

from flask import render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from pymongo import MongoClient
from bson import ObjectId
import os
from app.jobs import bp
from app.models.application import Application
from app.models.job_posting import JobPosting
from app import db


def get_mongo_db():
    """Get MongoDB database connection"""
    return current_app.mongo_db


@bp.route('/')
@bp.route('/list')
def jobs_list():
    """Display jobs list with faceting/filtering capabilities"""
    # Get filter parameters from request
    location = request.args.get('location', '')
    job_type = request.args.get('job_type', '')
    job_level = request.args.get('job_level', '')  # Changed from experience_level
    salary_min = request.args.get('salary_min', type=int)
    salary_max = request.args.get('salary_max', type=int)
    company = request.args.get('company', '')
    search_query = request.args.get('search', '')
    
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 20
    skip = (page - 1) * per_page
    
    mongo_db = get_mongo_db()
    
    if mongo_db is None:
        # Fallback to PostgreSQL jobs if MongoDB is not available
        flash('MongoDB not available. Showing PostgreSQL jobs.', 'warning')
        return redirect(url_for('match.recommended_jobs'))
    
    # Build MongoDB query with proper type checking
    query = {}
    
    # Text search
    if search_query:
        query['$or'] = [
            {'title': {'$regex': search_query, '$options': 'i'}},
            {'description': {'$regex': search_query, '$options': 'i'}},
            {'company': {'$regex': search_query, '$options': 'i'}},
            {'skills': {'$regex': search_query, '$options': 'i'}}
        ]
    
    # Location filter - handle NaN values and type issues
    if location:
        query['$and'] = query.get('$and', [])
        query['$and'].append({
            '$or': [
                {'location': {'$regex': location, '$options': 'i'}},
                {'location': {'$exists': True, '$type': 'string', '$regex': location, '$options': 'i'}}
            ]
        })
    
    # Job type filter with type checking
    if job_type:
        query['$and'] = query.get('$and', [])
        query['$and'].append({
            'job_type': {
                '$exists': True,
                '$type': 'string',
                '$regex': job_type,
                '$options': 'i'
            }
        })
    
    # Job level filter with type checking
    if job_level:
        query['$and'] = query.get('$and', [])
        query['$and'].append({
            'job_level': {
                '$exists': True,
                '$type': 'string',
                '$regex': job_level,
                '$options': 'i'
            }
        })
    
    # Company filter with type checking
    if company:
        query['$and'] = query.get('$and', [])
        query['$and'].append({
            'company': {
                '$exists': True,
                '$type': 'string',
                '$regex': company,
                '$options': 'i'
            }
        })
    
    # Salary filter with proper numeric handling
    if salary_min or salary_max:
        salary_conditions = []
        
        if salary_min:
            salary_conditions.extend([
                {'min_amount': {'$gte': salary_min, '$type': 'number'}},
                {'max_amount': {'$gte': salary_min, '$type': 'number'}}
            ])
        
        if salary_max:
            salary_conditions.extend([
                {'min_amount': {'$lte': salary_max, '$type': 'number'}},
                {'max_amount': {'$lte': salary_max, '$type': 'number'}}
            ])
        
        if salary_conditions:
            query['$and'] = query.get('$and', [])
            query['$and'].append({'$or': salary_conditions})
    
    try:
        # Get jobs with pagination
        jobs_cursor = mongo_db.jobs.find(query).skip(skip).limit(per_page).sort('date_posted', -1)
        jobs_list = list(jobs_cursor)
        
        # Get total count for pagination
        total_jobs = mongo_db.jobs.count_documents(query)
        total_pages = (total_jobs + per_page - 1) // per_page
        
        # Get facet data for filters
        facets = get_job_facets(mongo_db, query)
        
    except Exception as e:
        current_app.logger.error(f"Error in jobs_list: {str(e)}")
        flash('Error loading jobs. Please try again.', 'error')
        jobs_list = []
        total_jobs = 0
        total_pages = 0
        facets = {
            'locations': [],
            'job_types': [],
            'job_levels': [],
            'companies': [],
            'salary_range': {}
        }
    
    return render_template('jobs/list.html', 
                         jobs=jobs_list,
                         facets=facets,
                         current_filters={
                             'location': location,
                             'job_type': job_type,
                             'job_level': job_level,  # Changed from experience_level
                             'salary_min': salary_min,
                             'salary_max': salary_max,
                             'company': company,
                             'search': search_query
                         },
                         pagination={
                             'page': page,
                             'total_pages': total_pages,
                             'total_jobs': total_jobs,
                             'has_prev': page > 1,
                             'has_next': page < total_pages,
                             'prev_num': page - 1 if page > 1 else None,
                             'next_num': page + 1 if page < total_pages else None
                         })


@bp.route('/<job_id>')
def job_detail(job_id):
    """View detailed job posting"""
    mongo_db = get_mongo_db()
    
    if mongo_db is None:
        flash('Job not found.', 'error')
        return redirect(url_for('jobs.jobs_list'))
    
    try:
        job = mongo_db.jobs.find_one({"_id": ObjectId(job_id)})
    except:
        job = None
    
    if not job:
        flash('Job not found.', 'error')
        return redirect(url_for('jobs.jobs_list'))
    
    # Get similar jobs
    similar_jobs = []
    if job.get('company'):
        similar_jobs = list(mongo_db.jobs.find({
            "company": job['company'],
            "_id": {"$ne": ObjectId(job_id)}
        }).limit(3))
    
    # Check if user has applied to this job (if logged in)
    has_applied = False
    if current_user.is_authenticated:
        # Check if application exists in MongoDB tailored_resumes collection
        existing_application = mongo_db.tailored_resumes.find_one({
            "user_id": str(current_user.id),
            "job_id": job_id
        })
        has_applied = bool(existing_application)
    
    return render_template('jobs/detail.html', 
                         job=job,
                         similar_jobs=similar_jobs,
                         has_applied=has_applied)


def get_job_facets(mongo_db, base_query=None):
    """Get facet data for job filtering with proper type handling"""
    if base_query is None:
        base_query = {}
    
    try:
        pipeline = [
            {'$match': base_query},
            {'$facet': {
                'locations': [
                    {'$match': {'location': {'$type': 'string', '$ne': '', '$exists': True}}},
                    {'$group': {'_id': '$location', 'count': {'$sum': 1}}},
                    {'$match': {'_id': {'$ne': None}}},
                    {'$sort': {'count': -1}},
                    {'$limit': 20}
                ],
                'job_types': [
                    {'$match': {'job_type': {'$type': 'string', '$ne': '', '$exists': True}}},
                    {'$group': {'_id': '$job_type', 'count': {'$sum': 1}}},
                    {'$match': {'_id': {'$ne': None}}},
                    {'$sort': {'count': -1}}
                ],
                'job_levels': [
                    {'$match': {'job_level': {'$type': 'string', '$ne': '', '$exists': True}}},
                    {'$group': {'_id': '$job_level', 'count': {'$sum': 1}}},
                    {'$match': {'_id': {'$ne': None}}},
                    {'$sort': {'count': -1}}
                ],
                'companies': [
                    {'$match': {'company': {'$type': 'string', '$ne': '', '$exists': True}}},
                    {'$group': {'_id': '$company', 'count': {'$sum': 1}}},
                    {'$match': {'_id': {'$ne': None}}},
                    {'$sort': {'count': -1}},
                    {'$limit': 20}
                ],
                'salary_ranges': [
                    {'$match': {
                        '$or': [
                            {'min_amount': {'$type': 'number', '$gt': 0}},
                            {'max_amount': {'$type': 'number', '$gt': 0}}
                        ]
                    }},
                    {'$group': {
                        '_id': None,
                        'min_salary': {
                            '$min': {
                                '$cond': {
                                    'if': {'$and': [
                                        {'$type': '$min_amount'},
                                        {'$eq': [{'$type': '$min_amount'}, 'number']},
                                        {'$gt': ['$min_amount', 0]}
                                    ]},
                                    'then': '$min_amount',
                                    'else': '$max_amount'
                                }
                            }
                        },
                        'max_salary': {
                            '$max': {
                                '$cond': {
                                    'if': {'$and': [
                                        {'$type': '$max_amount'},
                                        {'$eq': [{'$type': '$max_amount'}, 'number']},
                                        {'$gt': ['$max_amount', 0]}
                                    ]},
                                    'then': '$max_amount',
                                    'else': '$min_amount'
                                }
                            }
                        }
                    }}
                ]
            }}
        ]
        
        result = list(mongo_db.jobs.aggregate(pipeline))[0]
        
        return {
            'locations': result.get('locations', []),
            'job_types': result.get('job_types', []),
            'job_levels': result.get('job_levels', []),
            'companies': result.get('companies', []),
            'salary_range': result.get('salary_ranges', [{}])[0] if result.get('salary_ranges') else {}
        }
        
    except Exception as e:
        current_app.logger.error(f"Error in get_job_facets: {str(e)}")
        return {
            'locations': [],
            'job_types': [],
            'job_levels': [],
            'companies': [],
            'salary_range': {}
        }


@bp.route('/api/facets')
def jobs_facets_api():
    """API endpoint for getting job facets (for dynamic filtering)"""
    mongo_db = get_mongo_db()
    
    if mongo_db is None:
        return jsonify({'error': 'MongoDB not available'}), 500
    
    facets = get_job_facets(mongo_db)
    return jsonify(facets)


@bp.route('/apply/<job_id>')
@login_required
def apply_to_job(job_id):
    """Redirect to tailor resume page for job application"""
    if not current_user.is_applicant():
        flash('Only applicants can apply to jobs.', 'error')
        return redirect(url_for('jobs.job_detail', job_id=job_id))
    
    return redirect(url_for('main.tailor_resume', job_id=job_id))


@bp.route('/save/<job_id>', methods=['POST'])
@login_required
def save_job(job_id):
    """Save/unsave a job for later"""
    if not current_user.is_applicant():
        return jsonify({'success': False, 'message': 'Only applicants can save jobs'}), 403
    
    mongo_db = get_mongo_db()
    
    if mongo_db is None:
        return jsonify({'success': False, 'message': 'Service unavailable'}), 500
    
    try:
        # Check if job exists
        job = mongo_db.jobs.find_one({"_id": ObjectId(job_id)})
        if not job:
            return jsonify({'success': False, 'message': 'Job not found'}), 404
        
        # Check if already saved
        saved_job = mongo_db.saved_jobs.find_one({
            "user_id": str(current_user.id),
            "job_id": job_id
        })
        
        if saved_job:
            # Unsave
            mongo_db.saved_jobs.delete_one({
                "user_id": str(current_user.id),
                "job_id": job_id
            })
            return jsonify({'success': True, 'message': 'Job unsaved', 'saved': False})
        else:
            # Save
            mongo_db.saved_jobs.insert_one({
                "user_id": str(current_user.id),
                "job_id": job_id,
                "job_title": job.get('title', ''),
                "company": job.get('company', ''),
                "saved_at": current_app.utcnow if hasattr(current_app, 'utcnow') else None
            })
            return jsonify({'success': True, 'message': 'Job saved', 'saved': True})
    
    except Exception as e:
        current_app.logger.error(f"Error saving/unsaving job: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500


@bp.route('/saved')
@login_required
def saved_jobs():
    """View user's saved jobs"""
    if not current_user.is_applicant():
        flash('Only applicants can view saved jobs.', 'error')
        return redirect(url_for('main.dashboard'))
    
    mongo_db = get_mongo_db()
    
    if mongo_db is None:
        flash('Service unavailable.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get user's saved jobs
    saved_jobs_list = list(mongo_db.saved_jobs.find({
        "user_id": str(current_user.id)
    }).sort("saved_at", -1))
    
    # Get full job details
    job_ids = [ObjectId(saved['job_id']) for saved in saved_jobs_list]
    jobs = list(mongo_db.jobs.find({"_id": {"$in": job_ids}}))
    
    return render_template('jobs/saved.html',
                         title='Saved Jobs',
                         jobs=jobs,
                         total_saved=len(jobs))
