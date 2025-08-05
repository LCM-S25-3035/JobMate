"""
Enhanced Jobs Faceting Service
Provides improved faceting capabilities for job search
"""

from flask import current_app
from pymongo import MongoClient
from collections import defaultdict
import re

class JobFacetService:
    """Service class for enhanced job faceting"""
    
    def __init__(self, mongo_db):
        self.mongo_db = mongo_db
    
    def get_enhanced_facets(self, base_query=None, current_filters=None):
        """
        Get enhanced facets with counts and better organization
        
        Args:
            base_query: MongoDB query object
            current_filters: Dict of currently applied filters
        
        Returns:
            Dict containing organized facet data
        """
        if base_query is None:
            base_query = {}
        
        if current_filters is None:
            current_filters = {}
        
        try:
            # Enhanced aggregation pipeline
            pipeline = [
                {'$match': base_query},
                {'$facet': {
                    'locations': [
                        {'$match': {
                            'location': {
                                '$type': 'string', 
                                '$ne': '', 
                                '$exists': True,
                                '$not': {'$regex': '^(nan|null|none)$', '$options': 'i'}
                            }
                        }},
                        {'$group': {'_id': '$location', 'count': {'$sum': 1}}},
                        {'$match': {'_id': {'$ne': None}}},
                        {'$sort': {'count': -1}},
                        {'$limit': 50}
                    ],
                    'job_types': [
                        {'$match': {
                            'job_type': {
                                '$type': 'string', 
                                '$ne': '', 
                                '$exists': True,
                                '$not': {'$regex': '^(nan|null|none)$', '$options': 'i'}
                            }
                        }},
                        {'$project': {
                            'job_type_split': {
                                '$map': {
                                    'input': {'$split': ['$job_type', ',']},
                                    'as': 'jt',
                                    'in': {'$trim': {'input': '$$jt'}}
                                }
                            }
                        }},
                        {'$unwind': '$job_type_split'},
                        {'$group': {'_id': '$job_type_split', 'count': {'$sum': 1}}},
                        {'$match': {'_id': {'$ne': None, '$ne': ''}}},
                        {'$sort': {'count': -1}}
                    ],
                    'job_levels': [
                        {'$match': {
                            'job_level': {
                                '$type': 'string', 
                                '$ne': '', 
                                '$exists': True,
                                '$not': {'$regex': '^(nan|null|none)$', '$options': 'i'}
                            }
                        }},
                        {'$group': {'_id': '$job_level', 'count': {'$sum': 1}}},
                        {'$match': {'_id': {'$ne': None}}},
                        {'$sort': {'count': -1}}
                    ],
                    'companies': [
                        {'$match': {
                            'company': {
                                '$type': 'string', 
                                '$ne': '', 
                                '$exists': True,
                                '$not': {'$regex': '^(nan|null|none)$', '$options': 'i'}
                            }
                        }},
                        {'$group': {'_id': '$company', 'count': {'$sum': 1}}},
                        {'$match': {'_id': {'$ne': None}}},
                        {'$sort': {'count': -1}},
                        {'$limit': 100}
                    ],
                    'salary_stats': [
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
                                        'if': {
                                            '$and': [
                                                {'$type': '$min_amount'},
                                                {'$eq': [{'$type': '$min_amount'}, 'number']},
                                                {'$gt': ['$min_amount', 0]}
                                            ]
                                        },
                                        'then': '$min_amount',
                                        'else': '$max_amount'
                                    }
                                }
                            },
                            'max_salary': {
                                '$max': {
                                    '$cond': {
                                        'if': {
                                            '$and': [
                                                {'$type': '$max_amount'},
                                                {'$eq': [{'$type': '$max_amount'}, 'number']},
                                                {'$gt': ['$max_amount', 0]}
                                            ]
                                        },
                                        'then': '$max_amount',
                                        'else': '$min_amount'
                                    }
                                }
                            },
                            'avg_salary': {'$avg': '$min_amount'},
                            'count': {'$sum': 1}
                        }}
                    ],
                    'remote_jobs': [
                        {'$match': {
                            '$or': [
                                {'location': {'$regex': 'remote', '$options': 'i'}},
                                {'job_type': {'$regex': 'remote', '$options': 'i'}},
                                {'description': {'$regex': 'remote', '$options': 'i'}}
                            ]
                        }},
                        {'$count': 'total'}
                    ]
                }}
            ]
            
            result = list(self.mongo_db.jobs.aggregate(pipeline))[0]
            
            # Process and enhance facets
            enhanced_facets = {
                'locations': self._process_location_facets(result.get('locations', []), current_filters),
                'job_types': self._process_job_type_facets(result.get('job_types', []), current_filters),
                'job_levels': self._process_job_level_facets(result.get('job_levels', []), current_filters),
                'companies': self._process_company_facets(result.get('companies', []), current_filters),
                'salary_stats': result.get('salary_stats', [{}])[0] if result.get('salary_stats') else {},
                'remote_count': result.get('remote_jobs', [{}])[0].get('total', 0) if result.get('remote_jobs') else 0
            }
            
            return enhanced_facets
            
        except Exception as e:
            current_app.logger.error(f"Error in get_enhanced_facets: {str(e)}")
            return self._get_empty_facets()
    
    def _process_location_facets(self, locations, current_filters):
        """Process location facets with grouping and sorting"""
        processed = []
        remote_locations = []
        
        for location in locations:
            location_name = location['_id']
            count = location['count']
            
            # Skip invalid locations
            if not location_name or location_name.lower() in ['nan', 'null', 'none', '']:
                continue
            
            # Separate remote locations
            if any(keyword in location_name.lower() for keyword in ['remote', 'anywhere', 'work from home']):
                remote_locations.append({
                    'value': location_name,
                    'count': count,
                    'is_selected': current_filters.get('location') == location_name
                })
            else:
                processed.append({
                    'value': location_name,
                    'count': count,
                    'is_selected': current_filters.get('location') == location_name
                })
        
        # Sort: Remote locations first, then by count
        return {
            'remote': remote_locations[:5],  # Top 5 remote options
            'cities': processed[:20],        # Top 20 cities
            'total': len(processed) + len(remote_locations)
        }
    
    def _process_job_type_facets(self, job_types, current_filters):
        """Process job type facets with flexible mapping and filtering"""
        # Map variations to canonical types
        canonical_mapping = {
            'full-time': 'Full-time',
            'fulltime': 'Full-time', 
            'full_time': 'Full-time',
            'part-time': 'Part-time',
            'parttime': 'Part-time',
            'part_time': 'Part-time',
            'contract': 'Contract',
            'temporary': 'Temporary',
            'temp': 'Temporary',
            'internship': 'Internship',
            'intern': 'Internship',
            'freelance': 'Freelance',
            'consultant': 'Contract'
        }
        
        # Aggregate counts for canonical types
        canonical_counts = {}
        
        for job_type in job_types:
            type_name = job_type['_id']
            if not type_name or ',' in type_name:
                continue  # Skip empty or combined types
            
            # Normalize to canonical form
            canonical_type = canonical_mapping.get(type_name.lower(), type_name.title())
            
            if canonical_type in canonical_counts:
                canonical_counts[canonical_type] += job_type['count']
            else:
                canonical_counts[canonical_type] = job_type['count']
        
        # Convert to list format and sort by count
        processed = []
        for job_type, count in sorted(canonical_counts.items(), key=lambda x: x[1], reverse=True):
            processed.append({
                'value': job_type,
                'display': job_type,
                'count': count,
                'is_selected': current_filters.get('job_type') == job_type
            })
        
        return processed
    
    def _process_job_level_facets(self, job_levels, current_filters):
        """Process job level facets with ordering"""
        # Define level order
        level_order = {
            'entry': 1,
            'junior': 2,
            'mid': 3,
            'senior': 4,
            'lead': 5,
            'manager': 6,
            'director': 7,
            'executive': 8
        }
        
        processed = []
        for level in job_levels:
            level_name = level['_id']
            if not level_name:
                continue
            
            processed.append({
                'value': level_name,
                'display': level_name.title(),
                'count': level['count'],
                'order': level_order.get(level_name.lower(), 99),
                'is_selected': current_filters.get('job_level') == level_name
            })
        
        # Sort by defined order, then by count
        return sorted(processed, key=lambda x: (x['order'], -x['count']))
    
    def _process_company_facets(self, companies, current_filters):
        """Process company facets with filtering"""
        processed = []
        
        for company in companies:
            company_name = company['_id']
            if not company_name or company_name.lower() in ['nan', 'null', 'none', '']:
                continue
            
            processed.append({
                'value': company_name,
                'count': company['count'],
                'is_selected': current_filters.get('company') == company_name
            })
        
        return processed
    
    def _get_empty_facets(self):
        """Return empty facets structure"""
        return {
            'locations': {'remote': [], 'cities': [], 'total': 0},
            'job_types': [],
            'job_levels': [],
            'companies': [],
            'salary_stats': {},
            'remote_count': 0
        }
    
    def get_active_filters_summary(self, filters):
        """Get a summary of active filters for display"""
        active = []
        
        if filters.get('search'):
            active.append({
                'type': 'search',
                'label': 'Search',
                'value': filters['search'],
                'display': f"'{filters['search']}'"
            })
        
        if filters.get('location'):
            active.append({
                'type': 'location',
                'label': 'Location',
                'value': filters['location'],
                'display': filters['location']
            })
        
        if filters.get('job_type'):
            active.append({
                'type': 'job_type',
                'label': 'Job Type',
                'value': filters['job_type'],
                'display': filters['job_type'].title()
            })
        
        if filters.get('job_level'):
            active.append({
                'type': 'job_level',
                'label': 'Job Level',
                'value': filters['job_level'],
                'display': filters['job_level'].title()
            })
        
        if filters.get('company'):
            active.append({
                'type': 'company',
                'label': 'Company',
                'value': filters['company'],
                'display': filters['company']
            })
        
        if filters.get('salary_min') or filters.get('salary_max'):
            salary_range = []
            if filters.get('salary_min'):
                salary_range.append(f"${filters['salary_min']:,}+")
            if filters.get('salary_max'):
                salary_range.append(f"up to ${filters['salary_max']:,}")
            
            active.append({
                'type': 'salary',
                'label': 'Salary',
                'value': f"{filters.get('salary_min', 0)}-{filters.get('salary_max', 999999)}",
                'display': ' '.join(salary_range)
            })
        
        return active
