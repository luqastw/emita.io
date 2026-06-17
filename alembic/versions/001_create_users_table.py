"""create users table

Revision ID: 001
Revises:
Create Date: 2026-06-11

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ENUM

# revision identifiers
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create plan_enum type
    plan_enum = ENUM("free", "pro", name="plan_enum", create_type=False)
    plan_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, index=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "plan",
            ENUM("free", "pro", name="plan_enum", create_type=False),
            server_default="free",
            nullable=False,
        ),
        sa.Column("business_name", sa.String(255), nullable=True),
        sa.Column("business_address", sa.String(500), nullable=True),
        sa.Column("business_tax_id", sa.String(50), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("users")
    plan_enum = ENUM(name="plan_enum")
    plan_enum.drop(op.get_bind(), checkfirst=True)
