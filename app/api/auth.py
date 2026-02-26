from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import timedelta, datetime
from app.core import database, security
from app.models.models import RoleEnum
from app.schemas import schemas

router = APIRouter()

@router.post("/register", response_model=schemas.UserOut)
async def register_user(user: schemas.UserCreate, db: AsyncIOMotorDatabase = Depends(database.get_db)):
    # Check if user exists
    db_user = await db.users.find_one({"email": user.email})
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = security.get_password_hash(user.password)
    
    # Create the user document
    new_user = {
        "email": user.email,
        "hashed_password": hashed_password,
        "name": user.name,
        "role": user.role.value,  # Store the enum value
        "preferred_language": user.preferred_language,
        "created_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(new_user)
    
    # Return matched Pydantic output
    return {
        "id": str(result.inserted_id),
        "email": user.email,
        "name": user.name,
        "role": RoleEnum(user.role.value),
        "preferred_language": user.preferred_language,
        "created_at": new_user["created_at"]
    }

@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncIOMotorDatabase = Depends(database.get_db)):
    # Find user
    user = await db.users.find_one({"email": form_data.username})
    if not user or not security.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Store email and role in token payload
    access_token = security.create_access_token(
        data={"sub": user["email"], "role": user["role"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
