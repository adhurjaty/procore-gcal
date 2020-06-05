"""create email settings table

Revision ID: 4a3403aa906c
Revises: e8020926ebff
Create Date: 2020-06-04 15:53:25.930551

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '4a3403aa906c'
down_revision = '08c26c516108'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'email_settings',
        sa.Column('id', UUID(as_uuid=True), sa.ForeignKey('procore_settings.id'), 
            primary_key=True)
    )


def downgrade():
    op.drop_table('email_settings')
