"""Initial migration for users and user_profiles tables

Revision ID: 001_initial_users_and_profiles
Revises: 
Create Date: 2026-09-20 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_users_and_profiles'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('date_of_birth', sa.String(length=50), nullable=True),
        sa.Column('home_state', sa.String(length=100), nullable=True),
        sa.Column('district', sa.String(length=100), nullable=True),
        sa.Column('current_city', sa.String(length=100), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('education_data', sa.JSON(), nullable=True),
        sa.Column('upsc_journey_data', sa.JSON(), nullable=True),
        sa.Column('interests', sa.JSON(), nullable=True),
        sa.Column('perspective', sa.JSON(), nullable=True),
        sa.Column('profile_completion', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )


def downgrade() -> None:
    op.drop_table('user_profiles')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
