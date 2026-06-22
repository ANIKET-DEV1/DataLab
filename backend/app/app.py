from fastapi import FastAPI
from .router import auth
from .models import models
from fastapi import FastAPI,Request

app=FastAPI()
app.include_router(auth.auth)

@app.get('/')
def start():
    return {"message":"working"}