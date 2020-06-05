"""create procore settings table

Revision ID: e8020926ebff
Revises: 
Create Date: 2020-06-04 15:40:25.031003

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'e8020926ebff'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'procore_settings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('type', sa.String(50))
    )


def downgrade():
    op.drop_table('procore_settings')
