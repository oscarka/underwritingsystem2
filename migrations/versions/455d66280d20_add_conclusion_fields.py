"""add conclusion fields

Revision ID: 455d66280d20
Revises: eb157058c420
Create Date: 2025-02-08 15:34:48.010400

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '455d66280d20'
down_revision = 'eb157058c420'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('conclusions', sa.Column('name', sa.String(length=100), nullable=True))
    op.add_column('conclusions', sa.Column('content', sa.Text(), nullable=True))
    op.add_column('conclusions', sa.Column('decision', sa.String(length=50), nullable=True))
    op.add_column('conclusions', sa.Column('em_value', sa.Float(), nullable=True))
    op.add_column('conclusions', sa.Column('type_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_conclusion_type', 'conclusions', 'conclusion_types', ['type_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_conclusion_type', 'conclusions', type_='foreignkey')
    op.drop_column('conclusions', 'type_id')
    op.drop_column('conclusions', 'em_value')
    op.drop_column('conclusions', 'decision')
    op.drop_column('conclusions', 'content')
    op.drop_column('conclusions', 'name')
    # ### end Alembic commands ###
