"""
Elasticsearch Documents for JobMate
Defines the structure of documents stored in Elasticsearch
"""

from elasticsearch_dsl import Document, Text, Keyword, Integer, Float, Date, Boolean


class JobDocument(Document):
    """Elasticsearch document for job postings"""
    
    # Basic job info
    title = Text(analyzer='standard', fields={'raw': Keyword()})
    company_name = Text(analyzer='standard', fields={'raw': Keyword()})
    description = Text(analyzer='standard')
    requirements = Text(analyzer='standard')
    responsibilities = Text(analyzer='standard')
    benefits = Text(analyzer='standard')
    
    # Location and remote
    location = Text(analyzer='standard', fields={'raw': Keyword()})
    city = Keyword()
    province = Keyword()
    country = Keyword()
    remote_type = Keyword()
    
    # Employment details
    employment_type = Keyword()
    experience_level = Keyword()
    min_experience_years = Integer()
    max_experience_years = Integer()
    
    # Salary
    salary_min = Float()
    salary_max = Float()
    salary_currency = Keyword()
    salary_type = Keyword()
    
    # Skills and industry
    required_skills = Keyword(multi=True)
    preferred_skills = Keyword(multi=True)
    industry = Keyword()
    
    # Company info
    company_size = Keyword()
    company_type = Keyword()
    
    # Job metadata
    status = Keyword()
    source = Keyword()
    featured = Boolean()
    urgent = Boolean()
    
    # Metrics
    view_count = Integer()
    application_count = Integer()
    
    # Timestamps
    created_at = Date()
    updated_at = Date()
    expires_at = Date()
    published_at = Date()
    
    class Index:
        name = 'jobmate_jobs'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {
                'analyzer': {
                    'job_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': ['lowercase', 'stop', 'synonym_filter']
                    },
                    'autocomplete_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': ['lowercase', 'edge_ngram_filter']
                    }
                },
                'filter': {
                    'synonym_filter': {
                        'type': 'synonym',
                        'synonyms': [
                            'developer,programmer,coder,engineer',
                            'javascript,js,node.js,nodejs',
                            'python,py,django,flask',
                            'senior,sr,lead',
                            'junior,jr,entry',
                            'frontend,front-end,ui,ux',
                            'backend,back-end,server-side',
                            'fullstack,full-stack,full stack'
                        ]
                    },
                    'edge_ngram_filter': {
                        'type': 'edge_ngram',
                        'min_gram': 2,
                        'max_gram': 20
                    }
                }
            }
        }
    
    def to_dict(self, **kwargs):
        """Convert document to dictionary"""
        return {
            'id': getattr(self.meta, 'id', None),
            'title': getattr(self, 'title', ''),
            'company_name': getattr(self, 'company_name', ''),
            'description': getattr(self, 'description', ''),
            'requirements': getattr(self, 'requirements', ''),
            'location': getattr(self, 'location', ''),
            'city': getattr(self, 'city', ''),
            'province': getattr(self, 'province', ''),
            'remote_type': getattr(self, 'remote_type', ''),
            'employment_type': getattr(self, 'employment_type', ''),
            'experience_level': getattr(self, 'experience_level', ''),
            'salary_min': getattr(self, 'salary_min', None),
            'salary_max': getattr(self, 'salary_max', None),
            'salary_currency': getattr(self, 'salary_currency', 'CAD'),
            'required_skills': getattr(self, 'required_skills', []),
            'preferred_skills': getattr(self, 'preferred_skills', []),
            'industry': getattr(self, 'industry', ''),
            'company_size': getattr(self, 'company_size', ''),
            'status': getattr(self, 'status', 'draft'),
            'featured': getattr(self, 'featured', False),
            'urgent': getattr(self, 'urgent', False),
            'created_at': getattr(self, 'created_at', None),
            'expires_at': getattr(self, 'expires_at', None),
            'score': getattr(self.meta, 'score', 0)
        }
    
    @classmethod
    def from_job_posting(cls, job):
        """Create document from JobPosting model"""
        doc = cls(meta={'id': job.id})
        doc.title = job.title
        doc.company_name = job.company_name
        doc.description = job.description or ''
        doc.requirements = job.requirements or ''
        doc.responsibilities = job.responsibilities or ''
        doc.benefits = job.benefits or ''
        doc.location = job.location or ''
        doc.city = job.city or ''
        doc.province = job.province or ''
        doc.country = job.country or 'Canada'
        doc.remote_type = job.remote_type or 'onsite'
        doc.employment_type = job.employment_type or 'full_time'
        doc.experience_level = job.experience_level or 'mid'
        doc.min_experience_years = job.min_experience_years
        doc.max_experience_years = job.max_experience_years
        doc.salary_min = job.salary_min
        doc.salary_max = job.salary_max
        doc.salary_currency = job.salary_currency or 'CAD'
        doc.salary_type = job.salary_type or 'yearly'
        doc.required_skills = job.required_skills or []
        doc.preferred_skills = job.preferred_skills or []
        doc.industry = job.industry or ''
        doc.company_size = job.company_size or ''
        doc.company_type = job.company_type or ''
        doc.status = job.status or 'draft'
        doc.source = job.source or 'internal'
        doc.featured = job.featured or False
        doc.urgent = job.urgent or False
        doc.view_count = job.view_count or 0
        doc.application_count = job.application_count or 0
        doc.created_at = job.created_at
        doc.updated_at = job.updated_at
        doc.expires_at = job.expires_at
        doc.published_at = job.published_at
        return doc 