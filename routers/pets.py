from fastapi import Request,Depends,HTTPException,APIRouter,Form
import logging
from sqlalchemy import select
from Database.database import get_db
from auth import decode_token
from schemas import Valid_Pets
from Database.models import Pets,Owners
from datetime import datetime,UTC
from auth import decode_token

router=APIRouter(prefix="/pets",tags=["Pets"],dependencies=[Depends(decode_token)])
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

@router.get("")
def get_pets(page_number:int,db=Depends(get_db)):
    page_size=10
    offset=(page_number-1)*page_size
    stmt = select(Pets).offset(offset).limit(page_size)

    db_pets = db.execute(stmt).scalars().all()

    response = []

    for pet in db_pets:
        if not pet.is_deleted:
           response.append({
            "id": pet.id,
            "name": pet.name,
            "species": pet.species,
            "breed": pet.breed,
            "age": pet.age,
            "owner_id": pet.owner_id
        })

    return response

@router.get("/filter")
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

@router.post("/create")
def post_createpets(name:str,species:str,breed:str,age:int,owner_name:str,owner_phone:str,db=Depends(get_db)):

    stmt=select(Owners.id).where(Owners.name==owner_name,Owners.phone==owner_phone)
    db_owner=db.execute(stmt).scalars().all()
    if not db_owner:
        logging.warning("No entry of the owner")
        raise HTTPException(status_code=400,detail="owner not exisiting")
    else:     
        pet=Pet(name,species,breed,age,db_owner[0])
        try:
            validated_entry=Valid_Pets.model_validate(pet)
        except Exception as e:
            logging.warning("Entered details in wrong format")
            raise HTTPException(status_code=422,detail=str(e))
        
        db_pet=Pets(name=validated_entry.name,species=validated_entry.species,breed=validated_entry.breed,age=validated_entry.age,owner_id=validated_entry.owner_id,created_at=datetime.now(UTC))
        db.add(db_pet)
        db.commit()
        logging.info("created a pet entry")
        return "Created the entry"

@router.delete("/delete")
def delete_pets_delete(request:Request,db=Depends(get_db),id:int=Form(...)):
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
    


@router.put("/update")
def put_pets(request:Request,id:int,name:str|None=None,species:str|None=None,breed:str|None=None,age:int|None=None,owner_id:int|None=None,db=Depends(get_db)):

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


@router.get("/{pet_id}")
def get_petsid(request:Request,pet_id:int,db=Depends(get_db)):
    stmt=select(Pets).where(Pets.id==pet_id)
    db_pet = db.execute(stmt).scalar_one_or_none()

    if db_pet:
      response = {
       "id": db_pet.id,
       "name": db_pet.name,
    "species": db_pet.species,
    "breed": db_pet.breed,
    "age": db_pet.age,
    "owner_id": db_pet.owner_id
     }
      return response
    else:
        logging.warning("Pet id not found")
        raise HTTPException(status_code=400,detail="invalid id")