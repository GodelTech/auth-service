"""user update

Revision ID: 9b99cad70dac
Revises: f65efd0ca5d5
Create Date: 2023-02-21 11:51:52.739350

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b99cad70dac'
down_revision = 'f65efd0ca5d5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_passwords',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('value', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('users', sa.Column('password_hash_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('identity_provider_id', sa.Integer(), nullable=True))
    op.alter_column('users', 'phone_number',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('users', 'phone_number_confirmed',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('users', 'two_factors_enabled',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.create_foreign_key(None, 'users', 'user_passwords', ['password_hash_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'users', 'identity_providers', ['identity_provider_id'], ['id'], ondelete='SET NULL')
    op.drop_column('users', 'password_hash')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password_hash', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.alter_column('users', 'two_factors_enabled',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('users', 'phone_number_confirmed',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('users', 'phone_number',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('users', 'identity_provider_id')
    op.drop_column('users', 'password_hash_id')
    op.drop_table('user_passwords')
    # ### end Alembic commands ###