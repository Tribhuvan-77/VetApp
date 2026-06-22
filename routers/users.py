from fastapi import Request,Depends,HTTPException,Cookie,APIRouter,Response
import logging
from sqlalchemy import select
from Database.database import get_db
from schemas import Valid_Users,Valid_UserLogin
from Database.models import Users
from passlib.context import CryptContext
from datetime import datetime,UTC,date
from auth import create_token,decode_token

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

router=APIRouter(prefix="/auth",tags=["Users"])

class User:
    name:str
    email:str
    password_hash:str
    role:str

    def __init__(self,name,email,password_hash,role):
        self.name=name


@router.post("/register")
def post_users(validated_user:Valid_Users,db=Depends(get_db)):
    logging.info(validated_user.password_hash)
    logging.info(len(validated_user.password_hash))
    logging.info(type(validated_user.password_hash.encode()))
    try:
     hashed_password=pwd_context.hash(validated_user.password_hash)
    except Exception as e:
        return HTTPException(status_code=400,detail=str(e))
    
    db_user=Users(name=validated_user.name,email=validated_user.email,password_hash=hashed_password,role=validated_user.role.value.upper(),created_at=datetime.now(UTC))
    logging.info(db_user.role)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        print(type(e))
        print(e)
        raise HTTPException(status_code=400,detail=str(e))

    logging.info("Created user entry")
    return "Created User entry"

@router.post("/login")
def post_user_login(user_login:Valid_UserLogin,db=Depends(get_db)):
    stmt=select(Users).where(Users.email==user_login.email)
    db_user=db.execute(stmt).scalar_one_or_none()

    if not db_user:
        raise HTTPException(status_code=400,detail="User not existing")
    if not pwd_context.verify(user_login.password_hash,db_user.password_hash):
        raise HTTPException(status_code=400,detail="Incorrect password")
    
    token=create_token(str(db_user.id),db_user.email,db_user.role.value)
    response=Response()
    response.set_cookie(key="login_token",value=token,httponly=True)
    
    logging.info("Login successful")
    return response

#when we are writing Cookie(None)-> it means we are telling fastapi that the parameter comes from a cookie-> by setting it to Cookie() obj
@router.get("/user-context")
def get_user_context(request:Request):
    login_token=request.cookies.get("login_token")
    if login_token is None:
        logging.info("authentication failed")
        raise HTTPException(status_code=404,detail={"success":"false","Reason":"Entry not found"})
    try:
     details=decode_token(login_token)
    except Exception as e:
        raise HTTPException(status_code=404,detail={"success":"false","Reason":f"{str(e)}"})
    
    logging.info("Successfully returned details")
    return details
    