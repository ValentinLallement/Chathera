"""Merge multiple heads

Revision ID: 88b300987b56
Revises: 7f4aab749e89, e3320be4d62b
Create Date: 2025-05-25 11:13:37.768497

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88b300987b56'
down_revision: Union[str, None] = ('7f4aab749e89', 'e3320be4d62b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
