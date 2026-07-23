import uuid

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..security.auth_handler import PasswordHasher
from fastapi import status

from sqlalchemy.exc import DataError, IntegrityError, SQLAlchemyError
from ..models import models
from ..schemas import auth as user_schema
from ..exceptions_handler.handle_expection import (
    ValidationError,
    UserNotFound,
    InvalidCredentials,
    DataProcessingError,
    DataLabExceptionHandler
)

async def register_user(db: AsyncSession, user_data: user_schema.UserCreate)->models.User:
    try:
        duplicate_check =await db.execute(
            select(models.User).where(
                (models.User.email == user_data.email) | 
                (models.User.username == user_data.username)
            )
        )

        if duplicate_check.scalar():
            raise ValidationError("Username or email address is already registered.")

        hashed_password = PasswordHasher.hash(user_data.password.get_secret_value())
        db_user = models.User(
            username=user_data.username,
            email=user_data.email,
            password=hashed_password 
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return  db_user

    except DataLabExceptionHandler:
        await db.rollback()
        raise
    except IntegrityError:
        await db.rollback()
        raise ValidationError("User with given credentials already exists.")
    except DataError:
        await db.rollback()
        raise ValidationError("Input data exceeds maximum allowed character limits.")
    except SQLAlchemyError as e:
        await db.rollback()
        raise DataProcessingError("A database error occurred during user registration.")
    
async def login(db:AsyncSession,user_data:user_schema.UserLogin):
    try:
        result=await db.execute(
            select(models.User).where(
                user_data.username==models.User.username
            ))
        user=result.scalar()
        if not user:
            raise UserNotFound("Username does not exist.")
        hashed_password=user.password
        passw =  PasswordHasher.verify(user_data.password.get_secret_value(),hashed_password)
        if passw:
            return user
        
        raise InvalidCredentials("Incorrect password. Please try again.") 
    
    except DataLabExceptionHandler:
        raise
    except SQLAlchemyError as e:
        raise DataProcessingError("Database error occurred during user authentication.")


async def update_verify_email(db:AsyncSession,user_id:uuid.UUID):
    try:
        result = await db.execute(select(models.User).where(models.User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFound("User account not found.")
        if user.is_verified:
            raise ValidationError("This account has already been verified.")
        user.is_verified = True
        await db.commit()
        return user
    
    except DataLabExceptionHandler:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise DataProcessingError("Database error occurred while updating email verification status.")
    
async def update_password(db:AsyncSession,user_id:uuid.UUID,cred=user_schema.UserPasswordReset):
    try:
        result = await db.execute(select(models.User).where(models.User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFound("User account not found.")
        
        if PasswordHasher.verify(cred.new_password.get_secret_value(),user.password):
            return user
        
        hashed_password = PasswordHasher.hash(cred.new_password.get_secret_value())
        user.password=hashed_password
        await db.commit()
        return user
    
    except DataLabExceptionHandler:
        await db.rollback()
        raise
    except SQLAlchemyError:
        await db.rollback()
        raise DataProcessingError("Database error occurred while resetting user password.")

async def get_user(db:AsyncSession,email:user_schema.ResetPasswordRequest):
    try :
        result = await db.execute(select(models.User).where(models.User.email == email.email))
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFound("No account found with the provided email address.")
        
        return  user
    except DataLabExceptionHandler:
        raise
    except SQLAlchemyError:
        raise DataProcessingError("Database error occurred while fetching user details.")
    



