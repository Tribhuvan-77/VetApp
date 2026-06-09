from fastapi import FastAPI,Request,Depends,Form,HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from Database.database import Base,engine,get_db
from Database.models import Pets
from schemas import Valid_Pets

from fastapi.templating import Jinja2Templates
from datetime import datetime,UTC

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
        

@app.get("/")
def get_home(request:Request):
    response=templates.TemplateResponse(request,"home.html")
    return response

@app.get("/pets")
def get_pets(request:Request,db=Depends(get_db)):
    stmt=select(Pets.id,Pets.name)
    db_user=db.execute(stmt).all()
    resp_dict={}
    for i in db_user:
        resp_dict[i[0]]=i[1]
    return resp_dict


@app.get("/pets/create")
def get_createpets(request:Request):
    response=templates.TemplateResponse(request,"create.html")
    return response
@app.post("/pets/create")
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

@app.get("/pets/delete")
def get_pets_delete(request:Request):
    response=templates.TemplateResponse(request,"delete.html")
    return response


@app.post("/pets/delete")
def delete_pets_delete(request:Request,db=Depends(get_db),id:int=Form(...)):
    stmt=select(Pets).where(Pets.id==id)
    pet=db.scalar(stmt)

    if pet:
        db.delete(pet)
        db.commit()
    response=RedirectResponse(url="/",status_code=303)
    return response

@app.get("/pets/update")
def get_pets_update(request:Request):
    response=templates.TemplateResponse(request,"check.html")
    return response

@app.post("/pets/check")
def post_pets_check(request:Request,id:int=Form(...),db=Depends(get_db)):
    stmt=select(Pets).where(Pets.id==id)
    db_pet = db.execute(stmt).scalar_one_or_none()


    if db_pet:
        response=templates.TemplateResponse(request,"update.html",{"pet":db_pet})
        return response
    else:
        raise HTTPException(status_code=400,detail="id not valid")
@app.post("/pets/update")
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


@app.get("/pets/{pet_id}")
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


    

    


