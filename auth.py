from jose import jwt
from datetime import datetime,timedelta,UTC
import os
from dotenv import load_dotenv

load_dotenv()

def create_token(id:str,email:str,role:str):
    payload={
        "id":id,
        "email":email,
        "role":role,
        "exp":datetime.now(UTC) + timedelta(minutes=30)
    }

    token=jwt.encode(payload,os.getenv("SECRET_KEY"),algorithm=os.getenv("ALGORITHM"))

    return token
