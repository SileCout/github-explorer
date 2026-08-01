# GitHub Explorer

Aplicação web para pesquisar usuários e repositórios públicos do GitHub, com
contas pessoais, histórico e favoritos isolados por usuário.

## Funcionalidades

- Cadastro e login com senha protegida por hash Argon2
- Sessões autenticadas por token com expiração
- Busca de usuários e repositórios pela API pública do GitHub
- Histórico de buscas privado por conta
- Repositórios e usuários favoritos privados por conta
- Notas em favoritos

## Tecnologias

- HTML, CSS e JavaScript
- FastAPI e SQLAlchemy
- PostgreSQL
- Argon2 e JWT

## Configuração local

1. Crie um ambiente virtual dentro de `backend`.
2. Instale as dependências:

   ```powershell
   python -m pip install -r backend/requirements.txt
   ```

3. Copie `backend/.env.example` para `backend/.env` e configure:

   - `DATABASE_URL`: conexão do PostgreSQL;
   - `SECRET_KEY`: chave longa e aleatória para assinar sessões;
   - `ALLOWED_ORIGINS`: endereços autorizados a acessar a API.

   O arquivo `backend/.env` é local e nunca deve ser enviado ao Git.

4. Em um banco novo, crie as tabelas:

   ```powershell
   python backend/init_db.py
   ```

5. Inicie a API:

   ```powershell
   python -m uvicorn main:app --reload --app-dir backend --env-file backend/.env
   ```

6. Sirva o frontend com um servidor local, por exemplo o Live Server na porta
   `5500`.

## Segurança

- Senhas de usuários nunca são armazenadas diretamente.
- Histórico e favoritos sempre são filtrados pela conta autenticada.
- `DATABASE_URL`, `SECRET_KEY` e demais credenciais devem existir somente nas
  variáveis protegidas de cada ambiente.
- Uma credencial que tenha aparecido em um commit deve ser trocada, mesmo após
  ser removida do código.

## Banco existente

`init_db.py` serve para bancos novos. Bancos existentes devem receber uma
migração revisada e testada antes do deploy; não execute alterações de esquema
sem backup e confirmação explícita.
