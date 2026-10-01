"""Add performance indexes for resources, documents, answers, and evaluations

Revision ID: 013_performance_indexes
Revises: 012_ai_preparation_coach
Create Date: 2026-09-28 17:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '013_performance_indexes'
down_revision: Union[str, None] = '012_ai_preparation_coach'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add indexes for resource ownership and filtering
    op.create_index(op.f('ix_resources_created_by'), 'resources', ['created_by'], unique=False)
    op.create_index(op.f('ix_resources_created_at'), 'resources', ['created_at'], unique=False)

    # Add indexes for document ownership and filtering
    op.create_index(op.f('ix_documents_created_by'), 'documents', ['created_by'], unique=False)
    op.create_index(op.f('ix_documents_created_at'), 'documents', ['created_at'], unique=False)

    # Add index for document chunk ordering/index
    op.create_index(op.f('ix_document_chunks_chunk_index'), 'document_chunks', ['chunk_index'], unique=False)

    # Add indexes for answers and evaluations time-series queries
    op.create_index(op.f('ix_interview_answers_created_at'), 'interview_answers', ['created_at'], unique=False)
    op.create_index(op.f('ix_interview_answer_evaluations_created_at'), 'interview_answer_evaluations', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_interview_answer_evaluations_created_at'), table_name='interview_answer_evaluations')
    op.drop_index(op.f('ix_interview_answers_created_at'), table_name='interview_answers')
    op.drop_index(op.f('ix_document_chunks_chunk_index'), table_name='document_chunks')
    op.drop_index(op.f('ix_documents_created_at'), table_name='documents')
    op.drop_index(op.f('ix_documents_created_by'), table_name='documents')
    op.drop_index(op.f('ix_resources_created_at'), table_name='resources')
    op.drop_index(op.f('ix_resources_created_by'), table_name='resources')
