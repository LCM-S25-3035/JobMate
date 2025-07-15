"""
Elasticsearch Search Service for JobMate
Handles search queries and filtering functionality
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from elasticsearch_dsl.query import MultiMatch, Bool, Range, Terms

from flask import current_app
from app.search.documents import JobDocument
from app.services.index_manager import index_manager

logger = logging.getLogger(__name__)


class SearchService:
    """Elasticsearch search service for job postings"""
    
    def __init__(self):
        self.index_manager = index_manager
    
    def is_available(self) -> bool:
        """Check if search service is available"""
        return self.index_manager.is_available()
    
    def search_jobs(
        self,
        query: str = '',
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = 'relevance'
    ) -> Dict[str, Any]:
        """Search for jobs with filters and pagination"""
        if not self.is_available():
            return self._empty_result()
        
        try:
            # Build search query
            search = JobDocument.search()
            
            # Apply text search
            if query:
                search = search.query(
                    MultiMatch(
                        query=query,
                        fields=[
                            'title^3',
                            'company_name^2',
                            'description',
                            'requirements',
                            'required_skills^2',
                            'industry'
                        ],
                        fuzziness='AUTO',
                        type='best_fields'
                    )
                )
            
            # Apply filters
            search = self._apply_filters(search, filters)
            
            # Apply sorting
            search = self._apply_sorting(search, sort_by)
            
            # Apply pagination
            start = (page - 1) * per_page
            search = search[start:start + per_page]
            
            # Execute search
            response = search.execute()
            
            # Build result
            jobs = []
            for hit in response:
                job_data = hit.to_dict()
                job_data['id'] = hit.meta.id
                job_data['score'] = hit.meta.score
                jobs.append(job_data)
            
            total = response.hits.total.value
            
            return {
                'jobs': jobs,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page,
                'has_next': page * per_page < total,
                'has_prev': page > 1,
                'query': query,
                'filters': filters or {}
            }
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return self._empty_result()
    
    def _apply_filters(self, search, filters: Optional[Dict[str, Any]]):
        """Apply search filters"""
        if not filters:
            # Default filters for active jobs
            search = search.filter('term', status='active')
            search = search.filter('range', expires_at={'gte': datetime.utcnow()})
            return search
        
        bool_query = Bool()
        
        # Location filter (single)
        if filters.get('location'):
            bool_query = bool_query.filter(
                'multi_match',
                query=filters['location'],
                fields=['city', 'province', 'location']
            )
        
        # Location filter (multiple from sidebar)
        if filters.get('location_multiple'):
            bool_query = bool_query.filter('terms', city=filters['location_multiple'])
        
        # Remote type filter
        if filters.get('remote_type'):
            bool_query = bool_query.filter('term', remote_type=filters['remote_type'])
        
        # Employment type filter
        if filters.get('employment_type'):
            bool_query = bool_query.filter('term', employment_type=filters['employment_type'])
        
        # Experience level filter
        if filters.get('experience_level'):
            bool_query = bool_query.filter('term', experience_level=filters['experience_level'])
        
        # Salary range filter
        if filters.get('salary_min'):
            bool_query = bool_query.filter('range', salary_max={'gte': filters['salary_min']})
        
        if filters.get('salary_max'):
            bool_query = bool_query.filter('range', salary_min={'lte': filters['salary_max']})
        
        # Skills filter
        if filters.get('skills'):
            skills = filters['skills'] if isinstance(filters['skills'], list) else [filters['skills']]
            bool_query = bool_query.filter('terms', required_skills=skills)
        
        # Company size filter (single)
        if filters.get('company_size'):
            bool_query = bool_query.filter('term', company_size=filters['company_size'])
        
        # Company size filter (multiple from sidebar)
        if filters.get('company_size_multiple'):
            bool_query = bool_query.filter('terms', company_size=filters['company_size_multiple'])
        
        # Industry filter (single)
        if filters.get('industry'):
            bool_query = bool_query.filter('term', industry=filters['industry'])
        
        # Industry filter (multiple from sidebar)
        if filters.get('industry_multiple'):
            bool_query = bool_query.filter('terms', industry=filters['industry_multiple'])
        
        # Featured jobs filter
        if filters.get('featured_only'):
            bool_query = bool_query.filter('term', featured=True)
        
        # Urgent jobs filter
        if filters.get('urgent_only'):
            bool_query = bool_query.filter('term', urgent=True)
        
        # Date range filter
        if filters.get('posted_since'):
            bool_query = bool_query.filter('range', created_at={'gte': filters['posted_since']})
        
        # Default filters
        bool_query = bool_query.filter('term', status='active')
        bool_query = bool_query.filter('range', expires_at={'gte': datetime.utcnow()})
        
        return search.query(bool_query)
    
    def _apply_sorting(self, search, sort_by: str):
        """Apply sorting to search"""
        if sort_by == 'date':
            search = search.sort('-created_at')
        elif sort_by == 'salary':
            search = search.sort('-salary_max')
        elif sort_by == 'featured':
            search = search.sort('-featured', '-created_at')
        elif sort_by == 'applications':
            search = search.sort('-application_count')
        elif sort_by == 'views':
            search = search.sort('-view_count')
        # Default is relevance (elasticsearch score)
        
        return search
    
    def get_autocomplete_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """Get autocomplete suggestions for job titles"""
        if not self.is_available() or not query:
            return []
        
        try:
            search = JobDocument.search()
            
            # Use match query for autocomplete
            search = search.query(
                MultiMatch(
                    query=query,
                    fields=['title^3', 'company_name^2'],
                    type='phrase_prefix'
                )
            )
            
            # Only get active jobs
            search = search.filter('term', status='active')
            search = search.filter('range', expires_at={'gte': datetime.utcnow()})
            
            # Limit results
            search = search[:limit]
            
            response = search.execute()
            
            suggestions = []
            for hit in response:
                suggestions.append(hit.title)
            
            return list(set(suggestions))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Failed to get autocomplete suggestions: {e}")
            return []
    
    def get_facets(self, query: str = '', filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get faceted search results for filters"""
        if not self.is_available():
            return {}
        
        try:
            search = JobDocument.search()
            
            # Apply base query
            if query:
                search = search.query(
                    MultiMatch(
                        query=query,
                        fields=['title^3', 'company_name^2', 'description', 'requirements'],
                        fuzziness='AUTO'
                    )
                )
            
            # Apply filters (similar to search_jobs)
            search = self._apply_filters(search, filters)
            
            # Add aggregations
            search.aggs.bucket('locations', 'terms', field='city', size=20)
            search.aggs.bucket('remote_types', 'terms', field='remote_type', size=10)
            search.aggs.bucket('employment_types', 'terms', field='employment_type', size=10)
            search.aggs.bucket('experience_levels', 'terms', field='experience_level', size=10)
            search.aggs.bucket('company_sizes', 'terms', field='company_size', size=10)
            search.aggs.bucket('industries', 'terms', field='industry', size=20)
            search.aggs.bucket('required_skills', 'terms', field='required_skills', size=30)
            
            # Salary range aggregation
            search.aggs.metric('salary_stats', 'stats', field='salary_max')
            
            # Don't return actual documents, just aggregations
            search = search[:0]
            
            response = search.execute()
            
            facets = {}
            if hasattr(response, 'aggregations'):
                for facet_name, aggregation in response.aggregations.items():
                    if facet_name == 'salary_stats':
                        facets[facet_name] = {
                            'min': getattr(aggregation, 'min', 0),
                            'max': getattr(aggregation, 'max', 0),
                            'avg': getattr(aggregation, 'avg', 0)
                        }
                    else:
                        # Handle buckets safely
                        if hasattr(aggregation, 'buckets'):
                            facets[facet_name] = [
                                {'key': bucket.key, 'count': bucket.doc_count}
                                for bucket in aggregation.buckets
                            ]
                        else:
                            facets[facet_name] = []
            
            return facets
            
        except Exception as e:
            logger.error(f"Failed to get facets: {e}")
            return {}
    
    def get_similar_jobs(self, job_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get jobs similar to a given job"""
        if not self.is_available():
            return []
        
        try:
            # Get the original job
            original_job = JobDocument.get(id=job_id)
            
            # Build similarity query
            search = JobDocument.search()
            search = search.query(
                'more_like_this',
                fields=['title', 'description', 'required_skills', 'industry'],
                like=[{'_index': original_job.meta.index, '_id': job_id}],
                min_term_freq=1,
                max_query_terms=25
            )
            
            # Filter out the original job
            search = search.filter('bool', must_not=[{'term': {'_id': job_id}}])
            
            # Only active jobs
            search = search.filter('term', status='active')
            search = search.filter('range', expires_at={'gte': datetime.utcnow()})
            
            # Limit results
            search = search[:limit]
            
            response = search.execute()
            
            similar_jobs = []
            for hit in response:
                job_data = hit.to_dict()
                job_data['id'] = hit.meta.id
                job_data['score'] = hit.meta.score
                similar_jobs.append(job_data)
            
            return similar_jobs
            
        except Exception as e:
            logger.error(f"Failed to get similar jobs: {e}")
            return []
    
    def get_job_by_id(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific job by ID"""
        if not self.is_available():
            return None
        
        try:
            job = JobDocument.get(id=job_id)
            job_data = job.to_dict()
            job_data['id'] = job.meta.id
            return job_data
            
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty search result"""
        return {
            'jobs': [],
            'total': 0,
            'page': 1,
            'per_page': 20,
            'pages': 0,
            'has_next': False,
            'has_prev': False,
            'query': '',
            'filters': {}
        }


# Global search service instance
search_service = SearchService() 