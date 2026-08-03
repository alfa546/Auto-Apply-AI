"""add_gmail_message_id_to_applications

Revision ID: a3f5c8d9e1b2
Revises: bd077b3e72ab
Create Date: 2026-08-03 21:56:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3f5c8d9e1b2'
down_revision: Union[str, Sequence[str], None] = 'bd077b3e72ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add gmail_message_id column to applications table for tracking sent email proof
    op.add_column('applications', sa.Column('gmail_message_id', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('applications', 'gmail_message_id')