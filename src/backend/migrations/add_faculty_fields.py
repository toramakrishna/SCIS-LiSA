"""Add homepage and research_interests to authors

Revision ID: add_faculty_fields
Revises: 
Create Date: 2026-02-02

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_faculty_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to authors table
    op.add_column('authors', sa.Column('homepage', sa.String(500), nullable=True))
    op.add_column('authors', sa.Column('research_interests', sa.Text(), nullable=True))


def downgrade():
    # Remove columns
    op.drop_column('authors', 'research_interests')
    op.drop_column('authors', 'homepage')
