import uuid
from uuid import UUID

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.api.v1.dishes.models import Dishes
from src.database import Base


class Submenus(Base):
    __tablename__ = 'submenus'

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, nullable=False, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    menu_id: Mapped[str] = mapped_column(Uuid, ForeignKey('menus.id', ondelete='CASCADE', onupdate='CASCADE'),
                                         nullable=False)

    dishes: Mapped[list['Dishes']] = relationship('Dishes', backref='submenu')
