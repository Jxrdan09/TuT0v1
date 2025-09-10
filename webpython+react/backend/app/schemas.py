from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    telegram_id: str

class UserCreate(UserBase):
    password: str
    key: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    subscription_expires_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Key schemas
class UserKeyBase(BaseModel):
    key: str
    duration_days: int = 30

class UserKeyCreate(UserKeyBase):
    pass

class UserKey(UserKeyBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]
    activated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Script schemas
class ScriptBase(BaseModel):
    name: str
    content: str
    language: str

class ScriptCreate(ScriptBase):
    pass

class ScriptUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    language: Optional[str] = None

class Script(ScriptBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Script execution schemas
class ScriptExecutionBase(BaseModel):
    script_id: int

class ScriptExecutionCreate(ScriptExecutionBase):
    pass

class ScriptExecution(ScriptExecutionBase):
    id: int
    status: str
    output: Optional[str] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Gateway schemas
class GatewayBase(BaseModel):
    name: str
    type: str
    config: str

class GatewayCreate(GatewayBase):
    pass

class GatewayUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    config: Optional[str] = None
    is_active: Optional[bool] = None

class Gateway(GatewayBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# User Cookie schemas
class UserCookieBase(BaseModel):
    gateway_type: str
    cookie_data: str

class UserCookieCreate(UserCookieBase):
    pass

class UserCookieUpdate(BaseModel):
    cookie_data: Optional[str] = None
    is_active: Optional[bool] = None

class UserCookie(UserCookieBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Card Check schemas
class CardCheckBase(BaseModel):
    gateway_type: str
    card_number: str
    card_data: str
    status: str
    response_message: Optional[str] = None
    bin_info: Optional[str] = None
    processing_time: Optional[float] = None

class CardCheckCreate(CardCheckBase):
    pass

class CardCheck(CardCheckBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Amazon Gateway specific schemas
class AmazonCardCheck(BaseModel):
    card_data: str  # Formato: "cc|mm|yyyy|cvv"
    cookie: str

class AmazonCardResult(BaseModel):
    card_number: str
    status: str
    response_message: str
    bin_info: dict
    processing_time: float
