from pydantic import BaseModel, EmailStr

from src.schemas.common import ORMModel


class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: str


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    senha: str | None = None
    perfil: str | None = None
    ativo: bool | None = None


class UsuarioOut(ORMModel):
    id: int
    nome: str
    email: EmailStr
    perfil: str
    ativo: bool
