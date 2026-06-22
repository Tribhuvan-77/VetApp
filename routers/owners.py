from fastapi import Depends,HTTPException,APIRouter
import logging
from sqlalchemy import select
from Database.database import get_db
from schemas import Valid_Owners
from Database.models import Owners
from datetime import datetime,UTC

router=APIRouter(prefix="/owner",tags=["Owners"])
class Owner:
    name:str
    phone:str
    email:str

    def __init__(self,name,phone,email):
        self.name=name
        self.phone=phone
        self.email=email


@router.get("")
def get_owner(page_number:int,db=Depends(get_db)):
    page_size=10
    offset=(page_number-1)*page_size
    stmt=select(Owners.id,Owners.name,Owners.is_deleted).offset(offset).limit(page_size)
    db_owner=db.execute(stmt).all()
    resp_dict={}
    for i in db_owner:
        if i[2]==False:
         resp_dict[i[0]]=i[1]
    return resp_dict

@router.post("/create")
def post_owner_create(name:str,phone:str,email:str,db=Depends(get_db)):
    owner=Owner(name,phone,email)
    try:
      valid_owner=Valid_Owners.model_validate(owner)
    except Exception as e:
        logging.warning("owner id not found")
        raise HTTPException(status_code=400,detail=str(e))
    stmt=select(Owners).where(Owners.name==valid_owner.name,Owners.phone==valid_owner.phone,Owners.email==valid_owner.email)
    db_owner=db.execute(stmt).scalar_one_or_none()
    print(db_owner)

    if db_owner:
        raise HTTPException(status_code=400,detail="Owner already exists")
    elif not db_owner:
        db_owner=Owners(name=valid_owner.name,phone=valid_owner.phone,email=valid_owner.email,created_at=datetime.now(UTC))
        db.add(db_owner)
        db.commit()
        logging.info("Created owner entry")
        return "Created owner entry"
    
@router.put("/update")
def update_owner(id:int,name:str|None=None,phone:str|None=None,email:str|None=None,db=Depends(get_db)):
    stmt=select(Owners).where(Owners.id==id)
    db_owner=db.execute(stmt).scalar_one_or_none()
    if db_owner:
        if name:
            db_owner.name=name
        if phone:
            db_owner.phone=phone
        if email:
            db_owner.email=email

        db_owner.updated_at=datetime.now(UTC)

        db.commit()
        db.refresh(db_owner)
        logging.info("Updated owner details")
        return "Updated owner details" 
    else:
        logging.warning("Owner id not found")
        raise HTTPException(status_code=400,detail="owner does not exist")


@router.delete("/delete")
def delete_owner(id:int,db=Depends(get_db)):
    stmt=select(Owners).where(Owners.id==id)
    db_owner=db.execute(stmt).scalar_one_or_none()

    if not db_owner:
        logging.warning("owner id not found")
        raise HTTPException(status_code=400,detail="Owner does not exist")
    else:
        db_owner.is_deleted=True
        db_owner.deleted_at=datetime.now(UTC)

        db.commit()
        db.refresh(db_owner)
        logging.info("Deleted owner entry")

        return "Deleted the owner"

