from pydantic import BaseModel,ConfigDict,Field,EmailStr
from datetime import date

from datetime import datetime


class Valid_Owners(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    name:str=Field(min_length=1,max_length=30)
    phone:str=Field(min_length=10,max_length=10)
    email:EmailStr

class Valid_Pets(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    name:str=Field(min_length=1,max_length=15)
    species:str=Field(min_length=1,max_length=20)
    breed:str=Field(min_length=1,max_length=20)
    age:int=Field(ge=0)
    owner_id:int=Field(ge=0)

class Valid_Visits(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pet_id: int = Field(ge=1)
    reason: str = Field(min_length=1, max_length=50)
    notes: str = Field(min_length=1, max_length=500)
    visit_date: date
