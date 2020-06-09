"""create collaborator table

Revision ID: 0d6eebeee5a3
Revises: a1a459b836c2
Create Date: 2020-06-05 11:39:42.965481

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '0d6eebeee5a3'
down_revision = 'a1a459b836c2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'collaborators',
        sa.Column('id', UUID(as_uuid=True), sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('manager_id', UUID(as_uuid=True), sa.ForeignKey('account_managers.id'))
    )


def downgrade():
    op.drop_table('collaborators')
