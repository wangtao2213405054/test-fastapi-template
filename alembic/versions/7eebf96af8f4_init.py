"""init

Revision ID: 7eebf96af8f4
Revises: 
Create Date: 2024-07-30 00:19:46.967965

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '7eebf96af8f4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('test_affiliation',
    sa.Column('createTime', sa.DateTime(), nullable=False),
    sa.Column('updateTime', sa.DateTime(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('nodeId', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_affiliation_name'), 'test_affiliation', ['name'], unique=False)
    op.create_index(op.f('ix_test_affiliation_nodeId'), 'test_affiliation', ['nodeId'], unique=False)
    op.create_table('test_menu',
    sa.Column('createTime', sa.DateTime(), nullable=False),
    sa.Column('updateTime', sa.DateTime(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('identifier', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('nodeId', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_menu_identifier'), 'test_menu', ['identifier'], unique=True)
    op.create_index(op.f('ix_test_menu_name'), 'test_menu', ['name'], unique=False)
    op.create_index(op.f('ix_test_menu_nodeId'), 'test_menu', ['nodeId'], unique=False)
    op.create_table('test_role',
    sa.Column('createTime', sa.DateTime(), nullable=False),
    sa.Column('updateTime', sa.DateTime(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('identifier', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('identifierList', sa.JSON(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_role_identifier'), 'test_role', ['identifier'], unique=True)
    op.create_index(op.f('ix_test_role_name'), 'test_role', ['name'], unique=False)
    op.create_table('test_user',
    sa.Column('createTime', sa.DateTime(), nullable=False),
    sa.Column('updateTime', sa.DateTime(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('username', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('mobile', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('avatarUrl', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.Column('roleId', sa.Integer(), nullable=True),
    sa.Column('affiliationId', sa.Integer(), nullable=False),
    sa.Column('password', sa.LargeBinary(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['affiliationId'], ['test_affiliation.id'], ),
    sa.ForeignKeyConstraint(['roleId'], ['test_role.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_user_email'), 'test_user', ['email'], unique=True)
    op.create_index(op.f('ix_test_user_mobile'), 'test_user', ['mobile'], unique=True)
    op.create_index(op.f('ix_test_user_name'), 'test_user', ['name'], unique=False)
    op.create_index(op.f('ix_test_user_username'), 'test_user', ['username'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_test_user_username'), table_name='test_user')
    op.drop_index(op.f('ix_test_user_name'), table_name='test_user')
    op.drop_index(op.f('ix_test_user_mobile'), table_name='test_user')
    op.drop_index(op.f('ix_test_user_email'), table_name='test_user')
    op.drop_table('test_user')
    op.drop_index(op.f('ix_test_role_name'), table_name='test_role')
    op.drop_index(op.f('ix_test_role_identifier'), table_name='test_role')
    op.drop_table('test_role')
    op.drop_index(op.f('ix_test_menu_nodeId'), table_name='test_menu')
    op.drop_index(op.f('ix_test_menu_name'), table_name='test_menu')
    op.drop_index(op.f('ix_test_menu_identifier'), table_name='test_menu')
    op.drop_table('test_menu')
    op.drop_index(op.f('ix_test_affiliation_nodeId'), table_name='test_affiliation')
    op.drop_index(op.f('ix_test_affiliation_name'), table_name='test_affiliation')
    op.drop_table('test_affiliation')
    # ### end Alembic commands ###
