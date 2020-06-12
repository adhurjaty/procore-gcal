"""increase token string length

Revision ID: c8455827f89c
Revises: 0d6eebeee5a3
Create Date: 2020-06-12 09:10:08.050912

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8455827f89c'
down_revision = '0d6eebeee5a3'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('oauth2_tokens', 'access_token',
        existing_type=sa.VARCHAR(100),
        type_=sa.String(500),
        existing_nullable=False)
    op.alter_column('oauth2_tokens', 'refresh_token',
        existing_type=sa.VARCHAR(100),
        type_=sa.String(500),
        existing_nullable=False)


def downgrade():
    op.alter_column('oauth2_tokens', 'access_token',
        existing_type=sa.VARCHAR(500),
        type_=sa.String(100),
        existing_nullable=False)
    op.alter_column('oauth2_tokens', 'refresh_token',
        existing_type=sa.VARCHAR(500),
        type_=sa.String(100),
        existing_nullable=False)
