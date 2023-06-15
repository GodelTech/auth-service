"""create rsa keys table

Revision ID: 6a2b3685577f
Revises: 432f08914e0c
Create Date: 2023-06-15 17:18:45.282222

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a2b3685577f'
down_revision = '432f08914e0c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rsa_keys",
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column("private_key", sa.LargeBinary),
        sa.Column("public_key", sa.LargeBinary),
        sa.Column('n', sa.Integer),
        sa.Column('e', sa.Integer),
    )

def downgrade() -> None:
    op.drop_table("rsa_keys")
