from fastapi import FastAPI,Request
from .router import auth,dataset
from .models import models
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

app=FastAPI()

APP_DIR = Path(__file__).resolve().parent.parent.parent

templates = Jinja2Templates(directory=APP_DIR/"frontend/templates")

#
app.mount("/static", StaticFiles(directory=APP_DIR/"frontend/static"), name="static")
app.include_router(auth.auth)
app.include_router(dataset.router)

@app.get('/')
def start(request:Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            'message':'Succefully html occur'
        }
        )