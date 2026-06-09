from Database.database import Base

from sqlalchemy import Integer,String,Text,ForeignKey,TIMESTAMP,DateTime
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime

class Pets(Base):

    __tablename__="Pets"

    id:Mapped[int]=mapped_column(Integer,primary_key=True,index=True)
    name:Mapped[str]=mapped_column(String,nullable=False)
    species:Mapped[str]=mapped_column(String,nullable=False)
    breed:Mapped[str]=mapped_column(String,nullable=False)
    age:Mapped[int]=mapped_column(Integer,nullable=False)
    owner_name:Mapped[str]=mapped_column(String,nullable=False)
    owner_phone:Mapped[str]=mapped_column(String,nullable=False)
    created_at:Mapped[datetime]=mapped_column(TIMESTAMP,nullable=False)

class Visits(Base):

    __tablename__="Vists"

    id:Mapped[int]=mapped_column(Integer,primary_key=True,index=True)
    pet_id:Mapped[int]=mapped_column(Integer,ForeignKey(Pets.id),nullable=False)
    reason:Mapped[str]=mapped_column(String,nullable=False)
    notes:Mapped[str]=mapped_column(String,nullable=False)
    visit_date:Mapped[datetime]=mapped_column(DateTime,nullable=False)
    created_at:Mapped[datetime]=mapped_column(TIMESTAMP,nullable=False)
    