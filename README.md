# Balancete MVP API — Vercel + Neon + GitHub

API FastAPI do MVP de processamento de balancetes mensais, preparada para deploy na Vercel e banco PostgreSQL na Neon.

## O que este projeto cobre

- autenticação JWT
- perfis `ADMIN`, `OPERACIONAL` e `CONSULTA`
- upload e publicação de estruturas
- competências
- processamentos mensais
- upload de balancete e custos com futebol
- validação com erros e alertas
- geração de balanço, DRE e balancete classificado
- OpenAPI em `/docs`

## Estrutura do projeto

```text
src/
  index.py
  main.py
  core/
  models/
  routers/
  schemas/
  services/
sample_data/
scripts/
```

## 1) Neon

Crie um projeto Neon e copie duas connection strings:

- **pooled**: para a aplicação em runtime
- **direct**: para migrações futuras e manutenção

No MVP atual, a aplicação usa `DATABASE_URL`.
`DIRECT_DATABASE_URL` fica documentada para evolução futura.

## 2) GitHub

No PowerShell:

```powershell
git init
git add .
git commit -m "feat: initial balancete mvp api"
gh repo create SEU_USUARIO/balancete-mvp-api --private --source=. --remote=origin --push
```

Se você não usa GitHub CLI, crie o repositório no GitHub e depois:

```powershell
git remote add origin https://github.com/SEU_USUARIO/balancete-mvp-api.git
git branch -M main
git push -u origin main
```

## 3) Vercel

### Pela UI
1. Entre na Vercel.
2. Clique em **Add New Project**.
3. Importe o repositório GitHub.
4. Framework preset: **Other**.
5. Root directory: deixe na raiz.
6. Adicione as variáveis de ambiente:
   - `DATABASE_URL`
   - `DIRECT_DATABASE_URL`
   - `SECRET_KEY`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`
   - `DEFAULT_ADMIN_EMAIL`
   - `DEFAULT_ADMIN_NAME`
   - `DEFAULT_ADMIN_PASSWORD`
   - `APP_BASE_URL`
   - `CORS_ORIGINS`

A Vercel faz deploy automático a cada push no GitHub.

### Pela CLI
```powershell
npm i -g vercel
vercel
vercel env add DATABASE_URL production
vercel env add DIRECT_DATABASE_URL production
vercel env add SECRET_KEY production
vercel env add ACCESS_TOKEN_EXPIRE_MINUTES production
vercel env add DEFAULT_ADMIN_EMAIL production
vercel env add DEFAULT_ADMIN_NAME production
vercel env add DEFAULT_ADMIN_PASSWORD production
vercel env add APP_BASE_URL production
vercel env add CORS_ORIGINS production
vercel --prod
```

## 4) Ambiente local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn src.index:app --reload
```

Acesse:
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/health`

## 5) Fluxo recomendado de uso

1. fazer login em `/auth/login`
2. subir plano de contas
3. subir estrutura DRE
4. subir estrutura de balanço
5. criar competência
6. criar processamento
7. subir balancete
8. subir custos com futebol
9. validar
10. processar
11. consultar resultados

## 6) Observações de arquitetura

- O projeto usa SQLAlchemy síncrono por simplicidade do MVP.
- Para ambiente serverless, a Neon recomenda usar **pooled connection** em runtime e **direct connection** para migrações.
- O schema é criado automaticamente no startup da aplicação. Em MVP isso simplifica bastante.
- Como Vercel Functions são serverless, este projeto evita depender de disco persistente. O conteúdo CSV enviado é armazenado no banco como texto.

## 7) Endpoints principais

- `POST /auth/login`
- `GET /auth/me`
- `GET /usuarios`
- `POST /usuarios`
- `GET /estruturas/em-producao`
- `GET /estruturas/versoes`
- `POST /estruturas/plano-contas/upload`
- `POST /estruturas/dre/upload`
- `POST /estruturas/balanco/upload`
- `GET /competencias`
- `POST /competencias`
- `POST /processamentos`
- `GET /processamentos/{id}`
- `POST /processamentos/{id}/upload-balancete`
- `POST /processamentos/{id}/upload-custos-futebol`
- `POST /processamentos/{id}/validar`
- `POST /processamentos/{id}/processar`
- `POST /processamentos/{id}/reprocessar`
- `GET /processamentos/{id}/validacoes`
- `GET /processamentos/{id}/resultado/balanco`
- `GET /processamentos/{id}/resultado/dre`
- `GET /processamentos/{id}/resultado/balancete-classificado`
- `GET /dashboard`
- `GET /health`
