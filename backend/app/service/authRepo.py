from .base import BaseRepository
from fastapi import status,Response
from ..schemas import auth as user
from ..security import jwt_handler as jwthandler
from ..repository import user as crud_auth 
from ..models.models import User
from ..core.config import get_config
from ..core.mail import NotificationService
from ..utils.email_verification import email_verification
from ..utils.password_reset import password_mail_verification
from ..database.redis import mail_send,is_mail_send
from ..exceptions_handler.handle_expection import InvalidCredentials, AccessDenied, ValidationError

class for_Auth(BaseRepository,NotificationService):
    async def login_user(self, credential: user.UserLogin):
        user= await crud_auth.login(self.db,user_data=credential)
        if not user:
                raise InvalidCredentials("Invalid username or password.")
        token_payload = {
            "sub": str(user.id),
            "verified":user.is_verified,
        }
        access_token= jwthandler.create_access_token(data=token_payload)
        if not user.is_verified:
            if not await is_mail_send(user.email):
                email_verify_token = email_verification.generate_token(user)

                magic_url = f"{get_config().base_url}/verify-email?token={email_verify_token}"
            
                await NotificationService(self.tasks).send_mail(
                    recipients=[user.email],
                    subject="Please Verify Your DataLab Account Email",
                    context_data={
                        "username":user.username,
                        "url":magic_url
                    },
                    template_name="mail_register.html"
                )
                raise AccessDenied("Please verify your email address before logging in.")
            else:
                raise AccessDenied("Please verify your email address before logging in.")
        

        return {"token":access_token,"message":"Login Successful"}
    
    async def create_user(self,cred: user.UserCreate):
        data = await crud_auth.register_user(self.db,user_data=cred)
        if not data:
                raise ValidationError("Failed to register user. Please check your credentials and try again.")
        
        email_verify_token = email_verification.generate_token(data)

        magic_url = f"{get_config().base_url}/mail-verification?token={email_verify_token}"
        
        await NotificationService(self.tasks).send_mail(
            recipients=[cred.email],
            subject="Welcome to DataLab! Please Verify Your Account",
            context_data={
                "username":cred.username,
                "url":magic_url
            },
            template_name="mail_register.html"
        )
        await mail_send(data.email)
        
        return data

    async def password_reset(self,email:user.ResetPasswordRequest): 
        user=await crud_auth.get_user(db=self.db,email=email)
        if not await is_mail_send(user.email):
                email_verify_token = password_mail_verification.generate_token(user)

                magic_url = f"{get_config().base_url}/change-password?token={email_verify_token}"
            
                await NotificationService(self.tasks).send_mail(
                    recipients=[user.email],
                    subject="DataLab - Reset Your Password",
                    context_data={
                        "username":user.username,
                        "url":magic_url
                    },
                    template_name="mail_password_reset.html"
                )
        else:
            return {"message":"Password reset email already sent. Please check your inbox."}
        
        return {"message":"Password reset email sent successfully."}

        