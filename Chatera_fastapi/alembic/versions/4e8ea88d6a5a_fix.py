# -*- coding: utf-8 -*-
"""fix

Révision ID: 4e8ea88d6a5a
Révise: da13029c85db
Date de création: 2025-05-01 15:30:43.562701
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# révision des identifiants de version pour Alembic
revision: str = '4e8ea88d6a5a'
down_revision: Union[str, None] = 'da13029c85db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Supprimer toutes les données de la table "user" et réinitialiser les séquences (pour les clés primaires auto-incrémentées)
    op.execute('TRUNCATE TABLE "user" RESTART IDENTITY CASCADE;')

    # Supprimer la contrainte d'unicité existante sur "bot"
    op.drop_constraint('uq_user_bot_name', 'bot', type_='unique')

    # ### Ajouter des colonnes ou autres modifications ici si nécessaire ###
    # Par exemple, si vous souhaitez ajouter de nouvelles colonnes plus tard :
    # op.add_column('user', sa.Column('new_column', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Rétablir la contrainte d'unicité sur "user_id" et "name" dans la table "bot"
    op.create_unique_constraint('uq_user_bot_name', 'bot', ['user_id', 'name'])

    # ### Supprimer les colonnes ou autres modifications si nécessaire ###
    # Par exemple, si vous avez ajouté une colonne dans l'upgrade, vous pouvez la supprimer ici :
    # op.drop_column('user', 'new_column')
