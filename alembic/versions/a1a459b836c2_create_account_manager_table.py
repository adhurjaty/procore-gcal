"""create account manager table

Revision ID: a1a459b836c2
Revises: 7777e811cb85
Create Date: 2020-06-05 11:39:26.648490

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'a1a459b836c2'
down_revision = '7777e811cb85'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'account_managers',
        sa.Column('id', UUID(as_uuid=True), sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('subscribed', sa.Boolean(), nullable=False),
        sa.Column('trial_start', sa.DateTime()),
        sa.Column('payment_id', sa.String(100)),
        sa.Column('project_id', sa.Integer()),
        sa.Column('procore_settings_id', UUID(as_uuid=True), sa.ForeignKey('procore_user_settings.id'))
    )


def downgrade():
    op.drop_table('account_managers')
