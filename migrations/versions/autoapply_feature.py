"""AutoApply Feature Migration

Revision ID: autoapply_feature
Revises: 
Create Date: 2025-06-23 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'autoapply_feature'
down_revision = None  # Update this with the previous migration's revision id
branch_labels = None
depends_on = None


def upgrade():
    # Instead of creating PostgreSQL enum types, we'll use string types with check constraints
    # This avoids potential conflicts with existing enum types
    
    # Create auto_apply_settings table
    op.create_table(
        'auto_apply_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('max_daily', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('min_match_score', sa.Integer(), nullable=False, server_default='80'),
        sa.Column('cover_letter_type', sa.String(20), nullable=False, server_default="'generic'"),
        sa.Column('preferred_job_types', sa.String(20), nullable=False, server_default="'all'"),
        sa.Column('additional_preferences', sa.Text(), nullable=True),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('today_application_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
        sa.CheckConstraint("cover_letter_type IN ('none', 'generic', 'custom')", name='check_cover_letter_type'),
        sa.CheckConstraint("preferred_job_types IN ('all', 'full_time', 'remote', 'full_time_remote')", name='check_preferred_job_types')
    )
    
    # Add auto-apply related columns to applications table
    with op.batch_alter_table('applications', schema=None) as batch_op:
        batch_op.add_column(sa.Column('auto_applied', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('auto_apply_match_score', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('auto_apply_batch_id', sa.String(length=36), nullable=True))


def downgrade():
    # Remove auto-apply related columns from applications table
    with op.batch_alter_table('applications', schema=None) as batch_op:
        batch_op.drop_column('auto_apply_batch_id')
        batch_op.drop_column('auto_apply_match_score')
        batch_op.drop_column('auto_applied')
    
    # Drop auto_apply_settings table (this will automatically drop the check constraints)
    op.drop_table('auto_apply_settings')
    
    # Note: We don't need to drop enum types since we're using string with check constraints instead
