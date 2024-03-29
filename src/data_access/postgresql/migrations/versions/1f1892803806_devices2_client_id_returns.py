"""Devices2_client_id_returns

Revision ID: 1f1892803806
Revises: ccf9fffc92bc
Create Date: 2023-02-15 17:20:16.690654

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f1892803806'
down_revision = 'ccf9fffc92bc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('devices', sa.Column('client_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'devices', 'clients', ['client_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'devices', type_='foreignkey')
    op.drop_column('devices', 'client_id')
    # ### end Alembic commands ###
