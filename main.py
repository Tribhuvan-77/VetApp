from fastapi import FastAPI,Request,Depends,Form,HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from Database.database import Base,engine,get_db
from Database.models import Pets,Visits,Owners
from schemas import Valid_Pets,Valid_Visits,Valid_Owners

from fastapi.templating import Jinja2Templates
from datetime import datetime,UTC,date

#this creates table for all the models that inherit base
Base.metadata.create_all(bind=engine)

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

@app.get("/owner",tags=["Owners"])
def get_owner(db=Depends(get_db)):
    stmt=select(Owners.id,Owners.name)
    db_owner=db.execute(stmt).all()
    resp_dict={}
    for i in db_owner:
        resp_dict[i[0]]=i[1]
    return resp_dict


@app.post("/owner/create",tags=["Owners"])
def post_owner_create(request:Request,name:str,phone:str,email:str,db=Depends(get_db)):
    owner=Owner(name,phone,email)
    try:
      valid_owner=Valid_Owners.model_validate(owner)
    except Exception as e:
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
        return "Created owner entry"
@app.delete("/owner/delete",tags=["Owners"])
def delete_owner(id:int,db=Depends(get_db)):
    stmt=select(Owners).where(Owners.id==id)
    db_owner=db.execute(stmt).scalar_one_or_none()

    if not db_owner:
        raise HTTPException(status_code=400,detail="Owner does not exist")
    else:
        db.delete(db_owner)
        db.commit()
        return "Deleted the owner"
    

@app.get("/pets",tags=["Pets"])
def get_pets(db=Depends(get_db)):
    stmt=select(Pets.id,Pets.name)
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
    
    stmt=select(Pets).where(filter)
    db_pets=db.execute(stmt).all()
    print(db_pets)

@app.post("/pets/create",tags=["Pets"])
def post_createpets(request:Request,name:str,species:str,breed:str,age:int,owner_name:str,owner_phone:str,db=Depends(get_db)):
    stmt=select(Owners.id).where(Owners.name==owner_name,Owners.phone==owner_phone)
    db_owner=db.execute(stmt).scalars().all()
    if not db_owner:
        raise HTTPException(status_code=400,detail="owner not exisiting")
    else:     
        pet=Pet(name,species,breed,age,db_owner[0])
        try:
            validated_entry=Valid_Pets.model_validate(pet)
        except Exception as e:
            raise HTTPException(status_code=400,detail=str(e))
        
        db_pet=Pets(name=validated_entry.name,species=validated_entry.species,breed=validated_entry.breed,age=validated_entry.age,owner_id=validated_entry.owner_id,created_at=datetime.now(UTC))
        db.add(db_pet)
        db.commit()

        return "Created the entry"

@app.delete("/pets/delete",tags=["Pets"])
def delete_pets_delete(request:Request,db=Depends(get_db),id:int=Form(...)):
    stmt=select(Pets).where(Pets.id==id)
    pet=db.scalar(stmt)

    if pet:
        db.delete(pet)
        db.commit()
    else:
        raise HTTPException(status_code=400,detail="id not found")
    
    return "Deleted the pet entry"

@app.post("/pets/update",tags=["Pets"])
def post_pets_update(request:Request,id:int,name:str,species:str,breed:str,age:int,owner_id:int,db=Depends(get_db)):
    stmt=select(Pets).where(Pets.id==id)
    db_pet = db.execute(stmt).scalar_one_or_none()
    if not db_pet:
        raise HTTPException(status_code=400,detail="Invalid id")
    else:
        pet = db.scalar(select(Pets).where(Pets.id == id))
        stmt=select(Owners.id).where(Owners.name==owner_id)
        db_owner=db.execute(stmt).scalars().all()
        if not db_owner:
            return "Owner does not exist"
        if pet:
            pet.name = name
            pet.species = species
            pet.breed = breed
            pet.age = age
            pet.owner_id=db_owner[0]

        db.commit()
        db.refresh(pet)

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
        raise HTTPException(status_code=400,detail="invalid id")
    
@app.get("/pets/{pet_id}/visits",tags=["Visits"])
def get_pets_create(pet_id:int,db=Depends(get_db)):
    stmt=select(Visits.pet_id,Visits.reason,Visits.notes,Visits.visit_date).where(Visits.pet_id==pet_id)
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
        raise HTTPException(status_code=400,detail="No pet with the mentioned id")
    elif db_pet:
        visit=Visit(pet_id,reason,notes,visit_date)
        try:
           validated_visit=Valid_Visits.model_validate(visit)
        except Exception as e:
            raise HTTPException(status_code=400,detail=str(e))

        db_visit=Visits(pet_id=validated_visit.pet_id,reason=validated_visit.reason,notes=validated_visit.notes,visit_date=validated_visit.visit_date,created_at=datetime.now(UTC))
        db.add(db_visit)
        db.commit()

        return "Created the visit for pet"

@app.put("/pets/{pet_id}/visits",tags=["Visits"])
def put_pet_visits(pet_id:int,reason:str|None,notes:str|None,visit_date:date|None=None,db=Depends(get_db)):
    stmt=select(Pets).where(Pets.id==pet_id)
    db_pet = db.execute(stmt).scalar_one_or_none()

    if not db_pet:
        raise HTTPException(status_code=400,detail="No pet with the mentioned id")
    elif db_pet:
        visit=Visit(pet_id,reason,notes,visit_date)
        try:
           validated_visit=Valid_Visits.model_validate(visit)
        except Exception as e:
            raise HTTPException(status_code=400,detail=str(e))
        if reason:
         db_pet.reason=validated_visit.reason
        if notes:
         db_pet.notes=validated_visit.notes
        if visit_date:
         db_pet.visit_date=validated_visit.visit_date
        
        db.commit()
        db.refresh(db_pet)


        














    

    





