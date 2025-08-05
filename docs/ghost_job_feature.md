# Ghost Job Indicator Feature

## Overview
The ghost job indicator feature adds a visual representation of the likelihood that a job posting is a "ghost job" - a job that may not be genuinely available, may be posted for data collection, or has other suspicious characteristics.

## Implementation

### Data Structure
Each job in the MongoDB database has the following ghost job related fields:
- `ghost_job_percentage`: Integer value from 0 to 100 representing the likelihood
- `ghost_score`: Float value from 0.0 to 1.0 (same as percentage but in decimal form)
- `ghost_job_reasons`: List of strings explaining why the job might be a ghost job

### Visual Representation
The ghost job indicators appear on each job card in the job listing page, with:
- Color-coded risk levels:
  - Red (70-100%): High risk
  - Orange (40-69%): Medium risk
  - Yellow (20-39%): Low risk
  - Green (1-19%): Very low risk
- Progress bar visualizing the percentage
- Numerical percentage display

### Key Files

#### Templates
- `templates/jobs/list.html`: Contains the HTML for displaying ghost job indicators on job cards

#### CSS
- `static/css/ghost-job-indicator.css`: Styling for the ghost job indicators

#### JavaScript
- `static/js/ghost-job-indicators.js`: Ensures indicators are properly displayed and adds interactivity

### Risk Level Classification

```
70-100%: High risk (Red)
40-69%: Medium risk (Orange)
20-39%: Low risk (Yellow)
1-19%: Very low risk (Green)
0%: No risk (No indicator shown)
```

## Maintenance

If you need to update or reset the ghost job data in the future, you can use the following scripts:
- `update_ghost_job_scores.py`: Updates the ghost job scores for all jobs in the database
- `check_ghost_job_data.py`: Checks the current ghost job data in the database

## Future Enhancements

Potential improvements to consider:
1. Add tooltips to show specific reasons why a job might be a ghost job
2. Add filtering options to allow users to filter out high-risk ghost jobs
3. Implement machine learning to automatically detect ghost jobs based on job description
4. Add a ghost job reporting feature for users to flag suspicious listings
