Perfect, here's the updated breakdown for **Section 5: Architecture & Technology Stack** with your clarifications:

---

### `/docs/05-architecture.md`

# Architecture & Technology Stack

## Overview

JobMate is a web-based platform that integrates AI-driven resume customization and job recommendation capabilities using a modular, scalable architecture.

## Backend

- **Framework**: **Flask**

  - Chosen for its lightweight nature and built-in support for Jinja template engine.
  - Allows seamless embedding of HTML + Bootstrap for dynamic frontend rendering.

- **Alternative Consideration**: FastAPI was considered but not selected due to less native support for embedded templates and synchronous design alignment with Flask's simplicity.

## Frontend

- **Templating**: **Jinja2** (Flask default)
- **Styling**: **Bootstrap 5**

  - Responsive, component-rich UI framework embedded into Flask templates.

## AI/ML Components

- **LLM**: **Gemini (by Google)**

  - Used for resume parsing, keyword extraction, job matching, and ATS optimization.
  - Interfaces with backend via API endpoints or local inference server.

- **NLP Tasks**:

  - Resume keyword tagging
  - Skill categorization
  - Experience and education extraction
  - Job-to-resume match scoring

## Data Pipeline

- **Orchestration**: **Apache Airflow**

  - Manages scraping, parsing, enrichment, and storage workflows.
  - Enables scheduling and monitoring of data updates.

- **Scripts**: Python-based modules for scraping (Selenium, JobSpy), transformation, translation, and insertion.

## Database

- **Type**: **MongoDB Atlas**

  - NoSQL, cloud-hosted database for storing resumes and job listings.
  - Schema-flexible JSON-like documents enable adaptability during iteration.

## Deployment

- Flask app is containerized using Docker and deployed on a cloud provider (TBD).
- LLM integration via Gemini API or local deployment depending on availability and use-case.
