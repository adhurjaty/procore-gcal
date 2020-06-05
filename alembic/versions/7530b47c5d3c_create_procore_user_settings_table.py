"""create procore user settings table

Revision ID: 7530b47c5d3c
Revises: 08c26c516108
Create Date: 2020-06-04 15:53:40.330539

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '7530b47c5d3c'
down_revision = '4a3403aa906c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'procore_user_settings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('token_id', UUID(as_uuid=True), sa.ForeignKey('oauth2_tokens.id'))
    )
    op.create_table(
        'email_association',
        sa.Column('email_id', UUID(as_uuid=True), sa.ForeignKey('email_settings.id')),
        sa.Column('procore_id', UUID(as_uuid=True), sa.ForeignKey('procore_user_settings.id'))
    )
    op.create_table(
        'event_association',
        sa.Column('event_id', UUID(as_uuid=True), sa.ForeignKey('event_settings.id')),
        sa.Column('procore_id', UUID(as_uuid=True), sa.ForeignKey('procore_user_settings.id'))
    )

def downgrade():
    op.drop_table('procore_user_settings')
    op.drop_table('email_association')
    op.drop_table('event_association')
