"""add storage limit cap to users

Revision ID: 333a024ee11e
Revises: 
Create Date: 2026-07-12 21:22:48.220706

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
# 1. IMPORT THE POSTGRES DIALECT SPECIFIC ENUM
from sqlalchemy.dialects import postgresql 

# revision identifiers, used by Alembic.
revision: str = '333a024ee11e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 2. Safely check and create the type standalone if it's missing
    sa.Enum('csv', 'json', 'xlsx', name='file_type_enum').create(op.get_bind(), checkfirst=True)

    # 3. Build the users table
    op.create_table('users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('username', sa.String(length=20), nullable=False),
        sa.Column('email', sa.Text(), nullable=False),
        sa.Column('password', sa.Text(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('storage_used_bytes', sa.Integer(), server_default='0', nullable=False),
        sa.Column('storage_limit_bytes', sa.Integer(), server_default='52428800', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # 4. Build the datasets table 
    op.create_table('datasets',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.Column('original_name', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=512), nullable=False),
        
        # CHANGED HERE: Using postgresql.ENUM with create_type=False prevents the crash!
        sa.Column('file_type', postgresql.ENUM('csv', 'json', 'xlsx', name='file_type_enum', create_type=False), nullable=False),
        
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('last_accessed_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('datasets')
    op.drop_table('users')
    sa.Enum('csv', 'json', 'xlsx', name='file_type_enum').drop(op.get_bind(), checkfirst=True)