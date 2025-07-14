# Debug Backup Files

This folder contains test scripts and debugging files that were created during the debugging process for the resume optimization feature. These files are kept for reference but are not part of the main application test suite.

## Test Files

- `test_direct.py`: Direct test of the resume optimization function
- `test_integration.py`: Integration test for the resume optimization endpoint
- `test_mongo_upsert.py`: Test for MongoDB upsert operations
- `test_mongo.py`: Simplified test for MongoDB operations
- `test_optimize_resume.py`: Test for the optimize resume endpoint

## Debug Files

- `debug_gemini_response.py`: Test script for Gemini API JSON responses
- `debug_gemini.py`: Simplified test for Gemini API 
- `debug_dashboard.py`: Debug script for dashboard route issues
- `debug_cleanup_summary.md`: Documentation of the debugging code cleanup

## Notes

These scripts were used to diagnose and fix a bug where resume optimization would fail when a user tried to optimize a resume for a job for the first time. The issue was fixed by implementing proper document existence checking before attempting updates.

The permanent regression test for this feature is now in `/Users/mithran/JobMateRefactor/test_resume_optimize_regression.py`.
