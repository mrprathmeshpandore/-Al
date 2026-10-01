"""Add input_mode and language to interview_sessions table

Revision ID: 011_voice_mode
Revises: 010_adaptive_questions
Create Date: 2026-09-28 11:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '011_voice_mode'
down_revision: Union[str, None] = '010_adaptive_questions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'interview_sessions',
        sa.Column('input_mode', sa.String(length=20), nullable=False, server_default='TEXT')
    )
    op.add_column(
        'interview_sessions',
        sa.Column('language', sa.String(length=20), nullable=False, server_default='en-IN')
    )


def downgrade() -> None:
    op.drop_column('interview_sessions', 'language')
    op.drop_column('interview_sessions', 'input_mode')
