"""
Search Routes for JobMate
Main search functionality with Elasticsearch
"""

from flask import render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta

from app.search import bp
from app.search.forms import JobSearchForm, AdvancedJobSearchForm, QuickSearchForm, FilterForm, populate_filter_choices
from app.models.job_posting import JobPosting


@bp.route('/jobs')
def search_jobs():
    """Main job search page"""
    # Import locally to avoid circular imports
    from app.services.search_service import search_service
    
    form = JobSearchForm()
    
    # Get search parameters
    query = request.args.get('query', '').strip()
    location = request.args.get('location', '').strip()
    remote_type = request.args.get('remote_type', '')
    employment_type = request.args.get('employment_type', '')
    experience_level = request.args.get('experience_level', '')
    salary_min = request.args.get('salary_min', type=int)
    salary_max = request.args.get('salary_max', type=int)
    company_size = request.args.get('company_size', '')
    industry = request.args.get('industry', '')
    skills = request.args.get('skills', '')
    featured_only = request.args.get('featured_only', type=bool)
    urgent_only = request.args.get('urgent_only', type=bool)
    sort_by = request.args.get('sort_by', 'relevance')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Build filters
    filters = {}
    if location:
        filters['location'] = location
    if remote_type:
        filters['remote_type'] = remote_type
    if employment_type:
        filters['employment_type'] = employment_type
    if experience_level:
        filters['experience_level'] = experience_level
    if salary_min:
        filters['salary_min'] = salary_min
    if salary_max:
        filters['salary_max'] = salary_max
    if company_size:
        filters['company_size'] = company_size
    if industry:
        filters['industry'] = industry
    if skills:
        filters['skills'] = skills.split(',')
    if featured_only:
        filters['featured_only'] = True
    if urgent_only:
        filters['urgent_only'] = True
    
    # Perform search
    if search_service.is_available():
        results = search_service.search_jobs(
            query=query,
            filters=filters,
            page=page,
            per_page=per_page,
            sort_by=sort_by
        )
        
        # Get facets for filters
        facets = search_service.get_facets(query=query, filters=filters)
        
        # Populate form with current values
        form.query.data = query
        form.location.data = location
        form.remote_type.data = remote_type
        form.employment_type.data = employment_type
        form.experience_level.data = experience_level
        form.salary_min.data = salary_min
        form.salary_max.data = salary_max
        form.company_size.data = company_size
        form.industry.data = industry
        form.skills.data = skills
        form.featured_only.data = featured_only
        form.urgent_only.data = urgent_only
        form.sort_by.data = sort_by
        form.page.data = page
        form.per_page.data = str(per_page)
        
    else:
        # Fallback to database search
        results = _fallback_search(query, filters, page, per_page, sort_by)
        facets = {}
        flash('Search service is temporarily unavailable. Using basic search.', 'warning')
    
    return render_template('search/jobs.html',
                         title='Search Jobs',
                         form=form,
                         results=results,
                         facets=facets,
                         query=query)


@bp.route('/jobs/advanced')
def advanced_search():
    """Advanced job search page"""
    from app.services.search_service import search_service
    
    form = AdvancedJobSearchForm()
    
    # Get all parameters (including advanced ones)
    query = request.args.get('query', '').strip()
    filters = _extract_filters_from_request(request.args)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort_by', 'relevance')
    
    # Perform search
    if search_service.is_available():
        results = search_service.search_jobs(
            query=query,
            filters=filters,
            page=page,
            per_page=per_page,
            sort_by=sort_by
        )
        facets = search_service.get_facets(query=query, filters=filters)
    else:
        results = _fallback_search(query, filters, page, per_page, sort_by)
        facets = {}
    
    # Populate form
    _populate_form_from_request(form, request.args)
    
    return render_template('search/advanced_search.html',
                         title='Advanced Job Search',
                         form=form,
                         results=results,
                         facets=facets,
                         query=query)


@bp.route('/api/autocomplete')
def autocomplete():
    """Autocomplete API endpoint"""
    from app.services.search_service import search_service
    
    query = request.args.get('query', '').strip()
    limit = request.args.get('limit', 5, type=int)
    
    if not query:
        return jsonify({'suggestions': []})
    
    if search_service.is_available():
        suggestions = search_service.get_autocomplete_suggestions(query, limit)
    else:
        # Fallback to database
        suggestions = _fallback_autocomplete(query, limit)
    
    return jsonify({'suggestions': suggestions})


@bp.route('/api/facets')
def get_facets():
    """Get facets for dynamic filtering"""
    from app.services.search_service import search_service
    
    query = request.args.get('query', '').strip()
    filters = _extract_filters_from_request(request.args)
    
    if search_service.is_available():
        facets = search_service.get_facets(query=query, filters=filters)
    else:
        facets = {}
    
    return jsonify({'facets': facets})


