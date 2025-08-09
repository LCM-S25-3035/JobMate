"""
Enhanced Profile Migration
Add profile_picture field to User model for profile enhancements
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# Revision identifiers
revision = 'enhanced_profile_001'
down_revision = 'c7c02ef66411'  # Use the latest migration
branch_labels = None 
depends_on = None

def upgrade():
    """Add profile_picture field to users table"""
    try:
        # Add profile_picture column to users table
        op.add_column('users', sa.Column('profile_picture', sa.String(200), nullable=True, default='uploads/profiles/default.png'))
        
        # Add social media fields if desired
        op.add_column('users', sa.Column('linkedin_url', sa.String(200), nullable=True))
        op.add_column('users', sa.Column('github_url', sa.String(200), nullable=True))
        op.add_column('users', sa.Column('portfolio_url', sa.String(200), nullable=True))
        
        print("✅ Enhanced profile fields added successfully")
        
    except Exception as e:
        print(f"⚠️  Migration might have already been applied or error occurred: {e}")

def downgrade():
    """Remove profile_picture field from users table"""
    try:
        # Remove the added columns
        op.drop_column('users', 'profile_picture')
        op.drop_column('users', 'linkedin_url')
        op.drop_column('users', 'github_url')
        op.drop_column('users', 'portfolio_url')
        
        print("✅ Enhanced profile fields removed successfully")
        
    except Exception as e:
        print(f"⚠️  Error during downgrade: {e}")
