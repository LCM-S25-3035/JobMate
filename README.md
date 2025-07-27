# JobMate - AI-Powered Job Matching Platform

JobMate is a modern job matching platform for Ontario's tech sector, built with Flask, Bootstrap, and artificial intelligence.

## ✨ Implemented Features

### 🔐 **Complete Authentication Module**

- ✅ **Dual Login System**: Applicant (Job Seekers) and Recruiter (Hiring Managers)
- ✅ **Registration with Validation**: Responsive forms with real-time validation
- ✅ **Password Reset**: Complete password recovery system
- ✅ **Personalized Dashboards**: Specific interfaces for each user type
- ✅ **Responsive Design**: Modern interface with Bootstrap 5

### 🎨 **User Interface**

- ✅ **Attractive Landing Page**: Homepage with call-to-actions
- ✅ **Bootstrap Templates**: Modern and responsive design
- ✅ **Smart Navigation**: Adaptive menu based on user type
- ✅ **Real-time Validation**: Immediate feedback in forms
- ✅ **Toast Notifications**: Elegant alert system

### 🤖 **AI-Powered Features**

- ✅ **Resume Tailoring**: Customize your resume for specific job postings
- ✅ **ATS Score Analysis**: Get feedback on how your resume will perform with ATS systems
- ✅ **Cover Letter Generation**: AI-generated cover letters based on your resume and the job
- ✅ **One-Click Application**: Apply to jobs directly with tailored materials
- ✅ **Job Recommendations**: Smart matching of your skills with available positions

### 📨 **One-Click Application Feature**

The One-Click Application feature allows job seekers to:

- Tailor their resume and cover letter for a specific job
- Send application directly via email with properly formatted attachments
- Track application status in their dashboard
- Apply to jobs with minimal effort

This feature uses the following MongoDB job fields:

- `job_url_direct`: Direct URL to apply on company website
- `application_email`: Email address for sending applications

### 👥 **User Types**

#### 🎯 **Applicant (Job Seekers)**

- Dashboard with application metrics
- Profile completion progress
- AI recommendations
- Application history
- Resume upload and management
- One-click job applications

#### 🏢 **Recruiter (Hiring Managers)**

- Dashboard with hiring metrics
- Job posting management
- Candidate pipeline
- AI matches for candidates
- Performance analytics

## 🚀 **Quick Start**

```bash
git clone <repo-url>
cd JobMateRefactor
cp env.example .env
./setup.sh full
```

**That's it!** The script automatically detects Docker availability and sets up everything for you.

Access the application at: `http://localhost:5002`

### **Test Credentials**

- **Applicant**: `applicant@demo.com` / `password123`
- **Recruiter**: `recruiter@demo.com` / `password123`

## 🛠️ **Manual Commands**

### **Setup Options**

```bash
./setup.sh full       # Complete setup (recommended)
./setup.sh seed       # Just create test data
./setup.sh help       # Show all options
```

### **Database Seeding**

```bash
python seed.py        # Create test users and data
python seed.py reset  # Reset database (WARNING: deletes all data)
```

### **Environment Control**

```bash
# Force Docker mode
USE_DOCKER=true ./setup.sh full

# Force manual mode
## 🎮 **Using the System**

### For Job Seekers (Applicants)
1. **Registration**: Go to `/auth/register` and select "Job Seeker"
2. **Complete Profile**: Add personal and professional information
3. **Resume Upload**: Upload your CV for AI analysis
4. **Dashboard**: Monitor applications and recommendations
5. **Job Search**: Use the intelligent search system

### For Recruiters (Hiring Managers)
1. **Registration**: Go to `/auth/register` and select "Recruiter"
2. **Initial Setup**: Configure company profile
3. **Post Jobs**: Create and manage job postings
4. **Dashboard**: Monitor candidates and metrics
5. **Candidate Management**: Review applications and AI matches
```

```bash
# Universal seed script (auto-detects environment)
python seed.py

# Legacy manual scripts (still available)
python seed_database.py                     # Manual environment seed
python create_recruiter_user.py             # Create specific recruiter
python create_sample_jobs.py                # SQL sample jobs
python create_mongo_sample_jobs.py          # MongoDB sample jobs
```

8. **Start the application**

```bash
python run.py
```

## 🎯 **Quick Setup Alternatives**

### Universal Setup Script

```bash
# Complete setup (auto-detects Docker/manual)
./setup-universal.sh full

# Force specific environment
USE_DOCKER=true ./setup-universal.sh full   # Force Docker
USE_DOCKER=false ./setup-universal.sh full  # Force manual
```

