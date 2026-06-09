from fastapi import FastAPI,Request,Depends,Form,HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from Database.database import Base,engine,get_db
from Database.models import Pets,Visits
from schemas import Valid_Pets,Valid_Visits

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
    owner_name:str
    owner_phone:str

    def __init__(self,name,species,breed,age,owner_name,owner_phone):
        self.name=name
        self.species=species
        self.breed=breed
        self.age=age
        self.owner_name=owner_name
        self.owner_phone=owner_phone
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

@app.get("/")
def get_home(request:Request):
    response=templates.TemplateResponse(request,"home.html")
    return response

@app.get("/pets",tags=["Pets"])
def get_pets(request:Request,db=Depends(get_db)):
    stmt=select(Pets.id,Pets.name)
    db_user=db.execute(stmt).all()
    resp_dict={}
    for i in db_user:
        resp_dict[i[0]]=i[1]
    return resp_dict


@app.get("/pets/create",tags=["Pets"])
def get_createpets(request:Request):
    response=templates.TemplateResponse(request,"create.html")
    return response

@app.post("/pets/create",tags=["Pets"])
def post_createpets(request:Request,name:str=Form(...),species:str=Form(...),breed:str=Form(...),age:int=Form(...),owner_name:str=Form(...),owner_phone:str=Form(...),db=Depends(get_db)):
    pet=Pet(name,species,breed,age,owner_name,owner_phone)
    try:
      validated_entry=Valid_Pets.model_validate(pet)
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))
    db_pet=Pets(name=validated_entry.name,species=validated_entry.species,breed=validated_entry.breed,age=validated_entry.age,owner_name=validated_entry.owner_name,owner_phone=validated_entry.owner_phone,created_at=datetime.now(UTC))
    db.add(db_pet)
    db.commit()

    response=RedirectResponse(url="/",status_code=303)
    return response

@app.get("/pets/delete",tags=["Pets"])
def get_pets_delete(request:Request):
    response=templates.TemplateResponse(request,"delete.html")
    return response


@app.post("/pets/delete",tags=["Pets"])
def delete_pets_delete(request:Request,db=Depends(get_db),id:int=Form(...)):
    stmt=select(Pets).where(Pets.id==id)
    pet=db.scalar(stmt)

    if pet:
        db.delete(pet)
        db.commit()
    else:
        raise HTTPException(status_code=400,detail="id not found")
    
    response=RedirectResponse(url="/",status_code=303)
    return response

@app.get("/pets/update",tags=["Pets"])
def get_pets_update(request:Request):
    response=templates.TemplateResponse(request,"check.html")
    return response

@app.post("/pets/check",tags=["Pets"])
def post_pets_check(request:Request,id:int=Form(...),db=Depends(get_db)):
    stmt=select(Pets).where(Pets.id==id)
    db_pet = db.execute(stmt).scalar_one_or_none()


    if db_pet:
        response=templates.TemplateResponse(request,"update.html",{"pet":db_pet})
        return response
    else:
        raise HTTPException(status_code=400,detail="id not valid")
@app.post("/pets/update",tags=["Pets"])
def post_pets_update(request:Request,id: int = Form(...), name: str = Form(...), species: str = Form(...), breed: str = Form(...), age: int = Form(...), owner_name: str = Form(...), owner_phone: str = Form(...),db=Depends(get_db)):
    pet = db.scalar(select(Pets).where(Pets.id == id))

    if pet:
        pet.name = name
        pet.species = species
        pet.breed = breed
        pet.age = age
        pet.owner_name = owner_name
        pet.owner_phone = owner_phone

    db.commit()
    db.refresh(pet)

    response=RedirectResponse(url="/",status_code=303)
    return response


@app.get("/pets/{pet_id}",tags=["Pets"])
def get_petsid(request:Request,pet_id:int,db=Depends(get_db)):
    stmt=select(Pets).where(Pets.id==pet_id)
    db_pet = db.execute(stmt).scalar_one_or_none()
    resp_dict={}
    resp_dict["id"]=db_pet.id
    resp_dict["name"]=db_pet.name
    resp_dict["species"]=db_pet.species
    resp_dict["breed"]=db_pet.breed
    resp_dict["age"]=db_pet.age
    resp_dict["owner_name"]=db_pet.owner_name
    resp_dict["owner_phone"]=db_pet.owner_phone
    resp_dict["created_at"]=db_pet.created_at

    return resp_dict

@app.get("/pets/{pet_id}/create_visits",tags=["Visits"])
def get_pet_createvisit(request:Request,pet_id:int,db=Depends(get_db)):
    stmt=select(Pets).where(Pets.id==pet_id)
    db_pet = db.execute(stmt).scalar_one_or_none()

    if not db_pet:
        raise HTTPException(status_code=400,detail="No pet with the mentioned id")
    elif db_pet:
        response=templates.TemplateResponse(request,"create_visit.html",{"pet_id":pet_id})
        return response
    
@app.post("/pets/{pet_id}/create_visits",tags=["Visits"])
def post_pet_createvisit(request:Request,pet_id:int,reason: str = Form(...),notes: str = Form(...),visit_date: date = Form(...),db=Depends(get_db)):

    visit=Visit(pet_id,reason,notes,visit_date)
    try:
      validated_visit=Valid_Visits.model_validate(visit)
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))

    db_visit=Visits(pet_id=validated_visit.pet_id,reason=validated_visit.reason,notes=validated_visit.notes,visit_date=validated_visit.visit_date,created_at=datetime.now(UTC))
    db.add(db_visit)
    db.commit()

    response=RedirectResponse(url="/pets/{pet_id}/visits",status_code=303)
    return response

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















    

    


