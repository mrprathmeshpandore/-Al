"""Create current_affairs table and link interview_questions

Revision ID: 007_current_affairs_table
Revises: 006_question_personalization_fields
Create Date: 2026-09-21 19:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '007_current_affairs_table'
down_revision: Union[str, None] = '006_question_personalization_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create current_affairs table
    op.create_table(
        'current_affairs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('source_name', sa.String(length=100), nullable=False),
        sa.Column('source_url', sa.String(length=1024), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('retrieved_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False, server_default='NATIONAL'),
        sa.Column('topic', sa.String(length=100), nullable=True),
        sa.Column('subtopic', sa.String(length=100), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('key_points', sa.JSON(), nullable=True),
        sa.Column('context', sa.Text(), nullable=True),
        sa.Column('policy_response', sa.Text(), nullable=True),
        sa.Column('upsc_relevance', sa.Text(), nullable=True),
        sa.Column('interview_angle', sa.Text(), nullable=True),
        sa.Column('analysis_status', sa.String(length=30), nullable=False, server_default='FETCHED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_current_affairs_title'), 'current_affairs', ['title'], unique=False)
    op.create_index(op.f('ix_current_affairs_slug'), 'current_affairs', ['slug'], unique=True)
    op.create_index(op.f('ix_current_affairs_source_name'), 'current_affairs', ['source_name'], unique=False)
    op.create_index(op.f('ix_current_affairs_source_url'), 'current_affairs', ['source_url'], unique=False)
    op.create_index(op.f('ix_current_affairs_published_at'), 'current_affairs', ['published_at'], unique=False)
    op.create_index(op.f('ix_current_affairs_category'), 'current_affairs', ['category'], unique=False)
    op.create_index(op.f('ix_current_affairs_topic'), 'current_affairs', ['topic'], unique=False)
    op.create_index(op.f('ix_current_affairs_analysis_status'), 'current_affairs', ['analysis_status'], unique=False)
    op.create_index(op.f('ix_current_affairs_created_at'), 'current_affairs', ['created_at'], unique=False)

    # Update interview_questions table
    op.add_column('interview_questions', sa.Column('current_affair_id', sa.String(length=36), nullable=True))
    op.alter_column('interview_questions', 'user_id', existing_type=sa.String(length=36), nullable=True)
    op.create_index(op.f('ix_interview_questions_current_affair_id'), 'interview_questions', ['current_affair_id'], unique=False)
    op.create_foreign_key(
        'fk_interview_questions_current_affair_id',
        'interview_questions',
        'current_affairs',
        ['current_affair_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_interview_questions_current_affair_id', 'interview_questions', type_='foreignkey')
    op.drop_index(op.f('ix_interview_questions_current_affair_id'), table_name='interview_questions')
    op.alter_column('interview_questions', 'user_id', existing_type=sa.String(length=36), nullable=False)
    op.drop_column('interview_questions', 'current_affair_id')

    op.drop_index(op.f('ix_current_affairs_created_at'), table_name='current_affairs')
    op.drop_index(op.f('ix_current_affairs_analysis_status'), table_name='current_affairs')
    op.drop_index(op.f('ix_current_affairs_topic'), table_name='current_affairs')
    op.drop_index(op.f('ix_current_affairs_category'), table_name='current_affairs')
    op.drop_index(op.f('ix_current_affairs_published_at'), table_name='current_affairs')
    op.drop_index(op.f('ix_current_affairs_source_url'), table_name='current_affairs')
    op.drop_index(op.f('ix_current_affairs_source_name'), table_name='current_affairs')
    op.drop_index(op.f('ix_current_affairs_slug'), table_name='current_affairs')
    op.drop_index(op.f('ix_current_affairs_title'), table_name='current_affairs')
    op.drop_table('current_affairs')
