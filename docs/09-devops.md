Perfect, thanks! Here's the finalized draft for **Section 9: DevOps & Deployment Plan** based on your deployment strategy:

---

### `/docs/09-devops.md`

# DevOps & Deployment Plan

## Infrastructure & Hosting

- **Deployment Platform**: **AWS**

  - Hosts the application backend, frontend, and database.
  - Services may include EC2 (compute), RDS (PostgreSQL), and S3 (for static assets or backups).

## Containerization

- **Tool**: **Docker Compose**

  - Orchestrates services: Flask API, PostgreSQL, MongoDB, and Nginx (optional).
  - Enables isolated environments per tier (dev, staging, prod).

## Environments

- **Development**:

  - Local development with `.env.dev`
  - Debug mode enabled, auto-reloading Flask server

- **Staging**:

  - Mirrors production stack for QA testing
  - Hosted on separate AWS EC2 instance

- **Production**:

  - Hardened environment
  - Monitored and autoscaled on AWS infrastructure

## CI/CD

- **Version Control**: **GitHub**
- **CI/CD Tool**: **GitHub Actions**

  - Runs test suites, linting, and security checks on pull requests
  - Builds and deploys Docker containers to AWS on push to `main` or `release` branches

## Secrets & Config

- **Environment Management**:

  - `.env` files for local development
  - AWS Secrets Manager or SSM (future upgrade) for production

- Sensitive credentials include:

  - Database URIs
  - LLM (Gemini) API keys
  - OAuth credentials (if used)
