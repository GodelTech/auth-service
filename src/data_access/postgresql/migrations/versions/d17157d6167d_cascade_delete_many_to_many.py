"""cascade delete many to many

Revision ID: d17157d6167d
Revises: d9002b7cfc73
Create Date: 2023-02-02 11:04:37.810495

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd17157d6167d'
down_revision = 'd9002b7cfc73'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('permissions_groups_group_id_fkey', 'permissions_groups', type_='foreignkey')
    op.drop_constraint('permissions_groups_permission_id_fkey', 'permissions_groups', type_='foreignkey')
    op.create_foreign_key(None, 'permissions_groups', 'groups', ['group_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'permissions_groups', 'permissions', ['permission_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('permissions_roles_role_id_fkey', 'permissions_roles', type_='foreignkey')
    op.drop_constraint('permissions_roles_permission_id_fkey', 'permissions_roles', type_='foreignkey')
    op.create_foreign_key(None, 'permissions_roles', 'roles', ['role_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'permissions_roles', 'permissions', ['permission_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('users_groups_group_id_fkey', 'users_groups', type_='foreignkey')
    op.drop_constraint('users_groups_user_id_fkey', 'users_groups', type_='foreignkey')
    op.create_foreign_key(None, 'users_groups', 'groups', ['group_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'users_groups', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('users_roles_user_id_fkey', 'users_roles', type_='foreignkey')
    op.drop_constraint('users_roles_role_id_fkey', 'users_roles', type_='foreignkey')
    op.create_foreign_key(None, 'users_roles', 'roles', ['role_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'users_roles', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users_roles', type_='foreignkey')
    op.drop_constraint(None, 'users_roles', type_='foreignkey')
    op.create_foreign_key('users_roles_role_id_fkey', 'users_roles', 'roles', ['role_id'], ['id'])
    op.create_foreign_key('users_roles_user_id_fkey', 'users_roles', 'users', ['user_id'], ['id'])
    op.drop_constraint(None, 'users_groups', type_='foreignkey')
    op.drop_constraint(None, 'users_groups', type_='foreignkey')
    op.create_foreign_key('users_groups_user_id_fkey', 'users_groups', 'users', ['user_id'], ['id'])
    op.create_foreign_key('users_groups_group_id_fkey', 'users_groups', 'groups', ['group_id'], ['id'])
    op.drop_constraint(None, 'permissions_roles', type_='foreignkey')
    op.drop_constraint(None, 'permissions_roles', type_='foreignkey')
    op.create_foreign_key('permissions_roles_permission_id_fkey', 'permissions_roles', 'permissions', ['permission_id'], ['id'])
    op.create_foreign_key('permissions_roles_role_id_fkey', 'permissions_roles', 'roles', ['role_id'], ['id'])
    op.drop_constraint(None, 'permissions_groups', type_='foreignkey')
    op.drop_constraint(None, 'permissions_groups', type_='foreignkey')
    op.create_foreign_key('permissions_groups_permission_id_fkey', 'permissions_groups', 'permissions', ['permission_id'], ['id'])
    op.create_foreign_key('permissions_groups_group_id_fkey', 'permissions_groups', 'groups', ['group_id'], ['id'])
    # ### end Alembic commands ###
