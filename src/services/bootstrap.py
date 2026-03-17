from sqlalchemy import select, inspect
from sqlalchemy.orm import Session

from src.core.security import get_password_hash
from src.models.entities import EstruturaTipo, Usuario
from src.models.base import Base
from src.core.config import get_settings
from src.core.db import engine


def ensure_seed_data(db: Session) -> None:
    # Em ambiente serverless (Vercel), lifespan pode nao executar.
    # Cria tabelas se nao existirem.
    insp = inspect(engine)
    if not insp.has_table("usuarios"):
        Base.metadata.create_all(bind=engine)

    settings = get_settings()

    structure_types = [
        ("PLANO_CONTAS", "Plano de Contas"),
        ("DRE", "Estrutura DRE"),
        ("BALANCO", "Estrutura Balanço"),
    ]
    for codigo, nome in structure_types:
        exists = db.scalar(select(EstruturaTipo).where(EstruturaTipo.codigo == codigo))
        if not exists:
            db.add(EstruturaTipo(codigo=codigo, nome=nome))

    admin = db.scalar(select(Usuario).where(Usuario.email == settings.DEFAULT_ADMIN_EMAIL))
    if not admin:
        db.add(
            Usuario(
                nome=settings.DEFAULT_ADMIN_NAME,
                email=settings.DEFAULT_ADMIN_EMAIL,
                senha_hash=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                perfil="ADMIN",
                ativo=True,
            )
        )
    db.commit()
