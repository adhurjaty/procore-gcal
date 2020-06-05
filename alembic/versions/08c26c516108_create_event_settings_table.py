"""create event settings table

Revision ID: 08c26c516108
Revises: 4a3403aa906c
Create Date: 2020-06-04 15:53:30.344286

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '08c26c516108'
down_revision = 'e0225818db4a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'event_settings',
        sa.Column('id', UUID(as_uuid=True), sa.ForeignKey('procore_settings.id'), 
            primary_key=True)
    )


def downgrade():
    op.drop_table('event_settings')
