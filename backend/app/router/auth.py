from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request,Response,status
from typing import Annotated
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from ..schemas import auth as user
from .deps import get_current_user
from ..security import jwt_handler as jwthandler
from ..schemas.token import TokenData
from ..database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..repository.user import update_verify_email,update_password
from ..service.authRepo import for_Auth
from ..models import models
from ..utils.email_verification import email_verification
from ..utils.password_reset import password_mail_verification
from ..database.redis import mail_work_done
#from ..rate_limiter import limiter


auth = APIRouter(prefix="/auth", tags=["Authentication"])

@auth.post("/login")
#@limiter.limit("5/minute")
async def login(request: Request, cred: user.UserLogin, response: Response, auth_repo: for_Auth = Depends()):
    data = await auth_repo.login_user(cred)
    jwthandler.set_auth_cookies(response,data.get("token"))
    return {"message":data.get("message")}

@auth.post("/register")
#@limiter.limit("5/minute")
async def register(request: Request, cred: user.UserCreate, response: Response, auth_repo: for_Auth = Depends()):
    maybe = await auth_repo.create_user(cred)
    if not maybe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return {"message": "Register Sucessful please verify then proceed to login"}

@auth.get("/me")
#@limiter.limit("60/minute")
def getuser(request: Request,response: Response, current_user:models.User=Depends(get_current_user)):
    return {
        "authenticated": True,
        "user": {
            "username": current_user.username,
            "email": current_user.email
        }
    }


@auth.post("/logout")
#@limiter.limit("60/minute")
async def logout(request: Request,
    response: Response,
    current_user:models.User = Depends(get_current_user),
    db : AsyncSession =Depends(get_db)
):
    current_user.logged_out_at= datetime.utcnow()
    
    await db.commit()

    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    return response
    

@auth.get("/verify-email")
async def verify_email(request: Request,
                       reponse:Response,
    token: str = Query(..., description="The cryptographic token sent via email"),
    db: AsyncSession = Depends(get_db)
):
    user_id=email_verification.verify_email_token(token)
    if not user_id:
        raise HTTPException(
            status_code=400, 
            detail="The verification link is invalid or has expired. Please request a new one."
        )
    result = await update_verify_email(db,user_id) 
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    await mail_work_done(email=result.email)
    return {"message": "Succesfully verified"}
    
@auth.post("/password-reset")
#@limiter.limit("3/hour")
async def reset_password(request: Request,
                         response:Response,
    email: user.ResetPasswordRequest,
    auth_repo: for_Auth = Depends()
):
    data = await auth_repo.password_reset(email)
    if not data:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="failed to send mail")
    return {"message":"Check you mail"}


@auth.post("/password-reset-verify")
#@limiter.limit("3/hour")
async def verified_reset_password(request: Request,
                                  response:Response,
    cred:user.UserPasswordReset,
    token:str=Query(...,description="The cryptographic token sent via email"),
    db: AsyncSession = Depends(get_db)
):
    user_id=password_mail_verification.verify_password_reset_token(token)
    print(user_id)
    if not user_id:
        raise HTTPException(
            status_code=400, 
            detail="The verification link is invalid or has expired. Please request a new one."
        )
    result = await update_password(db,user_id,cred=cred)
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error Occured")
    await mail_work_done(email=result.email)
    return {"message":"Succesful"}
