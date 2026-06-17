from Database.database import Base
from enum import Enum as PyEnum
from uuid import uuid4
from sqlalchemy import Integer, String, ForeignKey, TIMESTAMP, DateTime, Date,Boolean,UUID,Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date


class Owners(Base):

    __tablename__ = "Owners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at:Mapped[datetime]=mapped_column(DateTime,nullable=True)
    is_deleted:Mapped[bool]=mapped_column(Boolean,default=False)
    deleted_at:Mapped[datetime]=mapped_column(DateTime,nullable=True)
    pets = relationship("Pets", back_populates="owners",cascade="all, delete-orphan")


class Pets(Base):

    __tablename__ = "Pets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    species: Mapped[str] = mapped_column(String, nullable=False)
    breed: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)

    owner_id: Mapped[int] = mapped_column(Integer,ForeignKey("Owners.id"),nullable=False)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    updated_at:Mapped[datetime]=mapped_column(DateTime,nullable=True)
    is_deleted:Mapped[bool]=mapped_column(Boolean,default=False)
    deleted_at:Mapped[datetime]=mapped_column(DateTime,nullable=True)

    owners = relationship("Owners",back_populates="pets")

    visits = relationship("Visits",back_populates="pet",cascade="all, delete-orphan")


class Visits(Base):

    __tablename__ = "Visits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    pet_id: Mapped[int] = mapped_column(Integer,ForeignKey("Pets.id"),nullable=False)

    reason: Mapped[str] = mapped_column(String, nullable=False)
    notes: Mapped[str] = mapped_column(String, nullable=False)
    visit_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[date] = mapped_column(Date, nullable=False)
    updated_at:Mapped[datetime]=mapped_column(DateTime,nullable=True)
    is_deleted:Mapped[bool]=mapped_column(Boolean,default=False)
    deleted_at:Mapped[datetime]=mapped_column(DateTime,nullable=True)

    pet = relationship("Pets",back_populates="visits")

class UserRole(PyEnum):
    ADMIN="ADMIN"
    VET="VET"
    RECEPTIONIST="RECEPTIONIST"

class Users(Base):
    __tablename__="Users"
    id:Mapped[UUID]=mapped_column(UUID,primary_key=True,default=uuid4)
    name:Mapped[str]=mapped_column(String,nullable=False)
    email:Mapped[str]=mapped_column(String,unique=True,nullable=False,index=True)
    password_hash:Mapped[str]=mapped_column(String,nullable=False)
    role:Mapped[UserRole]=mapped_column(Enum(UserRole),nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime,nullable=False)
    updated_at:Mapped[datetime]=mapped_column(DateTime,nullable=True)

    
