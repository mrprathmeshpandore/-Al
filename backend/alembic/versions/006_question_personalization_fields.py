"""Add personalization fields to interview_questions

Revision ID: 006_question_personalization_fields
Revises: 005_interview_questions
Create Date: 2026-09-21 17:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '006_question_personalization_fields'
down_revision: Union[str, None] = '005_interview_questions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('interview_questions', sa.Column('is_personalized', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('interview_questions', sa.Column('personalization_source', sa.String(length=50), nullable=True))
    op.add_column('interview_questions', sa.Column('personalization_label', sa.String(length=255), nullable=True))

    op.create_index(op.f('ix_interview_questions_is_personalized'), 'interview_questions', ['is_personalized'], unique=False)
    op.create_index(op.f('ix_interview_questions_personalization_source'), 'interview_questions', ['personalization_source'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_interview_questions_personalization_source'), table_name='interview_questions')
    op.drop_index(op.f('ix_interview_questions_is_personalized'), table_name='interview_questions')

    op.drop_column('interview_questions', 'personalization_label')
    op.drop_column('interview_questions', 'personalization_source')
    op.drop_column('interview_questions', 'is_personalized')
