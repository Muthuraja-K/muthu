from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenRequest(BaseModel):
    token: str

class StockRequest(BaseModel):
    ticker: str
    sector: str
    isxticker: Optional[bool] = False

class StockUpdateRequest(BaseModel):
    oldTicker: str
    ticker: Optional[str] = None
    sector: str
    isxticker: Optional[bool] = False

class StockDeleteRequest(BaseModel):
    ticker: str

class SectorRequest(BaseModel):
    sector: str

class SectorUpdateRequest(BaseModel):
    oldSector: str
    newSector: str

class SectorDeleteRequest(BaseModel):
    sector: str

class UserRequest(BaseModel):
    username: str
    password: str
    role: str
    firstname: str
    lastname: str

class UserUpdateRequest(BaseModel):
    oldUsername: str
    username: str
    password: Optional[str] = ""
    role: str
    firstname: str
    lastname: str

class UserDeleteRequest(BaseModel):
    username: str 