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
    # Create enum type for cover letter types
    op.execute("CREATE TYPE cover_letter_types AS ENUM ('none', 'generic', 'custom')")
    
    # Create enum type for preferred job types
    op.execute(
        "CREATE TYPE preferred_job_types AS ENUM ('all', 'full_time', 'remote', 'full_time_remote')"
    )
    
    # Create auto_apply_settings table
    op.create_table(
        'auto_apply_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('max_daily', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('min_match_score', sa.Integer(), nullable=False, server_default='80'),
        sa.Column('cover_letter_type', sa.Enum('none', 'generic', 'custom', name='cover_letter_types'), 
                  nullable=False, server_default='generic'),
        sa.Column('preferred_job_types', sa.Enum('all', 'full_time', 'remote', 'full_time_remote', 
                                              name='preferred_job_types'), 
                  nullable=False, server_default='all'),
        sa.Column('additional_preferences', sa.Text(), nullable=True),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('today_application_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
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
    
    # Drop auto_apply_settings table
    op.drop_table('auto_apply_settings')
    
    # Drop enum types
    op.execute("DROP TYPE preferred_job_types")
    op.execute("DROP TYPE cover_letter_types")
