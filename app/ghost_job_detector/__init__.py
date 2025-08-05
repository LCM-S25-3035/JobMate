"""
Ghost Job Detector Package

This package provides functionality for detecting "ghost jobs" -
job listings that may not be legitimate opportunities.
"""

from .analyzer import analyze_job_listing

__all__ = ['analyze_job_listing']
