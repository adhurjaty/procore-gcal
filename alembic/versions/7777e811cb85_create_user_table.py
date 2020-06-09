"""create user table

Revision ID: 7777e811cb85
Revises: 7530b47c5d3c
Create Date: 2020-06-05 11:39:17.715791

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '7777e811cb85'
down_revision = '7530b47c5d3c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(50), nullable=False),
        sa.Column('full_name', sa.String(100)),
        sa.Column('temporary', sa.Boolean(), nullable=False),
        sa.Column('type', sa.String(50)),
        sa.Column('gcal_settings_id', UUID(as_uuid=True), sa.ForeignKey('gcal_user_settings.id'))
    )


def downgrade():
    op.drop_table('users')
