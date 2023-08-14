import uuid
from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.api.v1.submenus.models import Submenus
from src.database import Base


class Menus(Base):
    __tablename__ = 'menus'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)

    submenus: Mapped[list['Submenus']] = relationship('Submenus', backref='menu')
