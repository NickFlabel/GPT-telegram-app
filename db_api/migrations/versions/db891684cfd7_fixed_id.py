"""fixed id

Revision ID: db891684cfd7
Revises: 24a013fa310f
Create Date: 2023-04-26 15:35:34.223996

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db891684cfd7'
down_revision = '24a013fa310f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('users', 'id', type_=sa.BigInteger())


def downgrade() -> None:
    op.alter_column('users', 'id', type_=sa.Integer())
