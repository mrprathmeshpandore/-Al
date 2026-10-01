"""Create interview_sessions, interview_session_questions, and interview_answers tables

Revision ID: 008_interview_sessions
Revises: 007_current_affairs_table
Create Date: 2026-09-21 23:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '008_interview_sessions'
down_revision: Union[str, None] = '007_current_affairs_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create interview_sessions table
    op.create_table(
        'interview_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='CREATED'),
        sa.Column('interview_type', sa.String(length=50), nullable=False, server_default='FULL_INTERVIEW'),
        sa.Column('total_questions', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('current_question_index', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_interview_sessions_user_id'), 'interview_sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_interview_sessions_status'), 'interview_sessions', ['status'], unique=False)
    op.create_index(op.f('ix_interview_sessions_interview_type'), 'interview_sessions', ['interview_type'], unique=False)
    op.create_index(op.f('ix_interview_sessions_created_at'), 'interview_sessions', ['created_at'], unique=False)

    # 2. Create interview_session_questions table
    op.create_table(
        'interview_session_questions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('question_id', sa.String(length=36), nullable=True),
        sa.Column('sequence_number', sa.Integer(), nullable=False),
        sa.Column('question_status', sa.String(length=30), nullable=False, server_default='PENDING'),
        sa.Column('presented_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('answered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['interview_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['interview_questions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_interview_session_questions_session_id'), 'interview_session_questions', ['session_id'], unique=False)
    op.create_index(op.f('ix_interview_session_questions_question_id'), 'interview_session_questions', ['question_id'], unique=False)
    op.create_index(op.f('ix_interview_session_questions_question_status'), 'interview_session_questions', ['question_status'], unique=False)

    # 3. Create interview_answers table
    op.create_table(
        'interview_answers',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_question_id', sa.String(length=36), nullable=False),
        sa.Column('answer_text', sa.Text(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('answer_duration_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['session_question_id'], ['interview_session_questions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_interview_answers_session_question_id'), 'interview_answers', ['session_question_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_interview_answers_session_question_id'), table_name='interview_answers')
    op.drop_table('interview_answers')

    op.drop_index(op.f('ix_interview_session_questions_question_status'), table_name='interview_session_questions')
    op.drop_index(op.f('ix_interview_session_questions_question_id'), table_name='interview_session_questions')
    op.drop_index(op.f('ix_interview_session_questions_session_id'), table_name='interview_session_questions')
    op.drop_table('interview_session_questions')

    op.drop_index(op.f('ix_interview_sessions_created_at'), table_name='interview_sessions')
    op.drop_index(op.f('ix_interview_sessions_interview_type'), table_name='interview_sessions')
    op.drop_index(op.f('ix_interview_sessions_status'), table_name='interview_sessions')
    op.drop_index(op.f('ix_interview_sessions_user_id'), table_name='interview_sessions')
    op.drop_table('interview_sessions')
