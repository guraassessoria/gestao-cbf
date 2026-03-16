from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    nome: str
    email: str
    perfil: str
    ativo: bool
