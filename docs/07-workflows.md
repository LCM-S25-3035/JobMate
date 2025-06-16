Excellent. Based on your confirmation, here’s the draft for **Section 7: Workflow & User Journeys**:

---

### `/docs/07-workflows.md`

# Workflow & User Journeys

## Applicant Workflow

### 1. Onboarding

- Register via email/password
- Complete profile: full name, location, preferred roles, salary expectations

### 2. Resume Upload & Parsing

- Upload original resume (DOCX, PDF)
- Backend uses LLM (Gemini) to parse and extract skills, education, experience
- Parsed data preview shown for confirmation/editing

### 3. Job Discovery

- User receives job recommendations based on:

  - Skills match
  - Location preferences
  - ATS keyword overlap

### 4. Resume Tailoring

- Select a job to apply for
- JobMate dynamically customizes the resume:

  - Reorders sections
  - Injects missing keywords
  - Generates a professional summary

### 5. Application Submission

- One-click auto-apply (fills job board forms, attaches tailored resume)
- Status updates: applied, pending, rejected, approved

### 6. Feedback & Metrics

- Resume receives ATS compatibility score
- Tracks which tailored resumes perform best
- Optional AI-generated interview questions for practice

---

## Recruiter Workflow

### 1. Login & Dashboard

- Secure login with recruiter role
- View candidate submissions for their job listings

### 2. Candidate Review

- Access parsed/tailored resumes
- View ATS match scores and applicant metadata

### 3. Decision Making

- Approve/reject candidates
- Optionally leave feedback or notes
- Track candidate funnel progression
