#!/bin/bash

# JobMate Bio Field Migration Setup Script
# This script handles everything needed to add bio fields to the users table

set -e

echo "🚀 JobMate Bio Field Migration Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
print_status "Checking Docker status..."
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Stop existing containers if running
print_status "Stopping existing containers..."
docker-compose down || true

# Build and start PostgreSQL container
print_status "Starting PostgreSQL container..."
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
print_status "Waiting for PostgreSQL to be ready..."
sleep 10

# Check PostgreSQL connection
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U jobmate_user -d jobmate_db >/dev/null 2>&1; then
        print_status "PostgreSQL is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "PostgreSQL failed to start within 30 seconds"
        exit 1
    fi
    sleep 1
done

# Create the migration script content directly in the shell script
print_status "Creating migration script..."
cat > /tmp/bio_migration.py << 'EOF'
#!/usr/bin/env python3
"""
Bio Field Migration Script
Adds bio, skills, and experience_level fields to users table
"""

import os
import sys
import psycopg
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    conn_string = os.environ.get(
        'DATABASE_URL',
        'postgresql://jobmate_user:jobmate_password@localhost:5432/jobmate_db'
    ).replace('postgresql+psycopg://', 'postgresql://')
    return psycopg.connect(conn_string)

def check_columns_exist():
    """Check which bio columns already exist"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name IN ('bio', 'skills', 'experience_level')
                    ORDER BY column_name;
                """)
                return [row[0] for row in cur.fetchall()]
    except Exception as e:
        print(f"Error checking columns: {e}")
        return []

def add_bio_columns():
    """Add bio-related columns to users table"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Add bio column
                cur.execute("""
                    DO $$ 
                    BEGIN 
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name = 'users' AND column_name = 'bio'
                        ) THEN
                            ALTER TABLE users ADD COLUMN bio TEXT;
                            RAISE NOTICE 'Added bio column';
                        END IF;
                    END $$;
                """)
                
                # Add skills column
                cur.execute("""
                    DO $$ 
                    BEGIN 
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name = 'users' AND column_name = 'skills'
                        ) THEN
                            ALTER TABLE users ADD COLUMN skills VARCHAR(500);
                            RAISE NOTICE 'Added skills column';
                        END IF;
                    END $$;
                """)
                
                # Add experience_level column
                cur.execute("""
                    DO $$ 
                    BEGIN 
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name = 'users' AND column_name = 'experience_level'
                        ) THEN
                            ALTER TABLE users ADD COLUMN experience_level VARCHAR(50);
                            RAISE NOTICE 'Added experience_level column';
                        END IF;
                    END $$;
                """)
                
                conn.commit()
                return True
                
    except Exception as e:
        print(f"Error adding columns: {e}")
        return False

def update_migration_state():
    """Update Alembic migration state"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Check if alembic_version table exists
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'alembic_version'
                    );
                """)
                
                if cur.fetchone()[0]:
                    # Update to the bio migration revision
                    cur.execute("""
                        UPDATE alembic_version SET version_num = 'f1a2b3c4d5e6' 
                        WHERE version_num = 'c57186012b4d';
                    """)
                    if cur.rowcount > 0:
                        print("Updated migration state to f1a2b3c4d5e6")
                    else:
                        print("Migration state was already up to date")
                else:
                    print("Alembic version table not found - skipping migration state update")
                
                conn.commit()
                return True
                
    except Exception as e:
        print(f"Error updating migration state: {e}")
        return False

def main():
    print("🔍 Checking existing bio columns...")
    existing = check_columns_exist()
    
    if len(existing) == 3:
        print("✅ All bio columns already exist:")
        for col in existing:
            print(f"   - {col}")
        return True
    
    print("📝 Adding missing bio columns...")
    if add_bio_columns():
        print("✅ Successfully added bio columns")
        
        # Verify columns were added
        final_columns = check_columns_exist()
        if len(final_columns) == 3:
            print("🎉 Verification successful! All columns present:")
            for col in final_columns:
                print(f"   - {col}")
            
            # Update migration state
            update_migration_state()
            return True
        else:
            print("⚠️  Some columns may not have been added")
            return False
    else:
        print("❌ Failed to add bio columns")
        return False

if __name__ == '__main__':
    if main():
        print("🎉 Bio migration completed successfully!")
    else:
        print("❌ Bio migration failed!")
        sys.exit(1)
EOF

# Copy the migration script to the container and run it
print_status "Running bio field migration..."
docker cp /tmp/bio_migration.py $(docker-compose ps -q postgres):/tmp/bio_migration.py

# Grant privileges first
print_status "Ensuring proper database privileges..."
docker-compose exec -T postgres psql -U postgres -d jobmate_db -c "
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO jobmate_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO jobmate_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO jobmate_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO jobmate_user;
" 2>/dev/null || print_warning "Could not grant privileges using postgres user"

# Run the migration script
if docker-compose exec -T postgres python3 /tmp/bio_migration.py; then
    print_status "✅ Bio field migration completed successfully!"
else
    print_error "Migration failed, trying manual approach..."
    
    # Manual column addition as fallback
    docker-compose exec -T postgres psql -U jobmate_user -d jobmate_db -c "
    ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT;
    ALTER TABLE users ADD COLUMN IF NOT EXISTS skills VARCHAR(500);
    ALTER TABLE users ADD COLUMN IF NOT EXISTS experience_level VARCHAR(50);
    " || {
        print_error "Manual migration also failed"
        exit 1
    }
    print_status "✅ Manual migration completed!"
fi

# Verify the final result
print_status "Verifying bio-related columns in users table..."
COLUMNS=$(docker-compose exec -T postgres psql -U jobmate_user -d jobmate_db -t -c "
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('bio', 'skills', 'experience_level')
ORDER BY column_name;
")

if [[ -n "$COLUMNS" ]]; then
    print_status "✅ Bio-related columns verified:"
    echo "$COLUMNS"
else
    print_error "❌ No bio-related columns found in users table"
    exit 1
fi

# Clean up temporary file
rm -f /tmp/bio_migration.py

print_status "🎉 Bio field migration setup completed successfully!"
print_status "📋 Summary:"
print_status "   - bio (TEXT) - User biography/description"
print_status "   - skills (VARCHAR(500)) - User skills list"  
print_status "   - experience_level (VARCHAR(50)) - User experience level"
print_status ""
print_status "🚀 Next steps:"
print_status "1. Start your application: docker-compose up -d"
print_status "2. The bio fields are ready to use in your User model"
print_status "" 