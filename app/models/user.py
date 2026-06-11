import enum
from datetime import datetime

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class PlanEnum(enum.StrEnum):
    free = "free"
    pro = "pro"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    plan: Mapped[PlanEnum] = mapped_column(
        ENUM(PlanEnum, name="plan_enum", create_type=True), default=PlanEnum.free
    )
    business_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    business_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    business_tax_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True, default=None)
