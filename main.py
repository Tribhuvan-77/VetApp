from fastapi import FastAPI,Request

from routers.owners import router as owners_router
from routers.pets import router as pets_router
from routers.visits import router as visits_router
from routers.users import router as users_router

from Database.database import Base,engine
import logging
import time

print(Base.metadata.tables.keys())



#this creates table for all the models that inherit base
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.DEBUG,format="%(asctime)s - %(levelname)s - %(message)s")
app=FastAPI()



@app.on_event("startup")
async def on_startup():
    logging.info("Application started")

@app.on_event("shutdown")
async def on_shutdown():
    logging.info("Application is closesd")
   
        

#async ->tells the code to do other works while it runs in backgroud (if the func needs to wait for something)
#await ->pause here until the result is ready
#middleware -> code the sits between a req and code that handles the req
#here -> middleware --> request --> middleware
    
@app.middleware("http")
async def log_request(request:Request,call_next):

    start_time=time.time()

    response=await call_next(request)

    resp_time=time.time()-start_time

    print(f"Method:{request.method} Path:{request.url.path} response_time:{resp_time} status_code:{response.status_code}")

    return response

         

@app.get("/")
def get_home(request:Request):
    return {"Welcome Home"}

#for paginaton->we have page number->tells which page to be shown and page size-> no of records in each page
#offset->(page-1)*page_size --> here we are doing page-1 as offset starts frm 0


app.include_router(owners_router)
app.include_router(pets_router)
app.include_router(visits_router)
app.include_router(users_router)
    
    

    
    

    
    





        














    

    





