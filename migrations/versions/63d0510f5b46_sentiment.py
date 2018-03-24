"""'Sentiment'

Revision ID: 63d0510f5b46
Revises: 73aa63e79620
Create Date: 2018-03-15 18:26:12.611773

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63d0510f5b46'
down_revision = '73aa63e79620'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sentences', sa.Column('sentiment', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sentences', 'sentiment')
    # ### end Alembic commands ###