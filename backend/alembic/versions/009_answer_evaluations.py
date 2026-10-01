"""Create interview_answer_evaluations table

Revision ID: 009_answer_evaluations
Revises: 008_interview_sessions
Create Date: 2026-09-21 23:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '009_answer_evaluations'
down_revision: Union[str, None] = '008_interview_sessions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'interview_answer_evaluations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('answer_id', sa.String(length=36), nullable=False),
        sa.Column('content_score', sa.Float(), nullable=False),
        sa.Column('content_feedback', sa.Text(), nullable=False),
        sa.Column('clarity_score', sa.Float(), nullable=False),
        sa.Column('clarity_feedback', sa.Text(), nullable=False),
        sa.Column('depth_score', sa.Float(), nullable=False),
        sa.Column('depth_feedback', sa.Text(), nullable=False),
        sa.Column('reasoning_score', sa.Float(), nullable=False),
        sa.Column('reasoning_feedback', sa.Text(), nullable=False),
        sa.Column('balance_score', sa.Float(), nullable=False),
        sa.Column('balance_feedback', sa.Text(), nullable=False),
        sa.Column('communication_score', sa.Float(), nullable=False),
        sa.Column('communication_feedback', sa.Text(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('overall_feedback', sa.Text(), nullable=False),
        sa.Column('strengths', sa.JSON(), nullable=False),
        sa.Column('areas_to_improve', sa.JSON(), nullable=False),
        sa.Column('suggested_answer', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['answer_id'], ['interview_answers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('answer_id', name='uq_interview_answer_evaluations_answer_id')
    )
    op.create_index(op.f('ix_interview_answer_evaluations_answer_id'), 'interview_answer_evaluations', ['answer_id'], unique=True)
    op.create_index(op.f('ix_interview_answer_evaluations_overall_score'), 'interview_answer_evaluations', ['overall_score'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_interview_answer_evaluations_overall_score'), table_name='interview_answer_evaluations')
    op.drop_index(op.f('ix_interview_answer_evaluations_answer_id'), table_name='interview_answer_evaluations')
    op.drop_table('interview_answer_evaluations')
