"""Merge autoapply_feature and cddba9a77f3b branches

Revision ID: c7c02ef66411
Revises: autoapply_feature, cddba9a77f3b
Create Date: 2025-07-17 21:25:30.565888

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7c02ef66411'
down_revision = ('autoapply_feature', 'cddba9a77f3b')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
