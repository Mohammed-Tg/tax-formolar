"""Add form data column and user profile table.

Revision ID: 20250101_add_form_data_and_user_profile
Revises: 
Create Date: 2025-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20250101_add_form_data_and_user_profile"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    columns = [column["name"] for column in inspector.get_columns("form")]
    if "data" not in columns:
        op.add_column("form", sa.Column("data", sa.JSON(), nullable=True))

    if "user_profile" not in inspector.get_table_names():
        op.create_table(
            "user_profile",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, unique=True),
            sa.Column("data", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )


def downgrade():
    op.drop_table("user_profile")
    op.drop_column("form", "data")
