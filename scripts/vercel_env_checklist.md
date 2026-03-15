# Checklist de variáveis na Vercel

Crie estas variáveis no projeto da Vercel:

- DATABASE_URL
- DIRECT_DATABASE_URL
- SECRET_KEY
- ACCESS_TOKEN_EXPIRE_MINUTES
- DEFAULT_ADMIN_EMAIL
- DEFAULT_ADMIN_NAME
- DEFAULT_ADMIN_PASSWORD
- APP_BASE_URL
- CORS_ORIGINS

## Valores recomendados

### DATABASE_URL
Use a **pooled connection string** da Neon.

### DIRECT_DATABASE_URL
Use a **direct connection string** da Neon.

### APP_BASE_URL
Após o primeiro deploy, atualize para a URL final da Vercel.
Exemplo:
`https://balancete-mvp-api.vercel.app`

### CORS_ORIGINS
Uma lista separada por vírgula.
Exemplo:
`https://seu-frontend.vercel.app,http://localhost:3000`
