"""new_migration

Revision ID: 9091e4b18665
Revises: ecfefeb21e28
Create Date: 2024-12-11 15:31:32.526384

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9091e4b18665'
down_revision = 'ecfefeb21e28'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_admin', sa.Boolean(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_admin')

    # ### end Alembic commands ###
