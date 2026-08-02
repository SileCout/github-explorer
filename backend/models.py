from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint

from database import Base


class Usuario(Base):
    """Conta local usada para autenticar e separar os dados."""

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)


class Busca(Base):
    """Historico de usuarios pesquisados."""

    __tablename__ = "buscas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    username = Column(String(100), nullable=False, index=True)
    avatar_url = Column(String(300), nullable=True)
    buscado_em = Column(DateTime, default=datetime.utcnow, nullable=False)


class Favorito(Base):
    """Repositorios marcados como favoritos."""

    __tablename__ = "favoritos"
    __table_args__ = (
        UniqueConstraint("usuario_id", "repo_id", name="uq_favorito_usuario_repo"),
    )

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    repo_id = Column(Integer, nullable=False, index=True)
    nome = Column(String(200), nullable=False)
    full_name = Column(String(300), nullable=False)
    descricao = Column(Text, nullable=True)
    url = Column(String(300), nullable=False)
    linguagem = Column(String(100), nullable=True)
    estrelas = Column(Integer, default=0)
    nota = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
class UsuarioFavorito(Base):
    """Usuarios do GitHub marcados como favoritos."""

    __tablename__ = "usuarios_favoritos"
    __table_args__ = (
        UniqueConstraint("usuario_id", "login", name="uq_usuario_favorito_conta_login"),
    )

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    login = Column(String(100), nullable=False, index=True)
    nome = Column(String(200), nullable=True)
    avatar_url = Column(String(300), nullable=True)
    url = Column(String(300), nullable=False)
    bio = Column(Text, nullable=True)
    nota = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
