
from fastapi import Request,Depends,HTTPException,Cookie,APIRouter
import logging
from sqlalchemy import select
from Database.database import get_db
from schemas import Valid_Visits
from Database.models import Pets,Visits
from datetime import datetime,UTC,date
from auth import decode_token

router=APIRouter(prefix="/pets/{pet_id}/visits",tags=["Visits"])

class Visit:
    pet_id:int
    reason:str
    notes:str
    visit_date:datetime

    def __init__(self,pet_id,reason,notes,visit_date):
        self.pet_id=pet_id
        self.reason=reason
        self.notes=notes
        self.visit_date=visit_date 
    
@router.get("")
def get_pets_create(page_number:int,pet_id:int,db=Depends(get_db)):
    page_size=10
    offset=(page_number-1)*page_size
    stmt=select(Visits.pet_id,Visits.reason,Visits.notes,Visits.visit_date).where(Visits.pet_id==pet_id).offset(offset).limit(page_number)
    db_visits = db.execute(stmt).all()

    resp_list = []

    for visit in db_visits:
        resp_dict = {}
        resp_dict["pet_id"] = visit[0]
        resp_dict["reason"] = visit[1]
        resp_dict["notes"] = visit[2]
        resp_dict["visit_date"] = visit[3]

        resp_list.append(resp_dict)

    return resp_list
    
@router.post("")
def post_pet_visit(request:Request,pet_id:int,reason: str,notes: str,visit_date: date,db=Depends(get_db)):
    login_token=request.cookies.get("login_token")
    if login_token is None:
        logging.info("authentication failed")
        raise HTTPException(status_code=401,detail={"success":"false","Reason":"Authentication error"})
    else:
        try:
          decode_token(login_token)
        except Exception as e:
           raise HTTPException(status_code=404,detail={"success":"false","Reason":f"{str(e)}"})
        stmt=select(Pets).where(Pets.id==pet_id)
        db_pet = db.execute(stmt).scalar_one_or_none()

        if not db_pet:
            logging.warning("Pet id not found")
            raise HTTPException(status_code=400,detail="No pet with the mentioned id")
        elif db_pet:
            visit=Visit(pet_id,reason,notes,visit_date)
            try:
               validated_visit=Valid_Visits.model_validate(visit)
            except Exception as e:
                logging.warning("Entered details in wrong format")
                raise HTTPException(status_code=422,detail=str(e))

            db_visit=Visits(pet_id=validated_visit.pet_id,reason=validated_visit.reason,notes=validated_visit.notes,visit_date=validated_visit.visit_date,created_at=datetime.now(UTC))
            db.add(db_visit)
            db.commit()
            logging.info("Created a visit for the pet")
            return "Created the visit for pet"

@router.put("")
def put_pet_visits(request:Request,pet_id:int,visit_date:date,reason:str|None=None,notes:str|None=None,db=Depends(get_db)):
    login_token=request.cookies.get("login_token")
    if login_token is None:
        logging.info("authentication failed")
        raise HTTPException(status_code=401,detail={"success":"false","Reason":"Authentication error"})
    else:
        try:
          decode_token(login_token)
        except Exception as e:
           raise HTTPException(status_code=404,detail={"success":"false","Reason":f"{str(e)}"})
        stmt=select(Visits).where(Visits.pet_id==pet_id,Visits.visit_date==visit_date)
        db_visit = db.execute(stmt).scalar_one_or_none()

        if not db_visit:
            logging.warning("No visits with given details")
            raise HTTPException(status_code=400,detail="No visit with mentioned details")
        elif db_visit:
            visit=Visit(pet_id,reason,notes,visit_date)
            try:
             validated_visit=Valid_Visits.model_validate(visit)
            except Exception as e:
                logging.warning("Enter details in valid format")
                raise HTTPException(status_code=400,detail=str(e))
            if reason:
             db_visit.reason=validated_visit.reason
            if notes:
             db_visit.notes=validated_visit.notes

            db_visit.updated_at=datetime.now(UTC)
            
            db.commit()
            db.refresh(db_visit)
            logging.info("Updated details successfully")

@router.delete("")
def delete_pet_visits(request:Request,pet_id:int,visit_date:date,db=Depends(get_db)):
    login_token=request.cookies.get("login_token")
    if login_token is None:
        raise HTTPException(status_code=401,detail={"success":"false","Reason":"Authentication error"})
    else:
        try:
          decode_token(login_token)
        except Exception as e:
           raise HTTPException(status_code=404,detail={"success":"false","Reason":f"{str(e)}"})
        stmt=select(Visits).where(Visits.pet_id==pet_id,Visits.visit_date==visit_date)
        db_visit=db.execute(stmt).scalar_one_or_none()
        if db_visit:
            db_visit.is_deleted=True
            db_visit.deleted_at=datetime.now(UTC)

            db.commit()
            db.refresh(db_visit)
            logging.info("Successfully deleted the visit")
            return "Deleted the visit"
        else:
            logging.warning("No visit with given details")
            raise HTTPException(status_code=400,detail="no visit with given details")