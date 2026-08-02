import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "A variavel de ambiente DATABASE_URL precisa estar definida."
    )

# O Render entrega a URL comecando com "postgres://", mas o SQLAlchemy
# exige "postgresql://". Essa troca evita erro no deploy.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Abre uma sessao por requisicao e fecha no final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
