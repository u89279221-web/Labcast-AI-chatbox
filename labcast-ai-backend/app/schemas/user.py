from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    id: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(..., pattern="^(student|faculty|technician|admin)$")

class UserResponse(BaseModel):
    id: str
    email: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str
