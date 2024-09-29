"""Changing customers model name to users

Revision ID: 3352a37374b0
Revises: 
Create Date: 2024-09-29 13:24:08.247874

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3352a37374b0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Rename the customers table to users
    op.rename_table('customers', 'users')

    # Create a new column user_id in the loans table
    op.add_column('loans', sa.Column('user_id', sa.Integer, nullable=True))

    # Copy data from customer_id to user_id
    conn = op.get_bind()
    conn.execute("UPDATE loans SET user_id = customer_id")

    # Drop the old customer_id column
    op.drop_column('loans', 'customer_id')

def downgrade():
    # If you ever need to roll back the migration
    op.rename_table('users', 'customers')
    
    # Create a new column customer_id in the loans table
    op.add_column('loans', sa.Column('customer_id', sa.Integer, nullable=True))

    # Copy data from user_id to customer_id
    conn = op.get_bind()
    conn.execute("UPDATE loans SET customer_id = user_id")

    # Drop the old user_id column
    op.drop_column('loans', 'user_id')
