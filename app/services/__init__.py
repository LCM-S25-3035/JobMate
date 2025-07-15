"""
Services Module for JobMate
Contains business logic services for the application
"""

from .search_service import SearchService
from .index_manager import IndexManager

__all__ = ['SearchService', 'IndexManager'] 