@bp.route('/api/jobs/<int:job_id>/similar')
def similar_jobs(job_id):
    """Get similar jobs API endpoint"""
    from app.services.search_service import search_service
    
    limit = request.args.get('limit', 5, type=int)
    
    if search_service.is_available():
        similar = search_service.get_similar_jobs(job_id, limit)
    else:
        similar = []
    
    return jsonify({'similar_jobs': similar})


@bp.route('/job/<int:job_id>')
def job_detail(job_id):
    """Job detail page with search context"""
    from app.services.search_service import search_service
    
    # Get job from database
    job = JobPosting.query.get_or_404(job_id)
    
    # Get similar jobs
    similar_jobs = []
    if search_service.is_available():
        similar_jobs = search_service.get_similar_jobs(job_id, 5)
    
    # Get search context if available
    search_context = {
        'query': request.args.get('query', ''),
        'page': request.args.get('page', 1, type=int),
        'sort_by': request.args.get('sort_by', 'relevance')
    }
    
    return render_template('search/job_detail.html',
                         title=f'{job.title} - {job.company_name}',
                         job=job,
                         similar_jobs=similar_jobs,
                         search_context=search_context)


@bp.route('/health')
def health_check():
    """Search service health check"""
    from app.services.index_manager import index_manager
    
    health = index_manager.health_check()
    
    status_code = 200 if health.get('elasticsearch_available') else 503
    
    return jsonify(health), status_code


@bp.route('/admin/reindex', methods=['POST'])
@login_required
def reindex():
    """Reindex all jobs (admin only)"""
    from app.services.index_manager import index_manager
    
    if not current_user.is_authenticated or current_user.user_type != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('search.search_jobs'))
    
    try:
        result = index_manager.reindex_all_jobs()
        flash(f'Reindexing completed: {result["indexed"]} jobs indexed, {result["failed"]} failed', 'success')
    except Exception as e:
        current_app.logger.error(f'Reindex failed: {e}')
        flash('Reindexing failed. Please try again.', 'error')
    
    return redirect(url_for('search.search_jobs'))


# Helper functions

def _extract_filters_from_request(args):
    """Extract filters from request arguments"""
    filters = {}
    
    # Basic filters (from main form)
    if args.get('location'):
        filters['location'] = args.get('location')
    if args.get('remote_type'):
        filters['remote_type'] = args.get('remote_type')
    if args.get('employment_type'):
        filters['employment_type'] = args.get('employment_type')
    if args.get('experience_level'):
        filters['experience_level'] = args.get('experience_level')
    if args.get('salary_min'):
        filters['salary_min'] = args.get('salary_min', type=int)
    if args.get('salary_max'):
        filters['salary_max'] = args.get('salary_max', type=int)
    if args.get('company_size'):
        filters['company_size'] = args.get('company_size')
    if args.get('industry'):
        filters['industry'] = args.get('industry')
    if args.get('skills'):
        filters['skills'] = args.get('skills').split(',')
    if args.get('featured_only'):
        filters['featured_only'] = True
    if args.get('urgent_only'):
        filters['urgent_only'] = True
    
    # Sidebar filters (multiple selections)
    location_filters = args.getlist('location_filter')
    if location_filters:
        # If sidebar location filters exist, use them instead of main location
        filters['location_multiple'] = location_filters
    
    skills_filters = args.getlist('skills_filter')
    if skills_filters:
        # Combine with skills from main form
        existing_skills = filters.get('skills', [])
        all_skills = existing_skills + skills_filters
        filters['skills'] = list(set(all_skills))  # Remove duplicates
    
    industry_filters = args.getlist('industry_filter')
    if industry_filters:
        filters['industry_multiple'] = industry_filters
    
    company_size_filters = args.getlist('company_size_filter')
    if company_size_filters:
        filters['company_size_multiple'] = company_size_filters
    
    # Advanced filters
    if args.get('company_type'):
        filters['company_type'] = args.get('company_type')
    if args.get('source'):
        filters['source'] = args.get('source')
    if args.get('posted_since'):
        days = int(args.get('posted_since'))
        filters['posted_since'] = datetime.utcnow() - timedelta(days=days)
    
    return filters


