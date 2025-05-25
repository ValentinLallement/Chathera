"""Recreate future_actions table

Revision ID: 7f4aab749e89
Revises: e3320be4d62b
Create Date: 2025-05-25 11:09:35.144720

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

revision = '7f4aab749e89'
down_revision = '7aebb578638d'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'future_actions',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('conversation_id', pg.UUID(as_uuid=True), sa.ForeignKey('conversation.id', ondelete='CASCADE'), nullable=False),
        sa.Column('action', sa.String, nullable=False),
        sa.Column('date_action', sa.DateTime, nullable=False),
        sa.Column('future_message', sa.Text, nullable=False),
        sa.Column('condition', pg.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
    )

def downgrade() -> None:
    op.drop_table('future_actions')
