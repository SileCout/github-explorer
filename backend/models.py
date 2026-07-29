from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from database import Base


class Busca(Base):
    """Historico de usuarios pesquisados."""

    __tablename__ = "buscas"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, index=True)
    avatar_url = Column(String(300), nullable=True)
    buscado_em = Column(DateTime, default=datetime.utcnow, nullable=False)


class Favorito(Base):
    """Repositorios marcados como favoritos."""

    __tablename__ = "favoritos"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, unique=True, nullable=False, index=True)
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

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(100), unique=True, nullable=False, index=True)
    nome = Column(String(200), nullable=True)
    avatar_url = Column(String(300), nullable=True)
    url = Column(String(300), nullable=False)
    bio = Column(Text, nullable=True)
    nota = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)  