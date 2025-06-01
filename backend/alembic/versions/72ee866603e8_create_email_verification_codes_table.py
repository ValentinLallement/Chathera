"""create email_verification_codes table

Revision ID: 72ee866603e8
Revises: 38e31e572823
Create Date: 2025-06-01 23:59:42.006297
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime, timedelta

# revision identifiers, used by Alembic.
revision = '72ee866603e8'
down_revision = '38e31e572823'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'email_verification_codes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('email', sa.String(), nullable=False, index=True),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(), nullable=False, server_default=sa.text("(now() + interval '10 minutes')"))
    )


def downgrade() -> None:
    op.drop_table('email_verification_codes')
