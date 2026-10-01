"""Add adaptive question fields to interview_session_questions table

Revision ID: 010_adaptive_questions
Revises: 009_answer_evaluations
Create Date: 2026-09-22 10:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '010_adaptive_questions'
down_revision: Union[str, None] = '009_answer_evaluations'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('interview_sessions', sa.Column('include_adaptive', sa.Boolean(), nullable=False, server_default='1'))
    op.add_column('interview_session_questions', sa.Column('parent_session_question_id', sa.String(length=36), nullable=True))
    op.add_column('interview_session_questions', sa.Column('parent_answer_id', sa.String(length=36), nullable=True))
    op.add_column('interview_session_questions', sa.Column('question_depth', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('interview_session_questions', sa.Column('generated_reason', sa.Text(), nullable=True))
    op.add_column('interview_session_questions', sa.Column('adaptive_type', sa.String(length=30), nullable=False, server_default='MAIN'))

    op.create_foreign_key(
        'fk_isq_parent_session_question',
        'interview_session_questions',
        'interview_session_questions',
        ['parent_session_question_id'],
        ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_isq_parent_answer',
        'interview_session_questions',
        'interview_answers',
        ['parent_answer_id'],
        ['id'],
        ondelete='SET NULL'
    )
    op.create_index(op.f('ix_interview_session_questions_parent_session_question_id'), 'interview_session_questions', ['parent_session_question_id'], unique=False)
    op.create_index(op.f('ix_interview_session_questions_parent_answer_id'), 'interview_session_questions', ['parent_answer_id'], unique=False)
    op.create_index(op.f('ix_interview_session_questions_adaptive_type'), 'interview_session_questions', ['adaptive_type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_interview_session_questions_adaptive_type'), table_name='interview_session_questions')
    op.drop_index(op.f('ix_interview_session_questions_parent_answer_id'), table_name='interview_session_questions')
    op.drop_index(op.f('ix_interview_session_questions_parent_session_question_id'), table_name='interview_session_questions')
    op.drop_constraint('fk_isq_parent_answer', 'interview_session_questions', type_='foreignkey')
    op.drop_constraint('fk_isq_parent_session_question', 'interview_session_questions', type_='foreignkey')
    op.drop_column('interview_session_questions', 'adaptive_type')
    op.drop_column('interview_session_questions', 'generated_reason')
    op.drop_column('interview_session_questions', 'question_depth')
    op.drop_column('interview_session_questions', 'parent_answer_id')
    op.drop_column('interview_session_questions', 'parent_session_question_id')
