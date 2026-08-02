import os
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash


ALGORITMO_TOKEN = "HS256"
DURACAO_TOKEN_MINUTOS = 30
password_hash = PasswordHash.recommended()


def gerar_hash_senha(senha: str) -> str:
    return password_hash.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return password_hash.verify(senha, senha_hash)


def criar_token_acesso(usuario_id: int) -> str:
    segredo = os.getenv("SECRET_KEY")
    if not segredo:
        raise RuntimeError(
            "A variavel de ambiente SECRET_KEY precisa estar definida."
        )

    agora = datetime.now(timezone.utc)
    payload = {
        "sub": str(usuario_id),
        "iat": agora,
        "exp": agora + timedelta(minutes=DURACAO_TOKEN_MINUTOS),
    }
    return jwt.encode(payload, segredo, algorithm=ALGORITMO_TOKEN)


def ler_usuario_id_token(token: str) -> int:
    segredo = os.getenv("SECRET_KEY")
    if not segredo:
        raise RuntimeError(
            "A variavel de ambiente SECRET_KEY precisa estar definida."
        )

    payload = jwt.decode(token, segredo, algorithms=[ALGORITMO_TOKEN])
    return int(payload["sub"])
