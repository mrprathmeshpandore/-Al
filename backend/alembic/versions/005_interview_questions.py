"""Interview questions and sources migration

Revision ID: 005_interview_questions
Revises: 004_rag_pgvector_and_chunks
Create Date: 2026-09-21 15:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '005_interview_questions'
down_revision: Union[str, None] = '004_rag_pgvector_and_chunks'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create interview_questions table
    op.create_table(
        'interview_questions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(length=50), server_default='MAIN', nullable=False),
        sa.Column('difficulty', sa.String(length=30), server_default='MODERATE', nullable=False),
        sa.Column('subject', sa.String(length=100), nullable=True),
        sa.Column('topic', sa.String(length=255), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('why_this_matters', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=30), server_default='ACTIVE', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interview_questions_user_id'), 'interview_questions', ['user_id'], unique=False)
    op.create_index(op.f('ix_interview_questions_question_type'), 'interview_questions', ['question_type'], unique=False)
    op.create_index(op.f('ix_interview_questions_difficulty'), 'interview_questions', ['difficulty'], unique=False)
    op.create_index(op.f('ix_interview_questions_subject'), 'interview_questions', ['subject'], unique=False)
    op.create_index(op.f('ix_interview_questions_topic'), 'interview_questions', ['topic'], unique=False)
    op.create_index(op.f('ix_interview_questions_category'), 'interview_questions', ['category'], unique=False)
    op.create_index(op.f('ix_interview_questions_status'), 'interview_questions', ['status'], unique=False)
    op.create_index(op.f('ix_interview_questions_created_at'), 'interview_questions', ['created_at'], unique=False)

    # 2. Create interview_question_sources table
    op.create_table(
        'interview_question_sources',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('question_id', sa.String(length=36), nullable=False),
        sa.Column('resource_id', sa.String(length=36), nullable=True),
        sa.Column('document_id', sa.String(length=36), nullable=True),
        sa.Column('chunk_id', sa.String(length=36), nullable=True),
        sa.Column('resource_title', sa.String(length=255), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('chunk_index', sa.Integer(), nullable=True),
        sa.Column('similarity_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['interview_questions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interview_question_sources_question_id'), 'interview_question_sources', ['question_id'], unique=False)
    op.create_index(op.f('ix_interview_question_sources_resource_id'), 'interview_question_sources', ['resource_id'], unique=False)
    op.create_index(op.f('ix_interview_question_sources_document_id'), 'interview_question_sources', ['document_id'], unique=False)
    op.create_index(op.f('ix_interview_question_sources_chunk_id'), 'interview_question_sources', ['chunk_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_interview_question_sources_chunk_id'), table_name='interview_question_sources')
    op.drop_index(op.f('ix_interview_question_sources_document_id'), table_name='interview_question_sources')
    op.drop_index(op.f('ix_interview_question_sources_resource_id'), table_name='interview_question_sources')
    op.drop_index(op.f('ix_interview_question_sources_question_id'), table_name='interview_question_sources')
    op.drop_table('interview_question_sources')

    op.drop_index(op.f('ix_interview_questions_created_at'), table_name='interview_questions')
    op.drop_index(op.f('ix_interview_questions_status'), table_name='interview_questions')
    op.drop_index(op.f('ix_interview_questions_category'), table_name='interview_questions')
    op.drop_index(op.f('ix_interview_questions_topic'), table_name='interview_questions')
    op.drop_index(op.f('ix_interview_questions_subject'), table_name='interview_questions')
    op.drop_index(op.f('ix_interview_questions_difficulty'), table_name='interview_questions')
    op.drop_index(op.f('ix_interview_questions_question_type'), table_name='interview_questions')
    op.drop_index(op.f('ix_interview_questions_user_id'), table_name='interview_questions')
    op.drop_table('interview_questions')
