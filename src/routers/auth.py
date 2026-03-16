from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import get_current_user
from src.core.security import create_access_token, verify_password
from src.models.entities import Usuario
from src.schemas.auth import LoginRequest, MeResponse, TokenResponse
from src.services.bootstrap import ensure_seed_data

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Login via JSON - campos: email + senha"""
    ensure_seed_data(db)
    user = db.scalar(select(Usuario).where(Usuario.email == payload.email))
    if not user or not user.ativo or not verify_password(payload.senha, user.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais invalidas")
    token = create_access_token(subject=str(user.id), extra={"perfil": user.perfil})
    return TokenResponse(access_token=token)


@router.post("/token", response_model=TokenResponse, include_in_schema=False)
def login_oauth2(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login via OAuth2 form (usado pelo Swagger UI Authorize)"""
    ensure_seed_data(db)
    user = db.scalar(select(Usuario).where(Usuario.email == form.username))
    if not user or not user.ativo or not verify_password(form.password, user.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais invalidas")
    token = create_access_token(subject=str(user.id), extra={"perfil": user.perfil})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def me(current_user: Usuario = Depends(get_current_user)):
    return MeResponse.model_validate(current_user)
