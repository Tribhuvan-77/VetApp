from jose import jwt
from fastapi import Cookie,Depends
from datetime import datetime,timedelta,UTC
from fastapi.security import APIKeyCookie
import os
from dotenv import load_dotenv

load_dotenv()


cookie_scheme = APIKeyCookie(name="login_token",auto_error=True)

def create_token(id:str,email:str,role:str):
    payload={
        "id":id,
        "email":email,
        "role":role,
        "exp":datetime.now(UTC) + timedelta(minutes=30)
    }

    token=jwt.encode(payload,os.getenv("SECRET_KEY"),algorithm=os.getenv("ALGORITHM"))

    return token
def decode_token(login_token:str =Depends(cookie_scheme))->dict:
    payload=jwt.decode(login_token,os.getenv("SECRET_KEY"),algorithms=[os.getenv("ALGORITHM")])
    return payload
