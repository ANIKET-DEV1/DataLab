from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from backend.app.models import models
from .dependencies import deps
from .router import auth, dataset
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from .middleware.rate_limiting import limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from .exceptions_handler.handle_expection import DataLabExceptionHandler

app = FastAPI()
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

templates = Jinja2Templates(directory=deps.APP_DIR / "frontend/templates")
error_templates = Jinja2Templates(directory=Path(__file__).parent / "exceptions_handler" / "errors")

app.mount("/static", StaticFiles(directory=deps.APP_DIR/"frontend/static"), name="static")


app.include_router(auth.auth)
app.include_router(dataset.router)


def _wants_html(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    return "text/html" in accept or "application/xhtml+xml" in accept


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    if _wants_html(request):
        response = error_templates.TemplateResponse(
            name="429.html",
            request=request,
            context={"detail": "You have made too many requests in a short period. Please wait a minute before trying again."},
            status_code=429,
        )
    else:
        response = JSONResponse(
            status_code=429,
            content={"detail": "Too many requests!"},
        )
    if hasattr(request.state, "view_rate_limit") and isinstance(response, Response):
        try:
            limiter._inject_headers(
                response,
                request.state.view_rate_limit,
            )
        except Exception:
            pass
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        if _wants_html(request):
            return error_templates.TemplateResponse(
                name="404.html",
                request=request,
                context={"detail": exc.detail or "The endpoint or page you requested does not exist."},
                status_code=404,
            )
        return JSONResponse(status_code=404, content={"detail": exc.detail or "Not Found"})
    elif exc.status_code == 500:
        if _wants_html(request):
            return error_templates.TemplateResponse(
                name="500.html",
                request=request,
                context={"detail": exc.detail or "An internal server error occurred."},
                status_code=500,
            )
        return JSONResponse(status_code=500, content={"detail": exc.detail or "Internal Server Error"})

    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(DataLabExceptionHandler)
async def datalab_exception_handler(request: Request, exc: DataLabExceptionHandler):
    if exc.status_code == 500 and _wants_html(request):
        return error_templates.TemplateResponse(
            name="500.html",
            request=request,
            context={"detail": exc.detail},
            status_code=500,
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    if _wants_html(request):
        return error_templates.TemplateResponse(
            name="500.html",
            request=request,
            context={"detail": "An internal server error occurred on our servers."},
            status_code=500,
        )
    return JSONResponse(status_code=500, content={"detail": "An internal server error occurred."})


@app.get('/')
async def start(request: Request):
    try:
        from .database.session import get_db as _get_db
        from .dependencies.deps import get_current_user as _get_user
        async for db in _get_db():
            user = await _get_user(request, db)

            return RedirectResponse(url='/datasets/view', status_code=303)
    except (StarletteHTTPException, DataLabExceptionHandler):

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
def get_upload_page(request: Request):
    return templates.TemplateResponse(
        name="upload.html",
        request=request
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
def get_ml_page(request: Request):
    return templates.TemplateResponse(
        name="ml.html",
        request=request, 
)

@app.get("/visualize", response_class=HTMLResponse)
def get_visualize_page(request: Request):
    return templates.TemplateResponse(
        name="visualize.html", 
        request=request)

@app.get("/clean", response_class=HTMLResponse)
def get_clean_page(request: Request):
    return templates.TemplateResponse(
        name="clean.html", 
        request=request
        )

@app.get("/change-password", response_class=HTMLResponse)
def passwordreset(request: Request):
    return templates.TemplateResponse(
        name="password-reset.html", 
        request=request,
        )

@app.get("/dashboard",response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        name="index.html", 
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