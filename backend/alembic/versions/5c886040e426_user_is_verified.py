"""user is_verified

Revision ID: 5c886040e426
Revises: 72ee866603e8
Create Date: 2025-06-02 00:14:08.389770

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5c886040e426'
down_revision: Union[str, None] = '72ee866603e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.false()))

def downgrade() -> None:
    op.drop_column('user', 'is_verified')