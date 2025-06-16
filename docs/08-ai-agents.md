Perfect. Based on your confirmation, here's the finalized draft for **Section 8: AI Agents & Automation**:

---

### `/docs/08-ai-agents.md`

# AI Agents & Automation

## Overview

JobMate uses multiple task-specific AI agents powered by Gemini to streamline resume analysis, job recommendation, and application automation. Each agent operates independently but integrates with the main application workflow via the backend.

---

## 1. Resume Parser Agent

- **Input**: Uploaded DOCX/PDF resume
- **Tasks**:

  - Extracts structured fields: skills, experience, education, certifications
  - Converts unstructured resume to structured JSON
  - Detects action verbs, bullet points, and missing sections

- **Output**: Parsed JSON stored in MongoDB

---

## 2. Job Scraper Agent

- **Input**: Search keywords and job platforms
- **Tasks**:

  - Collects postings from platforms like Glassdoor, Indeed, ZipRecruiter
  - Uses tools: Selenium, JobSpy, Octoparse
  - Stores raw job descriptions with metadata

- **Output**: Job listings stored in MongoDB

---

## 3. Job Description Analyzer

- **Input**: Raw job description
- **Tasks**:

  - Extracts must-have and nice-to-have skills
  - Identifies required experience, education, and contract type
  - Uses LLM (Gemini) for semantic understanding

- **Output**: Enriched job profile stored in MongoDB

---

## 4. Resume Customizer Agent

- **Input**: Parsed resume + target job description
- **Tasks**:

  - Matches resume content to job keywords
  - Reorders sections and injects missing skills
  - Crafts custom professional summary

- **Output**: Tailored resume (HTML/Markdown)

---

## 5. Match Scoring Agent

- **Input**: Tailored resume + job description
- **Tasks**:

  - Calculates ATS compatibility score
  - Identifies keyword matches and formatting issues
  - Suggests improvements

- **Output**: Score and feedback report

---

## 6. Ghost Job Detector

- **Input**: Job metadata and posting age
- **Tasks**:

  - Detects outdated, duplicate, or suspicious job posts
  - Flags listings based on heuristics and LLM evaluations

- **Output**: Flagged job entries in MongoDB

---

## 7. Interview Question Generator

- **Input**: Job description + applicant’s resume
- **Tasks**:

  - Uses Gemini to create personalized interview questions
  - Focuses on likely topics based on job requirements and applicant’s gaps

- **Output**: List of questions stored in PostgreSQL for user review
