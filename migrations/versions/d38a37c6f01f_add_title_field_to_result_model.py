"""Add title field to Result model

Revision ID: d38a37c6f01f
Revises: bfed5c7a9f1a
Create Date: 2026-05-09 16:19:39.861246

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd38a37c6f01f'
down_revision = 'bfed5c7a9f1a'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Tambahkan kolom sebagai nullable dulu
    op.add_column('results', sa.Column('title', sa.String(length=255), nullable=True))
    
    # 2. Isi kolom kosong dengan nilai default (misal: "Untitled Portfolio")
    op.execute("UPDATE results SET title = 'Untitled Portfolio' WHERE title IS NULL")
    
    # 3. Ubah kolom menjadi NOT NULL
    op.alter_column('results', 'title', nullable=False)


def downgrade():
    op.drop_column('results', 'title')
