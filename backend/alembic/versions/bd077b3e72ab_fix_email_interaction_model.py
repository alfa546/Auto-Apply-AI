"""fix_email_interaction_model

Revision ID: bd077b3e72ab
Revises: 
Create Date: 2026-07-31 09:52:31.712153

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd077b3e72ab'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('email_interactions', 'sender_email', new_column_name='sender')
    op.alter_column('email_interactions', 'recipient_email', new_column_name='recipient')
    op.alter_column('email_interactions', 'sent_at', new_column_name='received_at')
    
    op.add_column('email_interactions', sa.Column('classification', sa.String(), nullable=True))
    op.add_column('email_interactions', sa.Column('response_draft', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('email_interactions', 'response_draft')
    op.drop_column('email_interactions', 'classification')
    
    op.alter_column('email_interactions', 'received_at', new_column_name='sent_at')
    op.alter_column('email_interactions', 'recipient', new_column_name='recipient_email')
    op.alter_column('email_interactions', 'sender', new_column_name='sender_email')
