"""empty message

Revision ID: 15945cfc860e
Revises: a616a59ea020
Create Date: 2023-01-22 14:35:58.769938

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15945cfc860e'
down_revision = 'a616a59ea020'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('likes',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'post_id')
    )
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('like_count', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('like_count')

    op.drop_table('likes')
    # ### end Alembic commands ###
