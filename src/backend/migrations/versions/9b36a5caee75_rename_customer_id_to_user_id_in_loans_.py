from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'xxxx'  # Replace with the new revision ID
down_revision = '3352a37374b0'  # The last migration ID that was applied
branch_labels = None
depends_on = None

def upgrade():
    # Rename the customer_id column to user_id in the loans table
    with op.batch_alter_table('loans') as batch_op:
        batch_op.alter_column('customer_id', new_column_name='user_id')

def downgrade():
    # Revert the change by renaming user_id back to customer_id
    with op.batch_alter_table('loans') as batch_op:
        batch_op.alter_column('user_id', new_column_name='customer_id')
