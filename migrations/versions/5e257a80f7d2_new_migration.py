"""new_migration

Revision ID: 5e257a80f7d2
Revises: 9091e4b18665
Create Date: 2024-12-11 19:07:18.787753

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e257a80f7d2'
down_revision = '9091e4b18665'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('fakenodo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('ds_meta_data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dataset_fakenodo_doi', sa.String(length=120), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ds_meta_data', schema=None) as batch_op:
        batch_op.drop_column('dataset_fakenodo_doi')

    op.drop_table('fakenodo')
    # ### end Alembic commands ###