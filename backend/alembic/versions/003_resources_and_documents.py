"""Resources, Documents, Document Chunks, and Bookmarks migration

Revision ID: 003_resources_and_documents
Revises: 002_auth_and_daf_schema
Create Date: 2026-09-20 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_resources_and_documents'
down_revision: Union[str, None] = '002_auth_and_daf_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create resources table
    op.create_table(
        'resources',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('subject', sa.String(length=100), nullable=False),
        sa.Column('topic', sa.String(length=100), nullable=True),
        sa.Column('resource_type', sa.String(length=50), nullable=False, server_default='pdf'),
        sa.Column('source', sa.String(length=255), nullable=True),
        sa.Column('is_official', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_by', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resources_title'), 'resources', ['title'], unique=False)
    op.create_index(op.f('ix_resources_category'), 'resources', ['category'], unique=False)
    op.create_index(op.f('ix_resources_subject'), 'resources', ['subject'], unique=False)
    op.create_index(op.f('ix_resources_topic'), 'resources', ['topic'], unique=False)
    op.create_index(op.f('ix_resources_resource_type'), 'resources', ['resource_type'], unique=False)

    # 2. Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('resource_id', sa.String(length=36), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('stored_filename', sa.String(length=255), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False, server_default='application/pdf'),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('page_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('processing_status', sa.String(length=30), nullable=False, server_default='UPLOADED'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['resource_id'], ['resources.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stored_filename')
    )
    op.create_index(op.f('ix_documents_resource_id'), 'documents', ['resource_id'], unique=False)
    op.create_index(op.f('ix_documents_processing_status'), 'documents', ['processing_status'], unique=False)

    # 3. Create document_chunks table
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('chunk_metadata', sa.JSON(), nullable=True),
        sa.Column('embedding', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_chunks_document_id'), 'document_chunks', ['document_id'], unique=False)

    # 4. Create resource_bookmarks table
    op.create_table(
        'resource_bookmarks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('resource_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['resource_id'], ['resources.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('resource_id', 'user_id', name='uq_resource_user_bookmark')
    )
    op.create_index(op.f('ix_resource_bookmarks_resource_id'), 'resource_bookmarks', ['resource_id'], unique=False)
    op.create_index(op.f('ix_resource_bookmarks_user_id'), 'resource_bookmarks', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_table('resource_bookmarks')
    op.drop_table('document_chunks')
    op.drop_table('documents')
    op.drop_table('resources')
