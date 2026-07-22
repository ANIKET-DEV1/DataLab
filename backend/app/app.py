from uuid import UUID
from fastapi import FastAPI,Request,Depends,HTTPException,status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from .dependencies import deps
from backend.app.schemas.dataset import Dataset
from .router import auth,dataset
from .models import models
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from urllib.parse import quote
from .middleware.rate_limiting import limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
app=FastAPI()
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request:Request,exc:RateLimitExceeded):
    response = JSONResponse(
        status_code=429,
        content={"detail":"Too many Request!"}
    )
    if hasattr(request.state, "view_rate_limit"):
        limiter._inject_headers(
            response,
            request.state.view_rate_limit
        )
    return response

templates = Jinja2Templates(directory=deps.APP_DIR/"frontend/templates")
app.mount("/static", StaticFiles(directory=deps.APP_DIR/"frontend/static"), name="static")
app.include_router(auth.auth)
app.include_router(dataset.router)

@app.get('/')
async def start(request: Request):
    try:
        from .database.session import get_db as _get_db
        from .dependencies.deps import get_current_user as _get_user
        async for db in _get_db():
            user = await _get_user(request, db)

            return RedirectResponse(url='/datasets/view', status_code=303)
    except HTTPException:

        return templates.TemplateResponse(name="landing.html", request=request)

@app.get('/landing', response_class=HTMLResponse)
def get_landing_page(request: Request):
    """Public landing / marketing page."""
    return templates.TemplateResponse(name="landing.html", request=request)

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

@app.get("/change-password", response_class=HTMLResponse)
def passwordreset(request: Request):
    return templates.TemplateResponse(
        name="password-reset.html", 
        request=request,
        )

@app.get("/email-verify", response_class=HTMLResponse)
def getMail(request: Request, ):
    return templates.TemplateResponse(
        name="get-email.html", 
        request=request,
        )

@app.get("/mail-verification", response_class=HTMLResponse)
def getMail(request: Request,
            token:str ):
    return templates.TemplateResponse(
        name="verify-email.html", 
        request=request,
        )