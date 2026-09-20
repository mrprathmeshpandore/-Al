"""RAG pgvector and document chunk fields migration

Revision ID: 004_rag_pgvector_and_chunks
Revises: 003_resources_and_documents
Create Date: 2026-09-20 16:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '004_rag_pgvector_and_chunks'
down_revision: Union[str, None] = '003_resources_and_documents'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add content_hash and embedding_status columns to document_chunks
    op.add_column('document_chunks', sa.Column('content_hash', sa.String(length=64), nullable=True))
    op.add_column('document_chunks', sa.Column('embedding_status', sa.String(length=30), nullable=False, server_default='PENDING'))

    op.create_index(op.f('ix_document_chunks_content_hash'), 'document_chunks', ['content_hash'], unique=False)
    op.create_index(op.f('ix_document_chunks_embedding_status'), 'document_chunks', ['embedding_status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_document_chunks_embedding_status'), table_name='document_chunks')
    op.drop_index(op.f('ix_document_chunks_content_hash'), table_name='document_chunks')
    op.drop_column('document_chunks', 'embedding_status')
    op.drop_column('document_chunks', 'content_hash')
