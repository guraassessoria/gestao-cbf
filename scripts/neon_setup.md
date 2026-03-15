# Configuração da Neon

## 1. Criar projeto
- Crie um projeto PostgreSQL na Neon.
- Escolha a região mais próxima de você ou do time.

## 2. Obter as duas strings de conexão
No botão **Connect** da Neon, copie:

- **Pooled connection**
- **Direct connection**

## 3. Qual usar
- Runtime da aplicação: `DATABASE_URL` com **pooled**
- Migrações futuras: `DIRECT_DATABASE_URL` com **direct**

## 4. Exemplo
```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@ep-xxxx-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
DIRECT_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@ep-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```
