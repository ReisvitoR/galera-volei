# 🚀 GUIA DE DEPLOY NO FLY.IO

## Pré-requisitos
1. Conta no Fly.io (https://fly.io)
2. Flyctl instalado (https://fly.io/docs/hands-on/install-flyctl/)

## Passo 1: Instalar Flyctl

**Windows (PowerShell):**
```powershell
pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**Ou via Scoop:**
```powershell
scoop install flyctl
```

## Passo 2: Login no Fly.io

```bash
flyctl auth login
```

## Passo 3: Criar a Aplicação

```bash
flyctl launch --name galera-volei --region gru --no-deploy
```

Responda:
- ✅ Would you like to copy its configuration? **YES**
- ✅ Choose a region: **gru (São Paulo)** ou **mia (Miami)** 
- ❌ Would you like to set up a PostgreSQL database? **NO** (usamos SQLite)
- ❌ Would you like to set up a Redis database? **NO**

## Passo 4: Ajustar fly.toml (já está configurado!)

O arquivo `fly.toml` já está pronto com:
- ✅ Região: gru (São Paulo)
- ✅ Porta: 8000
- ✅ Auto-scaling configurado
- ✅ Memory: 256MB (suficiente para início)

## Passo 5: Deploy!

```bash
flyctl deploy
```

## Passo 6: Verificar Status

```bash
flyctl status
flyctl logs
```

## Passo 7: Abrir a Aplicação

```bash
flyctl open
```

Ou acesse: `https://galera-volei.fly.dev`

---

## 🔧 COMANDOS ÚTEIS

### Ver logs em tempo real:
```bash
flyctl logs -a galera-volei
```

### Reiniciar aplicação:
```bash
flyctl apps restart galera-volei
```

### SSH na máquina:
```bash
flyctl ssh console -a galera-volei
```

### Ver informações:
```bash
flyctl info
```

### Escalar verticalmente (mais memória):
```bash
flyctl scale memory 512 -a galera-volei
```

### Escalar horizontalmente (mais instâncias):
```bash
flyctl scale count 2 -a galera-volei
```

---

## 🌐 URLs DA APLICAÇÃO

Após o deploy, sua API estará disponível em:

- **API Base:** `https://galera-volei.fly.dev/api/v1`
- **Docs (Swagger):** `https://galera-volei.fly.dev/docs`
- **Health Check:** `https://galera-volei.fly.dev/`

---

## 📝 TESTANDO A API EM PRODUÇÃO

### 1. Registrar usuário:
```bash
curl -X POST https://galera-volei.fly.dev/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Teste User",
    "email": "teste@example.com",
    "senha": "senha123"
  }'
```

### 2. Login:
```bash
curl -X POST https://galera-volei.fly.dev/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "senha": "senha123"
  }'
```

### 3. Listar partidas:
```bash
curl https://galera-volei.fly.dev/api/v1/partidas/ \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## 🔒 CONFIGURAÇÕES DE SEGURANÇA

### Adicionar secrets (variáveis de ambiente):
```bash
flyctl secrets set SECRET_KEY="sua-chave-secreta-aqui"
flyctl secrets set JWT_SECRET_KEY="outra-chave-secreta"
```

### Listar secrets:
```bash
flyctl secrets list
```

---

## 💰 CUSTOS

**Plano Free do Fly.io inclui:**
- ✅ 3 máquinas compartilhadas
- ✅ 160 GB de tráfego de saída/mês
- ✅ SSL automático

**Sua configuração atual:**
- 1 máquina de 256MB
- Auto-scaling (sobe quando necessário)
- **Custo: GRATUITO** (dentro do free tier)

---

## 🐛 TROUBLESHOOTING

### Aplicação não inicia:
```bash
flyctl logs
```

### Ver configuração atual:
```bash
cat fly.toml
```

### Rebuild forçado:
```bash
flyctl deploy --no-cache
```

### Deletar e recriar:
```bash
flyctl apps destroy galera-volei
flyctl launch
```

---

## 📊 MONITORAMENTO

### Dashboard:
https://fly.io/dashboard

### Métricas:
```bash
flyctl dashboard metrics -a galera-volei
```

---

## 🎉 PRONTO!

Sua API Galera Volei está no ar! 🚀

**Próximo passo:** Configure o frontend para apontar para:
`https://galera-volei.fly.dev/api/v1`