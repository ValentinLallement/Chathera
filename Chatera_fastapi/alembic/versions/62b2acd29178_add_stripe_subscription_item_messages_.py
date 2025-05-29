"""Add stripe_subscription_item_messages and stripe_subscription_item_bots columns to subscription

Revision ID: 62b2acd29178
Revises: 2d89ee1be6ed
Create Date: 2025-05-29 15:20:45.765423

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62b2acd29178'
down_revision: Union[str, None] = '2d89ee1be6ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('subscription', sa.Column('stripe_subscription_item_messages', sa.String(), nullable=True))
    op.add_column('subscription', sa.Column('stripe_subscription_item_bots', sa.String(), nullable=True))

def downgrade():
    op.drop_column('subscription', 'stripe_subscription_item_messages')
    op.drop_column('subscription', 'stripe_subscription_item_bots')