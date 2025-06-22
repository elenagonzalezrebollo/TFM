from alembic import op
import sqlalchemy as sa

revision = '9ca31c16bad4'
down_revision = '4cb97be1ba7d'
branch_labels = None
depends_on = None


def upgrade():
    
    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('display_name', sa.String(length=255), nullable=True))


def downgrade():
    
    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.drop_column('display_name')

   
