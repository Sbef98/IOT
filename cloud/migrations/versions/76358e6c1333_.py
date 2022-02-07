"""empty message

Revision ID: 76358e6c1333
Revises: 
Create Date: 2022-02-06 15:18:45.550680

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76358e6c1333'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('actuator',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('bridge_id', sa.Integer(), nullable=False),
                    sa.Column('local_id', sa.Integer(), nullable=False),
                    sa.Column('datatype', sa.String(length=100), nullable=False),
                    sa.Column('last_value', sa.String(length=100), nullable=True),
                    sa.Column('next_value', sa.String(length=100), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('sensor',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('bridge_id', sa.Integer(), nullable=False),
                    sa.Column('local_id', sa.Integer(), nullable=False),
                    sa.Column('datatype', sa.String(length=100), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('sensorfeed',
                    sa.Column('feedid', sa.Integer(), nullable=False),
                    sa.Column('value', sa.String(length=100), nullable=True),
                    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('sensor_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['sensor_id'], ['sensor.id'], ),
                    sa.PrimaryKeyConstraint('feedid')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sensorfeed')
    op.drop_table('sensor')
    op.drop_table('actuator')
    # ### end Alembic commands ###
