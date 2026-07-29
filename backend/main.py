import os
from typing import List

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import Base, engine, get_db

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GitHub Explorer API",
    description="API de historico de buscas e favoritos do GitHub Explorer",
    version="1.0.0",
)

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


# ---------- Buscas ----------


@app.post(
    "/buscas",
    response_model=schemas.BuscaOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Buscas"],
)
def criar_busca(busca: schemas.BuscaCreate, db: Session = Depends(get_db)):
    return crud.criar_busca(db, busca)


@app.get("/buscas", response_model=List[schemas.BuscaOut], tags=["Buscas"])
def listar_buscas(limite: int = 20, db: Session = Depends(get_db)):
    return crud.listar_buscas(db, limite)


@app.delete(
    "/buscas/{busca_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Buscas"],
)
def deletar_busca(busca_id: int, db: Session = Depends(get_db)):
    if not crud.deletar_busca(db, busca_id):
        raise HTTPException(status_code=404, detail="Busca nao encontrada")


@app.delete("/buscas", tags=["Buscas"])
def limpar_buscas(db: Session = Depends(get_db)):
    total = crud.limpar_buscas(db)
    return {"removidas": total}


# ---------- Favoritos ----------


@app.post(
    "/favoritos",
    response_model=schemas.FavoritoOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Favoritos"],
)
def criar_favorito(
    favorito: schemas.FavoritoCreate, db: Session = Depends(get_db)
):
    if crud.buscar_favorito_por_repo_id(db, favorito.repo_id):
        raise HTTPException(
            status_code=409, detail="Repositorio ja esta nos favoritos"
        )
    return crud.criar_favorito(db, favorito)


@app.get(
    "/favoritos", response_model=List[schemas.FavoritoOut], tags=["Favoritos"]
)
def listar_favoritos(db: Session = Depends(get_db)):
    return crud.listar_favoritos(db)


@app.patch(
    "/favoritos/{favorito_id}",
    response_model=schemas.FavoritoOut,
    tags=["Favoritos"],
)
def atualizar_favorito(
    favorito_id: int,
    dados: schemas.FavoritoUpdate,
    db: Session = Depends(get_db),
):
    db_favorito = crud.atualizar_favorito(db, favorito_id, dados)
    if not db_favorito:
        raise HTTPException(status_code=404, detail="Favorito nao encontrado")
    return db_favorito


@app.delete(
    "/favoritos/{favorito_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Favoritos"],
)
def deletar_favorito(favorito_id: int, db: Session = Depends(get_db)):
    if not crud.deletar_favorito(db, favorito_id):
        raise HTTPException(status_code=404, detail="Favorito nao encontrado")
        # ---------- Usuarios favoritos ----------


@app.post(
    "/usuarios-favoritos",
    response_model=schemas.UsuarioFavoritoOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Usuarios Favoritos"],
)
def criar_usuario_favorito(
    usuario: schemas.UsuarioFavoritoCreate, db: Session = Depends(get_db)
):
    if crud.buscar_usuario_favorito_por_login(db, usuario.login):
        raise HTTPException(
            status_code=409, detail="Usuario ja esta nos favoritos"
        )
    return crud.criar_usuario_favorito(db, usuario)


@app.get(
    "/usuarios-favoritos",
    response_model=List[schemas.UsuarioFavoritoOut],
    tags=["Usuarios Favoritos"],
)
def listar_usuarios_favoritos(db: Session = Depends(get_db)):
    return crud.listar_usuarios_favoritos(db)


@app.patch(
    "/usuarios-favoritos/{usuario_id}",
    response_model=schemas.UsuarioFavoritoOut,
    tags=["Usuarios Favoritos"],
)
def atualizar_usuario_favorito(
    usuario_id: int,
    dados: schemas.UsuarioFavoritoUpdate,
    db: Session = Depends(get_db),
):
    db_usuario = crud.atualizar_usuario_favorito(db, usuario_id, dados)
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return db_usuario


@app.delete(
    "/usuarios-favoritos/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Usuarios Favoritos"],
)
def deletar_usuario_favorito(usuario_id: int, db: Session = Depends(get_db)):
    if not crud.deletar_usuario_favorito(db, usuario_id):
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")