### Legacy Setup Scripts

```bash
# Manual environment setup
./setup.sh full

# Docker environment setup
./docker-setup.sh full
```

The application will be available at `http://localhost:5002`

## 🎮 **Using the System**

### For Job Seekers (Applicants)

1. **Registration**: Go to `/auth/register` and select "Job Seeker"
2. **Complete Profile**: Add personal and professional information
3. **Resume Upload**: Upload your CV for AI analysis
4. **Dashboard**: Monitor applications and recommendations
5. **Job Search**: Use the intelligent search system

### For Recruiters (Hiring Managers)

1. **Registration**: Go to `/auth/register` and select "Recruiter"
2. **Initial Setup**: Configure company profile
3. **Post Jobs**: Create and manage job postings
4. **Dashboard**: Monitor candidates and metrics
5. **Candidate Management**: Review applications and AI matches

## 🔑 **Test Credentials** (Development)

For easier testing, you can use:

**Test Applicant:**

- Email: `applicant@demo.com`
- Password: `password123`

**Test Recruiter:**

- Email: `recruiter@demo.com`
- Password: `password123`

_Keyboard shortcuts in development environment:_

- `Alt + A`: Fills applicant credentials
- `Alt + R`: Fills recruiter credentials

## 🏗️ **Architecture**

```
JobMateRefactor/
├── app/
│   ├── __init__.py              # Application factory
│   ├── auth/                    # Authentication module
│   │   ├── routes.py           # Login/registration routes
│   │   ├── forms.py            # WTF Forms
│   │   └── __init__.py         # Blueprint
│   ├── main/                   # Main routes
│   │   ├── routes.py           # Dashboard and landing
│   │   └── __init__.py         # Blueprint
│   ├── models/                 # Data models
│   │   ├── user.py            # User model
│   │   ├── job_posting.py     # Job posting model
│   │   └── __init__.py        # Initialization
│   └── [other modules]        # resume, jobs, match, etc.
├── templates/
│   ├── base.html              # Base template
│   ├── auth/                  # Authentication templates
│   │   ├── login.html         # Login page
│   │   ├── register.html      # Registration page
│   │   └── reset_password_request.html
│   ├── dashboard/             # Dashboards
│   │   ├── applicant.html     # Applicant dashboard
│   │   └── recruiter.html     # Recruiter dashboard
│   └── main/
│       └── landing.html       # Landing page
├── static/
│   ├── css/
│   │   └── custom.css         # Custom styles
│   └── js/
│       └── main.js            # Main JavaScript
├── database/                  # Database scripts
├── .github/workflows/         # CI/CD Pipeline
├── config.py                  # Configuration
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Container orchestration
├── Dockerfile                 # Docker image
└── run.py                     # Entry point
```

## 🔧 **Advanced Configuration**

### Main Environment Variables

```env
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@localhost/jobmate
MONGODB_URI=mongodb://localhost:27017/jobmate

# Email (for password reset)
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# AI APIs
GOOGLE_API_KEY=your-google-ai-key
```

### Docker (Optional)

```bash
# Build and run with Docker Compose
./docker-setup.sh full

# Services only (databases)
./docker-setup.sh start-dbs

# View logs
./docker-setup.sh logs [service]

# Open shell in container
./docker-setup.sh shell
```

**Docker Services:**

- **Web App**: `http://localhost:5002`
- **PostgreSQL**: `localhost:5432`
- **MongoDB**: `localhost:27017`
- **Redis**: `localhost:6379`
- **Elasticsearch**: `http://localhost:9200`
- **Kibana**: `http://localhost:5601`

## 🧪 **Testing**

```bash
# Run unit tests
pytest

# Tests with coverage
pytest --cov=app

# Integration tests (Playwright)
playwright test
```

## 📦 **Deployment**

### Production Preparation

1. **Configure production environment variables**
2. **Run database migrations**
3. **Configure reverse proxy (Nginx)**
4. **Configure SSL/TLS**
5. **Configure monitoring**

### CI/CD Pipeline

The project includes a complete GitHub Actions pipeline:

- ✅ Linting and security analysis
- ✅ Unit tests
- ✅ End-to-end tests
- ✅ Docker build
- ✅ Automatic deployment to staging/production

## 🤝 **Contributing**

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## 🆘 **Support**

- **Email**: support@jobmate.ca
- **Documentation**: [Link to docs]
- **Issues**: Use GitHub's issue system

---

**JobMate** - Connecting talent with opportunities through AI 🚀
