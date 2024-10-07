"""Add QR-CODE

Revision ID: 5266f18a4c87
Revises: 7b137a51367e
Create Date: 2024-09-29 22:04:37.615459

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5266f18a4c87'
down_revision = '7b137a51367e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('qr_code',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('link', sa.String(length=255), nullable=False),
    sa.Column('background_color', sa.String(length=10), nullable=False),
    sa.Column('fill_color', sa.String(length=10), nullable=False),
    sa.Column('size', sa.Integer(), nullable=False),
    sa.Column('file', sa.String(length=255), nullable=True),
    sa.Column('qr_base64', sa.Text(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('qr_code')
    # ### end Alembic commands ###