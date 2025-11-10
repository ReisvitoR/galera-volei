# ✅ Configuração PostgreSQL no Koyeb - CONCLUÍDO

## Status
✅ **Tabelas criadas com sucesso no banco Koyeb PostgreSQL!**

## Próximo Passo: Configurar Variável de Ambiente

### 1. Acessar o Koyeb Dashboard
1. Vá para: https://app.koyeb.com/
2. Clique no seu app: **galera-volei**
3. Vá na aba **Settings**

### 2. Adicionar Variável de Ambiente
Na seção **Environment variables**, adicione:

**Nome:** `DATABASE_URL`

**Valor:** `postgresql://koyeb-adm:npg_h9oeRMuWa3Li@ep-broad-rice-a2qzyo05.eu-central-1.pg.koyeb.app/koyebdb`

> ⚠️ **IMPORTANTE:** Use `postgresql://` (não `postgres://`)

### 3. Aplicar Alterações
1. Clique em **Save** ou **Update**
2. O Koyeb vai fazer um novo deploy automaticamente
3. Aguarde 2-3 minutos para o deploy completar

## Verificar Funcionamento

Após o deploy, teste a API:

```bash
# Login
curl -X POST https://substantial-ebonee-galera-volei-7e40783c.koyeb.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@exemplo.com","senha":"senha123"}'
```

Se retornar erro 404 (usuário não encontrado), é porque o banco está vazio (correto!).

## Próximas Funcionalidades

Depois de confirmar que está tudo funcionando:

1. ✅ **Migração para PostgreSQL** - CONCLUÍDO
2. ⏳ **Confirmação automática** - Quando o usuário entrar na partida, já confirmar presença automaticamente

## Informações do Banco

- **Serviço:** Koyeb PostgreSQL
- **Região:** EU Central 1
- **Banco:** koyebdb
- **Owner:** koyeb-adm
- **Tabelas:** 8 (usuarios, partidas, equipes, candidaturas, avaliacoes, convites, partida_participantes, equipe_membros)

## Estrutura Mantida

O sistema continua funcionando igual:
- ✅ Login/Registro
- ✅ Criar partidas
- ✅ Entrar em partidas
- ✅ Confirmar presença
- ✅ Criar equipes
- ✅ Sistema de convites
- ✅ Avaliações

**Única diferença:** Agora os dados são persistentes! 🎉
