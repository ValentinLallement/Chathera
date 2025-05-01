"""Ajout contrainte unique user_id/bot_id dans Conversation

Revision ID: d51ff161d6c3
Revises: 67b1515eb76f
Create Date: 2025-05-01 14:59:33.561097
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

# Identifiants de révision
revision: str = 'd51ff161d6c3'
down_revision: Union[str, None] = '67b1515eb76f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""

    # 1. Création de la table bot (nécessaire avant FK bot_id dans conversation)
    op.create_table(
        'bot',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bot_name'), 'bot', ['name'], unique=True)

    # 2. Suppression des données dépendantes pour éviter les violations de contraintes
    op.execute("DELETE FROM message")
    op.execute("DELETE FROM memory")
    op.execute("DELETE FROM futureaction")
    op.execute("DELETE FROM conversation")

    # 3. Ajout de la colonne bot_id dans conversation
    op.add_column('conversation', sa.Column('bot_id', sa.Uuid(), nullable=False))

    # 4. Création de la FK conversation.bot_id → bot.id
    op.create_foreign_key(
        constraint_name='fk_conversation_bot_id',
        source_table='conversation',
        referent_table='bot',
        local_cols=['bot_id'],
        remote_cols=['id']
    )

    # 5. Ajout de la contrainte d'unicité sur le couple (user_id, bot_id)
    op.create_unique_constraint(
        constraint_name='uq_user_bot',
        table_name='conversation',
        columns=['user_id', 'bot_id']
    )

    # 6. Ajout de la colonne conversation_id dans memory
    op.add_column('memory', sa.Column('conversation_id', sa.Uuid(), nullable=False))

    # 7. Création de la FK memory.conversation_id → conversation.id
    op.create_foreign_key(
        constraint_name='fk_memory_conversation_id',
        source_table='memory',
        referent_table='conversation',
        local_cols=['conversation_id'],
        remote_cols=['id']
    )

    # 8. FK memory.user_id → user.id (si elle n’existe pas encore)
    op.create_foreign_key(
        constraint_name='fk_memory_user_id',
        source_table='memory',
        referent_table='user',
        local_cols=['user_id'],
        remote_cols=['id']
    )




def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'user',
        'id',
        existing_type=sa.Integer(),
        type_=sa.UUID(),
        existing_nullable=False,
        autoincrement=True,
        existing_server_default=sa.text('gen_random_uuid()')
    )
    op.drop_constraint(None, 'memory', type_='foreignkey')
    op.drop_constraint(None, 'memory', type_='foreignkey')
    op.drop_column('memory', 'conversation_id')
    op.drop_constraint(None, 'conversation', type_='foreignkey')
    op.drop_constraint('uq_user_bot', 'conversation', type_='unique')
    op.drop_column('conversation', 'bot_id')
    op.drop_index(op.f('ix_bot_name'), table_name='bot')
    op.drop_table('bot')

    # ### end Alembic commands ###
