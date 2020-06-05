"""create oauth2 token table

Revision ID: be4f89bade9f
Revises: e0225818db4a
Create Date: 2020-06-04 15:54:01.838563

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'be4f89bade9f'
down_revision = 'e8020926ebff'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'oauth2_tokens',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('access_token', sa.String(100), nullable=False),
        sa.Column('refresh_token', sa.String(100), nullable=False),
        sa.Column('token_type', sa.String(50), nullable=False),
        sa.Column('expires_at', sa.Integer(), nullable=False),
    )


def downgrade():
    op.drop_table('oauth2_tokens')
