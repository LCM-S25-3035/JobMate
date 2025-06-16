Excellent. Based on your confirmation and the document, here’s the draft for **Section 4: Data Gathering & Sources**:

---

### `/docs/04-data-gathering.md`

# Data Gathering & Sources

## Job Postings

**Sources**:

- **Glassdoor**: Scraped using Selenium and BeautifulSoup with authentication and pagination handling.
- **Indeed**: Extracted via Octoparse templates for structured, no-code data extraction.
- **ZipRecruiter and Google Jobs**: Accessed using the JobSpy Python library for multi-source aggregation.

**Data Collected**:

- Job Title
- Company Name
- Location
- Salary
- Job Description
- Posting Date
- Required Skills (via LLM extraction)
- Experience Level, Contract Type, Education (via NLP)

**Volume**: Over 14,000 job listings aggregated.

## Resumes

**Source**:

- Direct uploads from users.
- Pre-collected dataset of 228 resumes (IT professionals in Ontario).

**Processing**:

- Resume parser converts Word files into structured JSON.
- Extracts sections: Summary, Skills, Experience, Education.
- Uses NLP for keyword extraction, skill categorization, and experience quantification.

**Challenges**:

- Inconsistent formatting, images, missing education or experience sections.
- Enhancements planned for improved parser coverage (e.g., soft skills, action verbs).

## Tools & Technologies Used

- **Selenium + BeautifulSoup**: Custom web scraping for Glassdoor.
- **Octoparse**: No-code scraping for Indeed.
- **JobSpy**: Multi-platform job aggregation.
- **Python Orchestrator**: Coordinates parallel and sequential data workflows.
- **MongoDB**: Flexible, JSON-like document store for job listings and resume data.
- **LLM (via Ollama)**: Extracts job attributes like must-have skills and education level.
