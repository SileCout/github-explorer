"""Cria as tabelas em um banco novo configurado por DATABASE_URL."""

import models  # noqa: F401 - registra os modelos no metadata
from database import Base, engine


def main():
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas ou ja existentes.")


if __name__ == "__main__":
    main()
