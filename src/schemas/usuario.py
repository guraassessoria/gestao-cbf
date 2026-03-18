from pydantic import BaseModel, EmailStr

from src.models.enums import Perfil
from src.schemas.common import ORMModel


class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: Perfil


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    senha: str | None = None
    perfil: Perfil | None = None
    ativo: bool | None = None


class UsuarioOut(ORMModel):
    id: int
    nome: str
    email: EmailStr
    perfil: Perfil
    ativo: bool