def _populate_form_from_request(form, args):
    """Populate form with request arguments"""
    form.query.data = args.get('query', '')
    form.location.data = args.get('location', '')
    form.remote_type.data = args.get('remote_type', '')
    form.employment_type.data = args.get('employment_type', '')
    form.experience_level.data = args.get('experience_level', '')
    form.salary_min.data = args.get('salary_min', type=int)
    form.salary_max.data = args.get('salary_max', type=int)
    form.company_size.data = args.get('company_size', '')
    form.industry.data = args.get('industry', '')
    form.skills.data = args.get('skills', '')
    form.featured_only.data = args.get('featured_only', type=bool)
    form.urgent_only.data = args.get('urgent_only', type=bool)
    form.sort_by.data = args.get('sort_by', 'relevance')
    form.page.data = args.get('page', 1, type=int)
    form.per_page.data = args.get('per_page', '20')
    
    # Advanced form fields
    if hasattr(form, 'company_type'):
        form.company_type.data = args.get('company_type', '')
    if hasattr(form, 'source'):
        form.source.data = args.get('source', '')
    if hasattr(form, 'posted_since'):
        form.posted_since.data = args.get('posted_since', '')


def _fallback_search(query, filters, page, per_page, sort_by):
    """Fallback search using database when Elasticsearch is unavailable"""
    try:
        # Base query
        jobs_query = JobPosting.query.filter_by(status='active')
        
        # Apply text search
        if query:
            search_filter = f'%{query}%'
            jobs_query = jobs_query.filter(
                db.or_(
                    JobPosting.title.ilike(search_filter),
                    JobPosting.company_name.ilike(search_filter),
                    JobPosting.description.ilike(search_filter)
                )
            )
        
        # Apply filters
        if filters.get('location'):
            jobs_query = jobs_query.filter(JobPosting.location.ilike(f'%{filters["location"]}%'))
        if filters.get('remote_type'):
            jobs_query = jobs_query.filter(JobPosting.remote_type == filters['remote_type'])
        if filters.get('employment_type'):
            jobs_query = jobs_query.filter(JobPosting.employment_type == filters['employment_type'])
        if filters.get('experience_level'):
            jobs_query = jobs_query.filter(JobPosting.experience_level == filters['experience_level'])
        if filters.get('salary_min'):
            jobs_query = jobs_query.filter(JobPosting.salary_max >= filters['salary_min'])
        if filters.get('salary_max'):
            jobs_query = jobs_query.filter(JobPosting.salary_min <= filters['salary_max'])
        if filters.get('company_size'):
            jobs_query = jobs_query.filter(JobPosting.company_size == filters['company_size'])
        if filters.get('industry'):
            jobs_query = jobs_query.filter(JobPosting.industry.ilike(f'%{filters["industry"]}%'))
        if filters.get('featured_only'):
            jobs_query = jobs_query.filter(JobPosting.featured == True)
        if filters.get('urgent_only'):
            jobs_query = jobs_query.filter(JobPosting.urgent == True)
        
        # Apply sorting
        if sort_by == 'date':
            jobs_query = jobs_query.order_by(JobPosting.created_at.desc())
        elif sort_by == 'salary':
            jobs_query = jobs_query.order_by(JobPosting.salary_max.desc())
        elif sort_by == 'featured':
            jobs_query = jobs_query.order_by(JobPosting.featured.desc(), JobPosting.created_at.desc())
        else:
            jobs_query = jobs_query.order_by(JobPosting.created_at.desc())
        
        # Paginate
        pagination = jobs_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Convert to expected format
        jobs = []
        for job in pagination.items:
            jobs.append({
                'id': job.id,
                'title': job.title,
                'company_name': job.company_name,
                'description': job.description,
                'location': job.location,
                'remote_type': job.remote_type,
                'employment_type': job.employment_type,
                'experience_level': job.experience_level,
                'salary_min': job.salary_min,
                'salary_max': job.salary_max,
                'required_skills': job.required_skills,
                'company_size': job.company_size,
                'featured': job.featured,
                'urgent': job.urgent,
                'created_at': job.created_at,
                'score': 1.0  # Default score
            })
        
        return {
            'jobs': jobs,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
            'query': query,
            'filters': filters
        }
        
    except Exception as e:
        current_app.logger.error(f'Fallback search failed: {e}')
        return {
            'jobs': [],
            'total': 0,
            'page': 1,
            'per_page': per_page,
            'pages': 0,
            'has_next': False,
            'has_prev': False,
            'query': query,
            'filters': filters
        }


def _fallback_autocomplete(query, limit):
    """Fallback autocomplete using database"""
    try:
        jobs = JobPosting.query.filter(
            JobPosting.title.ilike(f'%{query}%'),
            JobPosting.status == 'active'
        ).limit(limit).all()
        
        return [job.title for job in jobs]
        
    except Exception as e:
        current_app.logger.error(f'Fallback autocomplete failed: {e}')
        return [] 