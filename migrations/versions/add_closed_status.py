"""Add 'closed' status to job_posting enum

Revision ID: add_closed_status
Revises: 
Create Date: 2025-08-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_closed_status'
down_revision = None  # Update this if you have a previous migration
branch_labels = None
depends_on = None

def upgrade():
    """Add 'closed' to the job_status enum"""
    # PostgreSQL: Add new value to existing ENUM type
    op.execute("ALTER TYPE job_status ADD VALUE 'closed'")

def downgrade():
    """Remove 'closed' from the job_status enum"""
    # PostgreSQL doesn't support removing ENUM values easily
    # You would need to recreate the ENUM type and update the column
    # For now, we'll just update any 'closed' statuses to another value
    op.execute("UPDATE job_postings SET status = 'filled' WHERE status = 'closed'")
