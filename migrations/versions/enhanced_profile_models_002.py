"""Enhanced Profile Models Migration
Add tables for user experience, education, certifications, skills, and social links

Revision ID: enhanced_profile_models_002
Revises: enhanced_profile_001
Create Date: 2025-01-11 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'enhanced_profile_models_002'
down_revision = 'enhanced_profile_001'
branch_labels = None
depends_on = None


def upgrade():
    """Add enhanced profile tables"""
    try:
        # Create user_experiences table
        op.create_table('user_experiences',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('job_title', sa.String(length=100), nullable=False),
            sa.Column('company', sa.String(length=100), nullable=False),
            sa.Column('location', sa.String(length=100), nullable=True),
            sa.Column('start_date', sa.Date(), nullable=False),
            sa.Column('end_date', sa.Date(), nullable=True),
            sa.Column('is_current', sa.Boolean(), nullable=True, default=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
            sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Create user_educations table
        op.create_table('user_educations',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('degree', sa.String(length=100), nullable=False),
            sa.Column('institution', sa.String(length=100), nullable=False),
            sa.Column('field_of_study', sa.String(length=100), nullable=True),
            sa.Column('location', sa.String(length=100), nullable=True),
            sa.Column('start_year', sa.Integer(), nullable=True),
            sa.Column('end_year', sa.Integer(), nullable=True),
            sa.Column('gpa', sa.String(length=10), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
            sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Create user_certifications table
        op.create_table('user_certifications',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('issuing_organization', sa.String(length=100), nullable=False),
            sa.Column('issue_date', sa.Date(), nullable=True),
            sa.Column('expiry_date', sa.Date(), nullable=True),
            sa.Column('credential_id', sa.String(length=100), nullable=True),
            sa.Column('credential_url', sa.String(length=200), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
            sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Create user_skills table
        op.create_table('user_skills',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('proficiency', sa.Enum('beginner', 'intermediate', 'advanced', 'expert', name='skill_proficiency'), nullable=False, default='intermediate'),
            sa.Column('years_experience', sa.Integer(), nullable=True),
            sa.Column('category', sa.String(length=50), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
            sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'name', name='unique_user_skill')
        )
        
        # Create user_social_links table
        op.create_table('user_social_links',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('platform', sa.String(length=50), nullable=False),
            sa.Column('url', sa.String(length=200), nullable=False),
            sa.Column('display_name', sa.String(length=100), nullable=True),
            sa.Column('is_public', sa.Boolean(), nullable=True, default=True),
            sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
            sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'platform', name='unique_user_platform')
        )
        
        # Add additional fields to users table if they don't exist
        try:
            op.add_column('users', sa.Column('professional_title', sa.String(100), nullable=True))
            op.add_column('users', sa.Column('twitter_url', sa.String(200), nullable=True))
            op.add_column('users', sa.Column('job_search_status', sa.String(50), nullable=True, default='not_looking'))
            op.add_column('users', sa.Column('show_salary_expectations', sa.Boolean(), nullable=True, default=False))
            op.add_column('users', sa.Column('allow_recruiter_contact', sa.Boolean(), nullable=True, default=True))
        except Exception as e:
            print(f"Note: Some user table columns may already exist: {e}")
        
        print("✅ Enhanced profile models created successfully")
        
    except Exception as e:
        print(f"⚠️  Migration error (tables may already exist): {e}")


def downgrade():
    """Remove enhanced profile tables"""
    try:
        # Drop tables in reverse order to handle foreign key constraints
        op.drop_table('user_social_links')
        op.drop_table('user_skills')
        op.drop_table('user_certifications')
        op.drop_table('user_educations')
        op.drop_table('user_experiences')
        
        # Remove added columns from users table
        try:
            op.drop_column('users', 'professional_title')
            op.drop_column('users', 'twitter_url')
            op.drop_column('users', 'job_search_status')
            op.drop_column('users', 'show_salary_expectations')
            op.drop_column('users', 'allow_recruiter_contact')
        except Exception as e:
            print(f"Note: Some user table columns may not exist: {e}")
        
        print("✅ Enhanced profile models removed successfully")
        
    except Exception as e:
        print(f"⚠️  Downgrade error: {e}")
