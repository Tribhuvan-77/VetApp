from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,DeclarativeBase

SQLALCHMY_DATABASE_URL="sqlite:///./Database/pets.db"

engine=create_engine(SQLALCHMY_DATABASE_URL,connect_args={"check_same_thread":False})

Sessionlocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    with Sessionlocal() as db:
        yield db




