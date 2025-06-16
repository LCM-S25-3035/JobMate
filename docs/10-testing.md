Understood. Here's the final draft for **Section 10: Testing Strategy & Metrics**, focused exclusively on **End-to-End (E2E) Testing**:

---

### `/docs/10-testing.md`

# Testing Strategy & Metrics

## Testing Scope

### End-to-End (E2E) Testing

- **Purpose**: Validate that the full JobMate workflow functions correctly from the user's perspective.
- **Coverage**:

  - Applicant onboarding (registration, profile setup)
  - Resume upload and parsing
  - Job recommendation flow
  - Resume tailoring and preview
  - Job application submission
  - Recruiter login and candidate approval

- **Tools**:

  - **Playwright** (preferred) or **Selenium**
  - Tests scripted in Python or JavaScript

- **Execution**:

  - Triggered via GitHub Actions on staging deploys
  - Mock data for job listings and resumes included

- **Environments**:

  - Executed in isolated staging environment with seeded data

## Metrics & Goals

- **Test Completion Time**: < 5 minutes per full run
- **Minimum Functional Coverage**: All major user journeys validated before production push
- **Failure Logging**:

  - Screenshots and logs stored in GitHub Actions artifacts
  - Slack/email alerts on failures (future)
