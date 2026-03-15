from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    perfil: str
    ativo: bool
