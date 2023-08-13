import uuid
from uuid import UUID

from _decimal import Decimal
from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base


class Dishes(Base):
    __tablename__ = 'dishes',

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, nullable=False, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[Decimal] = mapped_column(String, nullable=False)
    submenu_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey('submenus.id', ondelete='CASCADE', onupdate='CASCADE'),
                                             nullable=False)
