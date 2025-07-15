"""
Elasticsearch Index Manager for JobMate
Handles index creation, deletion, and management
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError, RequestError
from elasticsearch_dsl import connections

from flask import current_app
from app.models.job_posting import JobPosting
from app.search.documents import JobDocument

logger = logging.getLogger(__name__)


class IndexManager:
    """Manages Elasticsearch indices for JobMate"""
    
    def __init__(self):
        self.client = None
        self.index_name = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Elasticsearch client"""
        try:
            es_url = current_app.config.get('ELASTICSEARCH_URL', 'http://localhost:9200')
            timeout = current_app.config.get('ELASTICSEARCH_TIMEOUT', 30)
            max_retries = current_app.config.get('ELASTICSEARCH_MAX_RETRIES', 3)
            
            self.client = Elasticsearch(
                [es_url],
                timeout=timeout,
                max_retries=max_retries,
                retry_on_timeout=True
            )
            
            # Configure elasticsearch-dsl connection
            connections.configure(
                default={'hosts': [es_url]},
                timeout=timeout
            )
            
            # Set index name with prefix
            prefix = current_app.config.get('ELASTICSEARCH_INDEX_PREFIX', 'jobmate')
            self.index_name = f'{prefix}_jobs'
            JobDocument.Index.name = self.index_name
            
            logger.info(f"Index manager initialized: {es_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Index Manager: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Elasticsearch is available"""
        if not self.client:
            return False
        
        try:
            return self.client.ping()
        except Exception:
            return False
    
    def create_index(self, delete_existing: bool = False) -> bool:
        """Create or update the jobs index"""
        if not self.is_available():
            logger.error("Elasticsearch not available")
            return False
        
        try:
            # Delete existing index if requested
            if delete_existing and self.client.indices.exists(index=self.index_name):
                self.client.indices.delete(index=self.index_name)
                logger.info(f"Deleted existing index: {self.index_name}")
            
            # Create new index
            if not self.client.indices.exists(index=self.index_name):
                JobDocument.init()
                logger.info(f"Created index: {self.index_name}")
            else:
                logger.info(f"Index already exists: {self.index_name}")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            return False
    
    def delete_index(self) -> bool:
        """Delete the jobs index"""
        if not self.is_available():
            return False
        
        try:
            if self.client.indices.exists(index=self.index_name):
                self.client.indices.delete(index=self.index_name)
                logger.info(f"Deleted index: {self.index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete index: {e}")
            return False
    
    def index_exists(self) -> bool:
        """Check if the jobs index exists"""
        if not self.is_available():
            return False
        
        try:
            return self.client.indices.exists(index=self.index_name)
        except Exception:
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        if not self.is_available():
            return {}
        
        try:
            stats = self.client.indices.stats(index=self.index_name)
            return {
                'total_docs': stats['_all']['total']['docs']['count'],
                'total_size': stats['_all']['total']['store']['size_in_bytes'],
                'index_name': self.index_name
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {}
    
    def index_job(self, job: JobPosting) -> bool:
        """Index a single job posting"""
        if not self.is_available():
            return False
        
        try:
            # Create document from job posting
            doc = JobDocument.from_job_posting(job)
            
            # Save to Elasticsearch
            doc.save()
            logger.debug(f"Indexed job: {job.id} - {job.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index job {job.id}: {e}")
            return False
    
    def bulk_index_jobs(self, jobs: list) -> Dict[str, int]:
        """Index multiple jobs in bulk"""
        if not self.is_available():
            return {'indexed': 0, 'failed': 0}
        
        indexed_count = 0
        failed_count = 0
        
        try:
            docs = []
            for job in jobs:
                try:
                    doc = JobDocument.from_job_posting(job)
                    docs.append(doc)
                except Exception as e:
                    logger.error(f"Failed to prepare job {job.id} for indexing: {e}")
                    failed_count += 1
            
            # Bulk index
            if docs:
                for doc in docs:
                    try:
                        doc.save()
                        indexed_count += 1
                    except Exception as e:
                        logger.error(f"Failed to index job in bulk: {e}")
                        failed_count += 1
            
            logger.info(f"Bulk indexed {indexed_count} jobs, {failed_count} failed")
            
        except Exception as e:
            logger.error(f"Bulk indexing failed: {e}")
        
        return {'indexed': indexed_count, 'failed': failed_count}
    
    def reindex_all_jobs(self) -> Dict[str, int]:
        """Reindex all active job postings"""
        if not self.is_available():
            return {'indexed': 0, 'failed': 0}
        
        try:
            # Get all active jobs
            active_jobs = JobPosting.query.filter_by(status='active').all()
            logger.info(f"Found {len(active_jobs)} active jobs to reindex")
            
            # Recreate index
            if not self.create_index(delete_existing=True):
                return {'indexed': 0, 'failed': len(active_jobs)}
            
            # Bulk index all jobs
            return self.bulk_index_jobs(active_jobs)
            
        except Exception as e:
            logger.error(f"Failed to reindex all jobs: {e}")
            return {'indexed': 0, 'failed': 0}
    
    def delete_job(self, job_id: int) -> bool:
        """Delete a job from the index"""
        if not self.is_available():
            return False
        
        try:
            doc = JobDocument.get(id=job_id)
            doc.delete()
            logger.debug(f"Deleted job from index: {job_id}")
            return True
            
        except NotFoundError:
            logger.warning(f"Job not found in index: {job_id}")
            return True  # Already deleted
            
        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}")
            return False
    
    def update_job(self, job: JobPosting) -> bool:
        """Update an existing job in the index"""
        if not self.is_available():
            return False
        
        try:
            # Delete old document
            self.delete_job(job.id)
            
            # Index new document
            return self.index_job(job)
            
        except Exception as e:
            logger.error(f"Failed to update job {job.id}: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the search infrastructure"""
        health = {
            'elasticsearch_available': False,
            'index_exists': False,
            'total_docs': 0,
            'cluster_health': 'red',
            'errors': []
        }
        
        try:
            # Check if Elasticsearch is available
            if not self.is_available():
                health['errors'].append('Elasticsearch is not available')
                return health
            
            health['elasticsearch_available'] = True
            
            # Check cluster health
            cluster_health = self.client.cluster.health()
            health['cluster_health'] = cluster_health['status']
            
            # Check if index exists
            if not self.index_exists():
                health['errors'].append(f'Index {self.index_name} does not exist')
                return health
            
            health['index_exists'] = True
            
            # Get index stats
            stats = self.get_index_stats()
            health['total_docs'] = stats.get('total_docs', 0)
            
        except Exception as e:
            health['errors'].append(f'Health check failed: {str(e)}')
        
        return health


# Global index manager instance
index_manager = IndexManager() 