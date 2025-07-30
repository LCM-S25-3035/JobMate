# JobMate Setup Guide for New Developers

## Quick Setup (5 minutes)

### 1. Clone and Install Dependencies
```bash
git clone <repository-url>
cd JobMateRefactor
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your database credentials
# The DATABASE_URL should point to the shared Supabase instance
```

### 3. Database Setup
```bash
# Create database tables (this is the key step!)
flask db upgrade

# Verify setup
python -c "
from app import create_app, db
from app.models.user import User
app = create_app()
with app.app_context():
    print('Users in database:', User.query.count())
    print('✅ Database setup successful!')
"
```

### 4. Run Application
```bash
python run.py
```

## Common Issues

### "Table 'users' doesn't exist"
**Solution:** Run `flask db upgrade` to create database tables

### "Connection refused" 
**Solution:** Check your `.env` file has the correct DATABASE_URL

### "Module not found"
**Solution:** Make sure virtual environment is activated: `source venv/bin/activate`

## Database Info
- **User/Profile Data:** Supabase PostgreSQL
- **Jobs Data:** MongoDB  
- **Database Tables:** Created automatically via Flask migrations
