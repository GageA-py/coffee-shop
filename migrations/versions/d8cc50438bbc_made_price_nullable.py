"""made price nullable

Revision ID: d8cc50438bbc
Revises: 034351c1aad3
Create Date: 2024-08-14 15:23:50.502217

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8cc50438bbc'
down_revision = '034351c1aad3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.alter_column('price',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.alter_column('price',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)

    # ### end Alembic commands ###