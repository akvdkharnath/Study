
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer

from typing import Optional
from sqlalchemy.orm import Session
import json

from app.models.base_model import get_db
from app.schema.profile import ProfileCreate, Profile
from app.services.v1.profile import ProfileOperations

profile_router = APIRouter(
    prefix = '/api/v1/profile',
    tags = ["PROFILE"]
    )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@profile_router.get("/token/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}

@profile_router.post('/', status_code=200, description= "API to create profile", response_model= Profile)
def create_profile(data:ProfileCreate, db: Session = Depends(get_db)):
    data = jsonable_encoder(data)
    # return 1
    return JSONResponse(content=jsonable_encoder(ProfileOperations.create_profile(db, data)))


