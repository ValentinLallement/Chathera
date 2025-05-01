"""user contraint for bots

Revision ID: da13029c85db
Revises: d51ff161d6c3
Create Date: 2025-05-01 15:17:17.422694
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'da13029c85db'
down_revision: Union[str, None] = 'd51ff161d6c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('bot', sa.Column('user_id', sa.Uuid(), nullable=False))
    op.drop_index('ix_bot_name', table_name='bot')
    op.create_index(op.f('ix_bot_name'), 'bot', ['name'], unique=False)
    op.create_foreign_key("fk_bot_user_id", 'bot', 'user', ['user_id'], ['id'])
    op.create_unique_constraint("uq_user_bot_name", "bot", ["user_id", "name"])

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_user_bot_name", "bot", type_="unique")
    op.drop_constraint("fk_bot_user_id", "bot", type_='foreignkey')
    op.drop_index(op.f('ix_bot_name'), table_name='bot')
    op.create_index('ix_bot_name', 'bot', ['name'], unique=True)
    op.drop_column('bot', 'user_id')
