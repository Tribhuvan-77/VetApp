from jose import jwt
from fastapi import Cookie
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
def decode_token(login_token:str=Cookie(None))->dict:
    payload=jwt.decode(login_token,os.getenv("SECRET_KEY"),algorithms=os.getenv("ALGORITHM"))
    return payload
