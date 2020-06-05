"""create gcal user settings table

Revision ID: e0225818db4a
Revises: 7530b47c5d3c
Create Date: 2020-06-04 15:53:47.336002

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'e0225818db4a'
down_revision = 'be4f89bade9f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'gcal_user_settings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('calendar_id', sa.String(50), nullable=False),
        sa.Column('token_id', UUID(as_uuid=True), sa.ForeignKey('oauth2_tokens.id')),
    )


def downgrade():
    op.drop_table('gcal_user_settings')
