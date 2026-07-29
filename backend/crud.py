from typing import List, Optional

from sqlalchemy.orm import Session

import models
import schemas


# ---------- Buscas ----------


def criar_busca(db: Session, busca: schemas.BuscaCreate) -> models.Busca:
    db_busca = models.Busca(**busca.model_dump())
    db.add(db_busca)
    db.commit()
    db.refresh(db_busca)
    return db_busca


def listar_buscas(db: Session, limite: int = 20) -> List[models.Busca]:
    return (
        db.query(models.Busca)
        .order_by(models.Busca.buscado_em.desc())
        .limit(limite)
        .all()
    )


def buscar_busca_por_id(db: Session, busca_id: int) -> Optional[models.Busca]:
    return db.query(models.Busca).filter(models.Busca.id == busca_id).first()


def deletar_busca(db: Session, busca_id: int) -> bool:
    db_busca = buscar_busca_por_id(db, busca_id)
    if not db_busca:
        return False
    db.delete(db_busca)
    db.commit()
    return True


def limpar_buscas(db: Session) -> int:
    total = db.query(models.Busca).delete()
    db.commit()
    return total


# ---------- Favoritos ----------


def criar_favorito(
    db: Session, favorito: schemas.FavoritoCreate
) -> models.Favorito:
    db_favorito = models.Favorito(**favorito.model_dump())
    db.add(db_favorito)
    db.commit()
    db.refresh(db_favorito)
    return db_favorito


def listar_favoritos(db: Session) -> List[models.Favorito]:
    return (
        db.query(models.Favorito)
        .order_by(models.Favorito.criado_em.desc())
        .all()
    )


def buscar_favorito_por_id(
    db: Session, favorito_id: int
) -> Optional[models.Favorito]:
    return (
        db.query(models.Favorito)
        .filter(models.Favorito.id == favorito_id)
        .first()
    )


def buscar_favorito_por_repo_id(
    db: Session, repo_id: int
) -> Optional[models.Favorito]:
    return (
        db.query(models.Favorito)
        .filter(models.Favorito.repo_id == repo_id)
        .first()
    )


def atualizar_favorito(
    db: Session, favorito_id: int, dados: schemas.FavoritoUpdate
) -> Optional[models.Favorito]:
    db_favorito = buscar_favorito_por_id(db, favorito_id)
    if not db_favorito:
        return None

    # exclude_unset evita apagar campos que o cliente nem enviou
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(db_favorito, campo, valor)

    db.commit()
    db.refresh(db_favorito)
    return db_favorito


def deletar_favorito(db: Session, favorito_id: int) -> bool:
    db_favorito = buscar_favorito_por_id(db, favorito_id)
    if not db_favorito:
        return False
    db.delete(db_favorito)
    db.commit()
    return True
    # ---------- Usuarios favoritos ----------


def criar_usuario_favorito(
    db: Session, usuario: schemas.UsuarioFavoritoCreate
) -> models.UsuarioFavorito:
    db_usuario = models.UsuarioFavorito(**usuario.model_dump())
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def listar_usuarios_favoritos(db: Session) -> List[models.UsuarioFavorito]:
    return (
        db.query(models.UsuarioFavorito)
        .order_by(models.UsuarioFavorito.criado_em.desc())
        .all()
    )


def buscar_usuario_favorito_por_id(
    db: Session, usuario_id: int
) -> Optional[models.UsuarioFavorito]:
    return (
        db.query(models.UsuarioFavorito)
        .filter(models.UsuarioFavorito.id == usuario_id)
        .first()
    )


def buscar_usuario_favorito_por_login(
    db: Session, login: str
) -> Optional[models.UsuarioFavorito]:
    return (
        db.query(models.UsuarioFavorito)
        .filter(models.UsuarioFavorito.login == login)
        .first()
    )


def atualizar_usuario_favorito(
    db: Session, usuario_id: int, dados: schemas.UsuarioFavoritoUpdate
) -> Optional[models.UsuarioFavorito]:
    db_usuario = buscar_usuario_favorito_por_id(db, usuario_id)
    if not db_usuario:
        return None

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(db_usuario, campo, valor)

    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def deletar_usuario_favorito(db: Session, usuario_id: int) -> bool:
    db_usuario = buscar_usuario_favorito_por_id(db, usuario_id)
    if not db_usuario:
        return False
    db.delete(db_usuario)
    db.commit()
    return True