from typing import List, Optional

from sqlalchemy.orm import Session

import models
import schemas


# ---------- Usuarios ----------


def buscar_usuario_por_email(
    db: Session, email: str
) -> Optional[models.Usuario]:
    return (
        db.query(models.Usuario)
        .filter(models.Usuario.email == email.strip().lower())
        .first()
    )


def criar_usuario(
    db: Session, usuario: schemas.UsuarioCreate, senha_hash: str
) -> models.Usuario:
    db_usuario = models.Usuario(
        nome=usuario.nome.strip(),
        email=usuario.email,
        senha_hash=senha_hash,
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


# ---------- Buscas ----------


def criar_busca(
    db: Session, busca: schemas.BuscaCreate, usuario_id: int
) -> models.Busca:
    db_busca = models.Busca(**busca.model_dump(), usuario_id=usuario_id)
    db.add(db_busca)
    db.commit()
    db.refresh(db_busca)
    return db_busca


def listar_buscas(
    db: Session, usuario_id: int, limite: int = 20
) -> List[models.Busca]:
    return (
        db.query(models.Busca)
        .filter(models.Busca.usuario_id == usuario_id)
        .order_by(models.Busca.buscado_em.desc())
        .limit(limite)
        .all()
    )


def buscar_busca_por_id(
    db: Session, busca_id: int, usuario_id: int
) -> Optional[models.Busca]:
    return (
        db.query(models.Busca)
        .filter(
            models.Busca.id == busca_id,
            models.Busca.usuario_id == usuario_id,
        )
        .first()
    )


def deletar_busca(db: Session, busca_id: int, usuario_id: int) -> bool:
    db_busca = buscar_busca_por_id(db, busca_id, usuario_id)
    if not db_busca:
        return False
    db.delete(db_busca)
    db.commit()
    return True


def limpar_buscas(db: Session, usuario_id: int) -> int:
    total = (
        db.query(models.Busca)
        .filter(models.Busca.usuario_id == usuario_id)
        .delete()
    )
    db.commit()
    return total


# ---------- Favoritos ----------


def criar_favorito(
    db: Session, favorito: schemas.FavoritoCreate, usuario_id: int
) -> models.Favorito:
    db_favorito = models.Favorito(
        **favorito.model_dump(), usuario_id=usuario_id
    )
    db.add(db_favorito)
    db.commit()
    db.refresh(db_favorito)
    return db_favorito


def listar_favoritos(db: Session, usuario_id: int) -> List[models.Favorito]:
    return (
        db.query(models.Favorito)
        .filter(models.Favorito.usuario_id == usuario_id)
        .order_by(models.Favorito.criado_em.desc())
        .all()
    )


def buscar_favorito_por_id(
    db: Session, favorito_id: int, usuario_id: int
) -> Optional[models.Favorito]:
    return (
        db.query(models.Favorito)
        .filter(
            models.Favorito.id == favorito_id,
            models.Favorito.usuario_id == usuario_id,
        )
        .first()
    )


def buscar_favorito_por_repo_id(
    db: Session, repo_id: int, usuario_id: int
) -> Optional[models.Favorito]:
    return (
        db.query(models.Favorito)
        .filter(
            models.Favorito.repo_id == repo_id,
            models.Favorito.usuario_id == usuario_id,
        )
        .first()
    )


def atualizar_favorito(
    db: Session,
    favorito_id: int,
    dados: schemas.FavoritoUpdate,
    usuario_id: int,
) -> Optional[models.Favorito]:
    db_favorito = buscar_favorito_por_id(db, favorito_id, usuario_id)
    if not db_favorito:
        return None

    # exclude_unset evita apagar campos que o cliente nem enviou
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(db_favorito, campo, valor)

    db.commit()
    db.refresh(db_favorito)
    return db_favorito


def deletar_favorito(db: Session, favorito_id: int, usuario_id: int) -> bool:
    db_favorito = buscar_favorito_por_id(db, favorito_id, usuario_id)
    if not db_favorito:
        return False
    db.delete(db_favorito)
    db.commit()
    return True
    # ---------- Usuarios favoritos ----------


def criar_usuario_favorito(
    db: Session, usuario: schemas.UsuarioFavoritoCreate, usuario_id: int
) -> models.UsuarioFavorito:
    db_usuario = models.UsuarioFavorito(
        **usuario.model_dump(), usuario_id=usuario_id
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def listar_usuarios_favoritos(
    db: Session, usuario_id: int
) -> List[models.UsuarioFavorito]:
    return (
        db.query(models.UsuarioFavorito)
        .filter(models.UsuarioFavorito.usuario_id == usuario_id)
        .order_by(models.UsuarioFavorito.criado_em.desc())
        .all()
    )


def buscar_usuario_favorito_por_id(
    db: Session, favorito_id: int, usuario_id: int
) -> Optional[models.UsuarioFavorito]:
    return (
        db.query(models.UsuarioFavorito)
        .filter(
            models.UsuarioFavorito.id == favorito_id,
            models.UsuarioFavorito.usuario_id == usuario_id,
        )
        .first()
    )


def buscar_usuario_favorito_por_login(
    db: Session, login: str, usuario_id: int
) -> Optional[models.UsuarioFavorito]:
    return (
        db.query(models.UsuarioFavorito)
        .filter(
            models.UsuarioFavorito.login == login,
            models.UsuarioFavorito.usuario_id == usuario_id,
        )
        .first()
    )


def atualizar_usuario_favorito(
    db: Session,
    favorito_id: int,
    dados: schemas.UsuarioFavoritoUpdate,
    usuario_id: int,
) -> Optional[models.UsuarioFavorito]:
    db_usuario = buscar_usuario_favorito_por_id(
        db, favorito_id, usuario_id
    )
    if not db_usuario:
        return None

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(db_usuario, campo, valor)

    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def deletar_usuario_favorito(
    db: Session, favorito_id: int, usuario_id: int
) -> bool:
    db_usuario = buscar_usuario_favorito_por_id(
        db, favorito_id, usuario_id
    )
    if not db_usuario:
        return False
    db.delete(db_usuario)
    db.commit()
    return True
