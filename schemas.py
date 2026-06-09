from pydantic import BaseModel,ConfigDict,Field

from datetime import datetime

class Valid_Pets(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    name:str=Field(min_length=1,max_length=15)
    species:str=Field(min_length=1,max_length=20)
    breed:str=Field(min_length=1,max_length=20)
    age:int=Field(ge=0)
    owner_name:str=Field(min_length=1,max_length=10)
    owner_phone:str=Field(min_length=10,max_length=10)