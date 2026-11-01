from pydantic import BaseModel

class LoginIn(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str

class RegisterIn(BaseModel):
    username: str
    password: str
    phone: str | None = None

class SmsSendIn(BaseModel):
    phone: str

class SmsLoginIn(BaseModel):
    phone: str
    code: str

class ResetIn(BaseModel):
    username: str
    phone: str
    code: str
    new_password: str
