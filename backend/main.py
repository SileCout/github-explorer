import os
from typing import List

from dotenv import load_dotenv
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import get_db
from security import (
    criar_token_acesso,
    gerar_hash_senha,
    ler_usuario_id_token,
    verificar_senha,
)

load_dotenv()

app = FastAPI(
    title="GitHub Explorer API",
    description="API de historico de buscas e favoritos do GitHub Explorer",
    version="1.0.0",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def usuario_atual(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.Usuario:
    erro = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessao invalida ou expirada",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        usuario_id = ler_usuario_id_token(token)
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise erro

    usuario = db.get(models.Usuario, usuario_id)
    if not usuario:
        raise erro
    return usuario

# Origens liberadas para o navegador. Em producao, defina ALLOWED_ORIGINS
# no painel do Render separando por virgula.
origens_padrao = "http://localhost:5500,http://127.0.0.1:5500,https://silecout.github.io"
ALLOWED_ORIGINS = [
    origem.strip()
    for origem in os.getenv("ALLOWED_ORIGINS", origens_padrao).split(",")
    if origem.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def raiz():
    return {"status": "ok", "mensagem": "GitHub Explorer API no ar"}


# ---------- Autenticacao ----------


@app.post(
    "/auth/cadastro",
    response_model=schemas.UsuarioOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Autenticacao"],
)
def cadastrar_usuario(
    usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)
):
    if crud.buscar_usuario_por_email(db, usuario.email):
        raise HTTPException(status_code=409, detail="Email ja cadastrado")

    return crud.criar_usuario(
        db, usuario, gerar_hash_senha(usuario.senha)
    )


@app.post(
    "/auth/login",
    response_model=schemas.TokenOut,
    tags=["Autenticacao"],
)
def login(dados: schemas.LoginCreate, db: Session = Depends(get_db)):
    usuario = crud.buscar_usuario_por_email(db, dados.email)
    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha invalidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return schemas.TokenOut(
        access_token=criar_token_acesso(usuario.id),
        usuario=usuario,
    )


@app.get("/auth/me", response_model=schemas.UsuarioOut, tags=["Autenticacao"])
def consultar_sessao(usuario: models.Usuario = Depends(usuario_atual)):
    return usuario


# ---------- Buscas ----------


@app.post(
    "/buscas",
    response_model=schemas.BuscaOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Buscas"],
)
def criar_busca(
    busca: schemas.BuscaCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(usuario_atual),
):
    return crud.criar_busca(db, busca, usuario.id)


@app.get("/buscas", response_model=List[schemas.BuscaOut], tags=["Buscas"])
def listar_buscas(
    limite: int = 20,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(usuario_atual),
):
    return crud.listar_buscas(db, usuario.id, limite)


@app.delete(
    "/buscas/{busca_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Buscas"],
)
def deletar_busca(
    busca_id: int,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(usuario_atual),
):
    if not crud.deletar_busca(db, busca_id, usuario.id):
        raise HTTPException(status_code=404, detail="Busca nao encontrada")


@app.delete("/buscas", tags=["Buscas"])
def limpar_buscas(
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(usuario_atual),
):
    total = crud.limpar_buscas(db, usuario.id)
    return {"removidas": total}


# ---------- Favoritos ----------


@app.post(
    "/favoritos",
    response_model=schemas.FavoritoOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Favoritos"],
)
def criar_favorito(
    favorito: schemas.FavoritoCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(usuario_atual),
):
    if crud.buscar_favorito_por_repo_id(db, favorito.repo_id, usuario.id):
        raise HTTPException(
            status_code=409, detail="Repositorio ja esta nos favoritos"
        )
    return crud.criar_favorito(db, favorito, usuario.id)


@app.get(
    "/favoritos", response_model=List[schemas.FavoritoOut], tags=["Favoritos"]
)
def listar_favoritos(
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(usuario_atual),
):
    return crud.listar_favoritos(db, usuario.id)


@app.patch(
    "/favoritos/{favorito_id}",
    response_model=schemas.FavoritoOut,
    tags=["Favoritos"],
)
def atualizar_favorito(
    favorito_id: int,
    dados: schemas.FavoritoUpdate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(usuario_atual),
):
    db_favorito = crud.atualizar_favorito(
        db, favorito_id, dados, usuario.id
    )
    if not db_favorito:
        raise HTTPException(status_code=404, detail="Favorito nao encontrado")
    return db_favorito


@app.delete(
    "/favoritos/{favorito_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Favoritos"],
)
def deletar_favorito(
    favorito_id: int,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(usuario_atual),
):
    if not crud.deletar_favorito(db, favorito_id, usuario.id):
        raise HTTPException(status_code=404, detail="Favorito nao encontrado")
        # ---------- Usuarios favoritos ----------


@app.post(
    "/usuarios-favoritos",
    response_model=schemas.UsuarioFavoritoOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Usuarios Favoritos"],
)
def criar_usuario_favorito(
    favorito: schemas.UsuarioFavoritoCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(usuario_atual),
):
    if crud.buscar_usuario_favorito_por_login(
        db, favorito.login, usuario.id
    ):
        raise HTTPException(
            status_code=409, detail="Usuario ja esta nos favoritos"
        )
    return crud.criar_usuario_favorito(db, favorito, usuario.id)


@app.get(
    "/usuarios-favoritos",
    response_model=List[schemas.UsuarioFavoritoOut],
    tags=["Usuarios Favoritos"],
)
def listar_usuarios_favoritos(
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(usuario_atual),
):
    return crud.listar_usuarios_favoritos(db, usuario.id)


@app.patch(
    "/usuarios-favoritos/{usuario_id}",
    response_model=schemas.UsuarioFavoritoOut,
    tags=["Usuarios Favoritos"],
)
def atualizar_usuario_favorito(
    usuario_id: int,
    dados: schemas.UsuarioFavoritoUpdate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(usuario_atual),
):
    db_usuario = crud.atualizar_usuario_favorito(
        db, usuario_id, dados, usuario.id
    )
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return db_usuario


@app.delete(
    "/usuarios-favoritos/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Usuarios Favoritos"],
)
def deletar_usuario_favorito(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(usuario_atual),
):
    if not crud.deletar_usuario_favorito(db, usuario_id, usuario.id):
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
