from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.security import decode_token
from src.models.entities import Usuario
from src.services.bootstrap import ensure_seed_data

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> Usuario:
    ensure_seed_data(db)
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    user = db.get(Usuario, int(user_id))
    if not user or not user.ativo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")
    return user


def require_roles(*roles: str):
    def checker(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        if current_user.perfil not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para esta ação")
        return current_user
    return checker
