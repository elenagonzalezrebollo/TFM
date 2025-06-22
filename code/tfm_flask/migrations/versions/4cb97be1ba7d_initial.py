from alembic import op
import sqlalchemy as sa


revision = '4cb97be1ba7d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('password', sa.String(length=128), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('history',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('filename', sa.String(length=255), nullable=True),
    sa.Column('audio_path', sa.String(length=255), nullable=True),
    sa.Column('audio_mime', sa.String(length=40), nullable=True),
    sa.Column('transcription', sa.Text(), nullable=True),
    sa.Column('summary_short', sa.Text(), nullable=True),
    sa.Column('summary_long', sa.Text(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_history_timestamp'), ['timestamp'], unique=False)


def downgrade():
    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_history_timestamp'))

    op.drop_table('history')
    op.drop_table('user')
