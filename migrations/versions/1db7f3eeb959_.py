"""empty message

Revision ID: 1db7f3eeb959
Revises: 63d0510f5b46
Create Date: 2018-12-05 11:35:59.492786

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1db7f3eeb959'
down_revision = '63d0510f5b46'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('audio',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('audio_filename', sa.String(), nullable=True),
    sa.Column('audio_url', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audio_timestamp'), 'audio', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_audio_timestamp'), table_name='audio')
    op.drop_table('audio')
    # ### end Alembic commands ###
