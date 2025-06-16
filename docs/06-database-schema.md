Thanks for the clarification — that’s an excellent hybrid approach.

Here’s the revised **database architecture** section, reflecting **PostgreSQL** for structured data and **MongoDB** for unstructured or semi-structured input data (scraped job descriptions, resumes, extracted metadata):

---

### `/docs/06-database-schema.md`

# Database Schema & Models

## Database Strategy

- **PostgreSQL**: Primary database for structured entities such as users, roles, permissions, resumes (finalized), applications, recruiter feedback, and AI-generated questions.
- **MongoDB**: Auxiliary storage for unstructured/semi-structured data, such as raw job postings from scraping, parsed resume content, and extracted metadata.

---

## PostgreSQL Schema (Structured Data)

### `users`

```sql
id SERIAL PRIMARY KEY,
email VARCHAR(255) UNIQUE NOT NULL,
password_hash TEXT NOT NULL,
created_at TIMESTAMP DEFAULT NOW(),
last_login TIMESTAMP
```

### `profiles`

```sql
id SERIAL PRIMARY KEY,
user_id INT REFERENCES users(id),
full_name VARCHAR(255),
location VARCHAR(255),
linkedin TEXT,
preferred_titles TEXT[],
preferred_locations TEXT[],
salary_range NUMERIC[]
```

### `roles`

```sql
id SERIAL PRIMARY KEY,
name VARCHAR(50) UNIQUE
```

### `permissions`

```sql
id SERIAL PRIMARY KEY,
role_id INT REFERENCES roles(id),
action TEXT
```

### `resumes`

```sql
id SERIAL PRIMARY KEY,
user_id INT REFERENCES users(id),
type VARCHAR(50), -- original or tailored
content TEXT,
ats_score NUMERIC,
created_at TIMESTAMP DEFAULT NOW()
```

### `jobs`

```sql
id SERIAL PRIMARY KEY,
title VARCHAR(255),
company VARCHAR(255),
location TEXT,
url TEXT,
source VARCHAR(50),
posted_at DATE
```

### `applications`

```sql
id SERIAL PRIMARY KEY,
user_id INT REFERENCES users(id),
job_id INT REFERENCES jobs(id),
resume_id INT REFERENCES resumes(id),
status VARCHAR(50),
applied_at TIMESTAMP DEFAULT NOW()
```

### `recruiter_feedback`

```sql
id SERIAL PRIMARY KEY,
application_id INT REFERENCES applications(id),
recruiter_id INT REFERENCES users(id),
decision VARCHAR(20),
notes TEXT,
reviewed_at TIMESTAMP
```

### `ai_generated_questions`

```sql
id SERIAL PRIMARY KEY,
job_id INT REFERENCES jobs(id),
questions TEXT[],
generated_by VARCHAR(50),
generated_at TIMESTAMP
```

---

## MongoDB Collections (Unstructured/Semi-Structured Data)

### `scraped_jobs`

- Raw job posts scraped from external platforms
- Includes description text, metadata, skill lists (pre-LLM)

### `resume_parsed_data`

- NLP-processed resume data (e.g., JSON output of skills, experience, education)
- Used for matching and internal analysis before being cleaned and saved in PostgreSQL

### `ghost_job_detector`

- Flags for potentially outdated or fake job listings
- Managed by heuristics or LLM review

# Database Schema & Models

## 4. `resumes`

Stores parsed and tailored resumes.

```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "type": String,  // "original" or "tailored"
  "content": String,  // Raw or formatted HTML/Markdown
  "parsed_data": {
    "skills": [String],
    "experience": [Object],
    "education": [Object]
  },
  "ats_score": Number,
  "created_at": Date
}
```

## 5. `jobs`

Stores job postings from multiple sources.

```json
{
  "_id": ObjectId,
  "title": String,
  "company": String,
  "location": String,
  "description": String,
  "keywords": [String],
  "url": String,
  "source": String,  // e.g., "Glassdoor"
  "scraped_at": Date,
  "must_have_skills": [String],
  "nice_to_have_skills": [String],
  "experience_level": String,
  "education_level": String
}
```

## 6. `applications`

Tracks jobs a user has applied to.

```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "job_id": ObjectId,
  "resume_id": ObjectId,
  "status": String,  // "applied", "rejected", "approved"
  "applied_at": Date
}
```

## 7. `ghost_job_detector`

Flags outdated or fake job listings.

```json
{
  "_id": ObjectId,
  "job_id": ObjectId,
  "detected_by": String,  // LLM or heuristic
  "reason": String,
  "flagged_at": Date
}
```
