"""Add preparation_plans and preparation_tasks tables

Revision ID: 012_ai_preparation_coach
Revises: 011_voice_mode
Create Date: 2026-09-28 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '012_ai_preparation_coach'
down_revision: Union[str, None] = '011_voice_mode'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'preparation_plans',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('plan_type', sa.String(length=20), nullable=False, server_default='DAILY'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='ACTIVE'),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('target_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_preparation_plans_user_id'), 'preparation_plans', ['user_id'], unique=False)
    op.create_index(op.f('ix_preparation_plans_plan_type'), 'preparation_plans', ['plan_type'], unique=False)
    op.create_index(op.f('ix_preparation_plans_status'), 'preparation_plans', ['status'], unique=False)
    op.create_index(op.f('ix_preparation_plans_target_date'), 'preparation_plans', ['target_date'], unique=False)
    op.create_index(op.f('ix_preparation_plans_created_at'), 'preparation_plans', ['created_at'], unique=False)

    op.create_table(
        'preparation_tasks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('plan_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('task_type', sa.String(length=50), nullable=False, server_default='QUESTION_PRACTICE'),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='MEDIUM'),
        sa.Column('estimated_minutes', sa.Integer(), nullable=False, server_default='15'),
        sa.Column('target_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='PENDING'),
        sa.Column('source_type', sa.String(length=50), nullable=True),
        sa.Column('source_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['preparation_plans.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_preparation_tasks_plan_id'), 'preparation_tasks', ['plan_id'], unique=False)
    op.create_index(op.f('ix_preparation_tasks_user_id'), 'preparation_tasks', ['user_id'], unique=False)
    op.create_index(op.f('ix_preparation_tasks_task_type'), 'preparation_tasks', ['task_type'], unique=False)
    op.create_index(op.f('ix_preparation_tasks_target_date'), 'preparation_tasks', ['target_date'], unique=False)
    op.create_index(op.f('ix_preparation_tasks_status'), 'preparation_tasks', ['status'], unique=False)


def downgrade() -> None:
    op.drop_table('preparation_tasks')
    op.drop_table('preparation_plans')
