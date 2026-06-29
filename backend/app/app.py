from fastapi import FastAPI,Request,Depends,HTTPException,status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from .router import auth,dataset,deps
from .models import models
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from urllib.parse import quote

app=FastAPI()

APP_DIR = Path(__file__).resolve().parent.parent.parent

templates = Jinja2Templates(directory=APP_DIR/"frontend/templates")

#
app.mount("/static", StaticFiles(directory=APP_DIR/"frontend/static"), name="static")
app.include_router(auth.auth)
app.include_router(dataset.router)


@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED and "text/html" in request.headers.get("accept", "").lower():
        next_path = request.url.path
        if request.url.query:
            next_path = f"{next_path}?{request.url.query}"
        return RedirectResponse(url=f"/login?next={quote(next_path)}", status_code=303)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get('/')
def start(request:Request,user:models.User=Depends(deps.get_current_user)):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "username":user.username
        }
        )

@app.get("/login", response_class=HTMLResponse)
def get_login_page(request: Request):
    return templates.TemplateResponse(
        name="login.html",
        request=request,
        context={"next": request.query_params.get("next", "/")}
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
@app.get("/preview", response_class=HTMLResponse)
def get_preview_page(request: Request, user:models.User=Depends(deps.get_current_user)):
    return templates.TemplateResponse(
        name="preview.html",
        request=request, 
        context={"username": user.username}
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