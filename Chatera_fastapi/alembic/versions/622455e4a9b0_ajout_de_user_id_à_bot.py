from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '622455e4a9b0'
down_revision: Union[str, None] = '4e8ea88d6a5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    # Vérifie si la colonne 'user_id' existe déjà avant d'essayer de l'ajouter
    connection = op.get_bind()
    result = connection.execute(
        sa.text("SELECT column_name FROM information_schema.columns WHERE table_name = 'bot' AND column_name = 'user_id'")
    )
    if not result.fetchone():  # Si 'user_id' n'existe pas
        op.add_column('bot', sa.Column('user_id', sa.UUID(), nullable=False))
        op.create_foreign_key('fk_bot_user', 'bot', 'user', ['user_id'], ['id'])
    
    # Supprimer l'index sur name dans bot si nécessaire
    op.drop_index('ix_bot_name', table_name='bot')

def downgrade() -> None:
    """Downgrade schema."""
    # Supprimer la clé étrangère entre bot et user
    op.drop_constraint('fk_bot_user', 'bot', type_='foreignkey')
    # Supprimer la colonne user_id
    op.drop_column('bot', 'user_id')
    # Recréer l'index sur name dans bot si nécessaire
    op.create_index('ix_bot_name', 'bot', ['name'], unique=False)
