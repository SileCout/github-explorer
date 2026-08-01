from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------- Autenticacao ----------


class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=255)
    senha: str = Field(min_length=12, max_length=128)

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, valor: str) -> str:
        email = valor.strip().lower()
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            raise ValueError("Email invalido")
        return email


class UsuarioOut(BaseModel):
    id: int
    nome: str
    email: str
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginCreate(BaseModel):
    email: str
    senha: str

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, valor: str) -> str:
        return valor.strip().lower()


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut


# ---------- Buscas ----------


class BuscaCreate(BaseModel):
    username: str
    avatar_url: Optional[str] = None


class BuscaOut(BaseModel):
    id: int
    username: str
    avatar_url: Optional[str] = None
    buscado_em: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Favoritos ----------


class FavoritoCreate(BaseModel):
    repo_id: int
    nome: str
    full_name: str
    descricao: Optional[str] = None
    url: str
    linguagem: Optional[str] = None
    estrelas: int = 0
    nota: Optional[str] = None


class FavoritoUpdate(BaseModel):
    """Usado no PATCH: so a nota pode ser editada."""

    nota: Optional[str] = None


class FavoritoOut(BaseModel):
    id: int
    repo_id: int
    nome: str
    full_name: str
    descricao: Optional[str] = None
    url: str
    linguagem: Optional[str] = None
    estrelas: int
    nota: Optional[str] = None
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)
    # ---------- Usuarios favoritos ----------


class UsuarioFavoritoCreate(BaseModel):
    login: str
    nome: Optional[str] = None
    avatar_url: Optional[str] = None
    url: str
    bio: Optional[str] = None
    nota: Optional[str] = None


class UsuarioFavoritoUpdate(BaseModel):
    nota: Optional[str] = None


class UsuarioFavoritoOut(BaseModel):
    id: int
    login: str
    nome: Optional[str] = None
    avatar_url: Optional[str] = None
    url: str
    bio: Optional[str] = None
    nota: Optional[str] = None
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)
