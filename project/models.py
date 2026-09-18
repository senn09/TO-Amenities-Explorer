from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from typing import List

from project import db

class User(db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)

class Amenity(db.Model):
    __tablename__ = 'amenity'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(), nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("amenity_type.id"))
    address: Mapped[str] = mapped_column(String())

    amenity_type: Mapped["AmenityType"] = relationship(back_populates="amenities")

class AmenityType(db.Model):
    __tablename__ = 'amenity_type'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] =  mapped_column(String(), nullable=False)

    amenities: Mapped[List["Amenity"]] = relationship(back_populates="amenity_type")