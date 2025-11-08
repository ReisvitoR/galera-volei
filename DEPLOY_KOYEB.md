# 🚀 GUIA DE DEPLOY NO KOYEB

## Vantagens do Koyeb
- ✅ Deploy direto do GitHub
- ✅ SSL automático
- ✅ Free tier generoso
- ✅ Deploy automático a cada push
- ✅ Mais simples que Fly.io

---

## Passo 1: Preparar o Repositório

### 1.1 Commit e Push para GitHub
```bash
git add .
git commit -m "Preparar para deploy no Koyeb"
git push origin main
```

---

## Passo 2: Criar Conta no Koyeb

1. Acesse: https://www.koyeb.com/
2. Clique em **Sign Up**
3. Conecte com sua conta GitHub

---

## Passo 3: Deploy no Koyeb

### Via Interface Web (Recomendado):

1. **No Dashboard do Koyeb**, clique em **Create App**

2. **Select Deployment Method:**
   - Escolha: **GitHub**
   - Autorize o Koyeb a acessar seus repositórios

3. **Select Repository:**
   - Escolha: `ReisvitoR/galera-volei`
   - Branch: `main`

4. **Builder:**
   - Selecione: **Dockerfile**
   - O Koyeb detectará automaticamente o Dockerfile

5. **Environment Variables:** (opcional por enquanto)
   - Deixe em branco (usaremos os padrões)

6. **Service Settings:**
   - **Name:** `galera-volei`
   - **Region:** `Frankfurt` ou `Washington DC` (escolha o mais próximo)
   - **Instance Type:** `Eco` (free tier)
   - **Port:** `8000`
   
7. **Scaling:**
   - Min instances: `1`
   - Max instances: `1`

8. **Advanced Settings:**
   - **Health Check Path:** `/`
   - Deixe o resto como padrão

9. Clique em **Deploy**

---

## Passo 4: Aguardar Deploy

O Koyeb irá:
1. ✅ Clonar seu repositório
2. ✅ Construir a imagem Docker
3. ✅ Fazer deploy
4. ✅ Gerar URL pública

**Tempo estimado:** 3-5 minutos

---

## 🌐 Sua API estará disponível em:

```
https://galera-volei-XXXXXXX.koyeb.app
```

### URLs importantes:
- **API Base:** `https://galera-volei-XXXXXXX.koyeb.app/api/v1`
- **Docs:** `https://galera-volei-XXXXXXX.koyeb.app/docs`
- **Health:** `https://galera-volei-XXXXXXX.koyeb.app/`

---

## 📝 TESTANDO A API

### 1. Verificar se está online:
```bash
curl https://galera-volei-XXXXXXX.koyeb.app/
```

### 2. Acessar documentação:
Abra no navegador: `https://galera-volei-XXXXXXX.koyeb.app/docs`

### 3. Testar registro:
```bash
curl -X POST https://galera-volei-XXXXXXX.koyeb.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Teste User",
    "email": "teste@example.com",
    "senha": "senha123"
  }'
```

---

## 🔄 DEPLOY AUTOMÁTICO

Após configurado, qualquer push no GitHub fará deploy automático!

```bash
git add .
git commit -m "Atualização"
git push origin main
```

O Koyeb detectará o push e fará redeploy automaticamente! 🎉

---

## 📊 MONITORAMENTO

### Ver Logs:
1. Dashboard do Koyeb
2. Selecione sua app
3. Clique em **Logs**
4. Veja logs em tempo real

### Métricas:
- CPU, RAM, Network
- Disponíveis no dashboard

---

## 🐛 TROUBLESHOOTING

### App não inicia:
1. Veja os logs no dashboard
2. Verifique se a porta está correta (8000)
3. Confirme que o Dockerfile está correto

### Erro de build:
1. Verifique se o `requirements.txt` está correto
2. Confirme que o `Dockerfile` está no root do repo

### Redeploy manual:
1. Dashboard → Sua App
2. Clique em **Redeploy**

---

## 💰 CUSTOS

**Free Tier do Koyeb:**
- ✅ 1 serviço
- ✅ Eco instance (gratuita)
- ✅ 100 GB transferência/mês
- ✅ SSL incluído
- ✅ Deploy automático

**Custo: GRATUITO!** 🎉

---

## 🔒 SEGURANÇA (Opcional)

### Adicionar variáveis de ambiente:
1. Dashboard → Sua App
2. **Settings** → **Environment Variables**
3. Adicionar:
   - `SECRET_KEY`: sua-chave-secreta
   - `JWT_SECRET_KEY`: outra-chave-secreta

---

## ⚙️ CUSTOM DOMAIN (Opcional)

1. Dashboard → Sua App
2. **Domains** → **Add Custom Domain**
3. Configure seu domínio (ex: api.galeravolei.com)
4. Atualize os registros DNS conforme instruções

---

## 🎯 CHECKLIST DE DEPLOY

- ✅ Código no GitHub
- ✅ Dockerfile configurado
- ✅ Conta no Koyeb criada
- ✅ App criada no Koyeb
- ✅ Deploy realizado
- ✅ URL funcionando
- ✅ Documentação acessível

---

## 🎉 PRONTO!

Sua API Galera Volei está no ar! 

**Próximo passo:** Configure o frontend para usar:
```
https://galera-volei-XXXXXXX.koyeb.app/api/v1
```

---

## 📌 LINKS ÚTEIS

- Dashboard: https://app.koyeb.com/
- Documentação: https://www.koyeb.com/docs
- Status: https://status.koyeb.com/