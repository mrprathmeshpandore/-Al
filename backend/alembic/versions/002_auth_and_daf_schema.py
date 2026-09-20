"""Auth and DAF Schema migration revision 002

Revision ID: 002_auth_and_daf_schema
Revises: 001_initial_users_and_profiles
Create Date: 2026-09-20 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_auth_and_daf_schema'
down_revision: Union[str, None] = '001_initial_users_and_profiles'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure index on user_profiles user_id for high performance lookups
    op.create_index(op.f('ix_user_profiles_user_id'), 'user_profiles', ['user_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_profiles_user_id'), table_name='user_profiles')
