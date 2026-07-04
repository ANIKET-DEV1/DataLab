from uuid import UUID
from fastapi import FastAPI,Request,Depends,HTTPException,status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from backend.app.schemas.dataset import Dataset
from .router import auth,dataset,deps
from .models import models
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from urllib.parse import quote

app=FastAPI()


templates = Jinja2Templates(directory=deps.APP_DIR/"frontend/templates")

#
app.mount("/static", StaticFiles(directory=deps.APP_DIR/"frontend/static"), name="static")
app.include_router(auth.auth)
app.include_router(dataset.router)


@app.get('/')
def start(request:Request,user:models.User=Depends(deps.get_current_user)):
    return RedirectResponse(url='/datasets/view', status_code=303)

@app.get("/login", response_class=HTMLResponse)
def get_login_page(request: Request):
    return templates.TemplateResponse(
        name="login.html",
        request=request,
        )

@app.get("/register", response_class=HTMLResponse)
def get_register_page(request: Request):
    return templates.TemplateResponse(
        name="register.html", 
        request=request
        )

@app.get("/upload", response_class=HTMLResponse)
def get_upload_page(request: Request, user:models.User=Depends(deps.get_current_user)):
    return templates.TemplateResponse(
        name="upload.html",
        request=request,
        context={"username": user.username}
    )

@app.get('/preview',response_class=HTMLResponse)
def get_preview_page(
    request: Request,
 ):
    return templates.TemplateResponse(
        name="preview.html",
        request=request,
        )

@app.get("/ml", response_class=HTMLResponse)
def get_ml_page(request: Request, user:models.User=Depends(deps.get_current_user)):
    return templates.TemplateResponse(
        name="ml.html",
        request=request, 
        context={"username": user.username})

@app.get("/visualize", response_class=HTMLResponse)
def get_visualize_page(request: Request, 
                       user:models.User=Depends(deps.get_current_user)):
    return templates.TemplateResponse(
        name="visualize.html", 
        request=request, 
        context={"username": user.username})

@app.get("/clean", response_class=HTMLResponse)
def get_clean_page(request: Request, 
                   user:models.User=Depends(deps.get_current_user)):
    return templates.TemplateResponse(
        name="clean.html", 
        request=request,
        context={"username": user.username})