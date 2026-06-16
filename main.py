from fastapi import FastAPI,Request,Depends,Form,HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from Database.database import Base,engine,get_db
from Database.models import Pets,Visits,Owners
from schemas import Valid_Pets,Valid_Visits,Valid_Owners

import logging

from fastapi.templating import Jinja2Templates
from datetime import datetime,UTC,date

#this creates table for all the models that inherit base
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.DEBUG,format="%(asctime)s - %(levelname)s - %(message)s")
app=FastAPI()
templates=Jinja2Templates(directory="templates")

class Pet:
    name:str
    species:str
    breed:str
    age:int
    owner_id:int

    def __init__(self,name,species,breed,age,owner_id):
        self.name=name
        self.species=species
        self.breed=breed
        self.age=age
        self.owner_id=owner_id
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

class Owner:
    name:str
    phone:str
    email:str

    def __init__(self,name,phone,email):
        self.name=name
        self.phone=phone
        self.email=email
         

@app.get("/")
def get_home(request:Request):
    return {"Welcome Home"}

#for paginaton->we have page number->tells which page to be shown and page size-> no of records in each page
#offset->(page-1)*page_size --> here we are doing page-1 as offset starts frm 0

@app.get("/owner",tags=["Owners"])
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


@app.post("/owner/create",tags=["Owners"])
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
    
@app.put("/owner/update",tags=["Owners"])
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


@app.delete("/owner/delete",tags=["Owners"])
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
    

@app.get("/pets",tags=["Pets"])
def get_pets(page_number:int,db=Depends(get_db)):
    page_size=10
    offset=(page_number-1)*page_size
    stmt=select(Pets.id,Pets.name).offset(offset).limit(page_number)
    db_pets=db.execute(stmt).all()

    resp_dict={}
    for i in db_pets:
        resp_dict[i[0]]=i[1]
    return resp_dict

@app.get("/pets/filter",tags=["Pets"])
def get_pets(species: str | None = None,breed: str | None = None,owner_name: str | None = None,min_age: int | None = None,max_age: int | None = None,search: str | None = None,db=Depends(get_db)):
    filter=[]
    if species:
        filter.append(Pets.species==species)
    if breed:
        filter.append(Pets.breed==breed)
    if owner_name:
        filter.append(Pets.owners.name==owner_name)
    if min_age:
        filter.append(Pets.age>=min_age)
    if max_age:
        filter.append(Pets.age<=max_age)
    if search:
        filter.append(Pets.name.lower().contains(search))
    
    stmt=select(Pets).where(*filter)
    db_pets=db.execute(stmt).all()
    print(db_pets)

@app.post("/pets/create",tags=["Pets"])
def post_createpets(request:Request,name:str,species:str,breed:str,age:int,owner_name:str,owner_phone:str,db=Depends(get_db)):
    stmt=select(Owners.id).where(Owners.name==owner_name,Owners.phone==owner_phone)
    db_owner=db.execute(stmt).scalars().all()
    if not db_owner:
        logging.warning("No entry of the owner")
        raise HTTPException(status_code=400,detail="owner not exisiting")
    else:     
        pet=Pet(name,species,breed,age,db_owner[0])
        try:
            logging.warning("Entered details in wrong format")
            validated_entry=Valid_Pets.model_validate(pet)
        except Exception as e:
            raise HTTPException(status_code=400,detail=str(e))
        
        db_pet=Pets(name=validated_entry.name,species=validated_entry.species,breed=validated_entry.breed,age=validated_entry.age,owner_id=validated_entry.owner_id,created_at=datetime.now(UTC))
        db.add(db_pet)
        db.commit()
        logging.info("created a pet entry")
        return "Created the entry"

@app.delete("/pets/delete",tags=["Pets"])
def delete_pets_delete(db=Depends(get_db),id:int=Form(...)):
    stmt=select(Pets).where(Pets.id==id)
    pet=db.scalar(stmt)

    if pet:
        pet.is_deleted=True
        pet.deleted_at=datetime.now(UTC)

        db.commit()
        db.refresh(pet)
        logging.info("Deleted pet entry")
        return "Deleted the pet entry"

    else:
        logging.warning("pet id not found")
        raise HTTPException(status_code=400,detail="id not found")
    


@app.put("/pets/update",tags=["Pets"])
def put_pets(id:int,name:str|None=None,species:str|None=None,breed:str|None=None,age:int|None=None,owner_id:int|None=None,db=Depends(get_db)):
    stmt=select(Pets).where(Pets.id==id)
    db_pet = db.execute(stmt).scalar_one_or_none()
    if not db_pet:
        logging.warning("pet id not found")
        raise HTTPException(status_code=400,detail="Invalid id")
    else:
        pet = db.scalar(select(Pets).where(Pets.id == id))
        if pet:
            if name:
               pet.name = name
            if species:
               pet.species = species
            if breed:
             pet.breed = breed
            if age:
             pet.age = age

            if owner_id:
             stmt=select(Owners.id).where(Owners.name==owner_id)
             db_owner=db.execute(stmt).scalars().all()
             if not db_owner:
                logging.warning("Owner id not found")
                raise HTTPException(status_code=400,detail="owner id not found")
             else:
              pet.owner_id=db_owner[0]
              pet.updated_at=datetime.now(UTC)
        else:
            logging.warning("pet id not found")
            raise HTTPException(status_code=400,detail="pet id not found")

        db.commit()
        db.refresh(pet)
        logging.info("Updated pet info")

        return "Updated the pet entry"


@app.get("/pets/{pet_id}",tags=["Pets"])
def get_petsid(request:Request,pet_id:int,db=Depends(get_db)):
    stmt=select(Pets).where(Pets.id==pet_id)
    db_pet = db.execute(stmt).scalar_one_or_none()

    if db_pet:
        resp_dict={}
        resp_dict["id"]=db_pet.id
        resp_dict["name"]=db_pet.name
        resp_dict["species"]=db_pet.species
        resp_dict["breed"]=db_pet.breed
        resp_dict["age"]=db_pet.age
        resp_dict["owner_id"]=db_pet.owner_id
        return resp_dict
    else:
        logging.warning("Pet id not found")
        raise HTTPException(status_code=400,detail="invalid id")
    
@app.get("/pets/{pet_id}/visits",tags=["Visits"])
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
    
@app.post("/pets/{pet_id}/visits",tags=["Visits"])
def post_pet_visit(request:Request,pet_id:int,reason: str,notes: str,visit_date: date,db=Depends(get_db)):
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
            raise HTTPException(status_code=400,detail=str(e))

        db_visit=Visits(pet_id=validated_visit.pet_id,reason=validated_visit.reason,notes=validated_visit.notes,visit_date=validated_visit.visit_date,created_at=datetime.now(UTC))
        db.add(db_visit)
        db.commit()
        logging.info("Created a visit for the pet")
        return "Created the visit for pet"

@app.put("/pets/{pet_id}/visits",tags=["Visits"])
def put_pet_visits(pet_id:int,visit_date:date,reason:str|None=None,notes:str|None=None,db=Depends(get_db)):
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

@app.delete("/pets/{pet_id}/visits",tags=["Visits"])
def delete_pet_visits(pet_id:int,visit_date:date,db=Depends(get_db)):
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
    
    






        














    

    





