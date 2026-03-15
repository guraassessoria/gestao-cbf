from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import require_roles
from src.core.security import get_password_hash
from src.models.entities import Usuario
from src.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UsuarioOut], dependencies=[Depends(require_roles("ADMIN"))])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.scalars(select(Usuario).order_by(Usuario.nome)).all()


@router.post("", response_model=UsuarioOut, dependencies=[Depends(require_roles("ADMIN"))])
def criar_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    if payload.perfil not in {"ADMIN", "OPERACIONAL", "CONSULTA"}:
        raise HTTPException(status_code=400, detail="Perfil inválido")
    exists = db.scalar(select(Usuario).where(Usuario.email == payload.email))
    if exists:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    user = Usuario(
        nome=payload.nome,
        email=payload.email,
        senha_hash=get_password_hash(payload.senha),
        perfil=payload.perfil,
        ativo=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{usuario_id}", response_model=UsuarioOut, dependencies=[Depends(require_roles("ADMIN"))])
def atualizar_usuario(usuario_id: int, payload: UsuarioUpdate, db: Session = Depends(get_db)):
    user = db.get(Usuario, usuario_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if payload.nome is not None:
        user.nome = payload.nome
    if payload.senha is not None:
        user.senha_hash = get_password_hash(payload.senha)
    if payload.perfil is not None:
        if payload.perfil not in {"ADMIN", "OPERACIONAL", "CONSULTA"}:
            raise HTTPException(status_code=400, detail="Perfil inválido")
        user.perfil = payload.perfil
    if payload.ativo is not None:
        user.ativo = payload.ativo

    db.commit()
    db.refresh(user)
    return user
