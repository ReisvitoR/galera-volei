# API Galera Vôlei 🏐

## Sobre o Projeto

API REST desenvolvida em **FastAPI** seguindo os **princípios SOLID** para gerenciar partidas de vôlei com **autenticação JWT**, **persistência em banco de dados** e **autorização baseada em roles**.

## 🏗️ Arquitetura SOLID

### **S** - Single Responsibility Principle
- **Controllers**: Apenas lidam com requisições HTTP
- **Services**: Contêm a lógica de negócio específica
- **Repositories**: Responsáveis apenas pelo acesso aos dados

### **O** - Open/Closed Principle  
- **BaseRepository**: Interface extensível para novos repositories
- **Services**: Podem ser estendidos sem modificar código existente

### **L** - Liskov Substitution Principle
- **Repositories**: Implementações podem ser substituídas
- **Services**: Interfaces consistentes e substituíveis

### **I** - Interface Segregation Principle
- **Middlewares**: Especializados por funcionalidade
- **Schemas**: Separados por contexto (Create, Update, Response)

### **D** - Dependency Inversion Principle
- **Dependency Injection**: Controllers dependem de abstrações
- **Database**: Injetado via dependências do FastAPI

## 📁 Estrutura do Projeto

```
app/
├── controllers/          # Controladores HTTP (API endpoints)
│   ├── auth_controller.py
│   ├── usuario_controller.py
│   └── partida_controller.py
├── services/            # Lógica de negócio
│   ├── auth_service.py
│   ├── usuario_service.py
│   └── partida_service.py
├── repositories/        # Camada de dados
│   ├── base.py
│   ├── usuario_repository.py
│   └── partida_repository.py
├── models/             # Modelos SQLAlchemy
│   ├── models.py
│   └── enums.py
├── schemas/            # Schemas Pydantic
│   └── schemas.py
├── middlewares/        # Autenticação e autorização
│   └── auth.py
└── core/              # Configurações base
    ├── config.py
    ├── database.py
    └── security.py
```

## 🔐 Sistema de Autenticação & Autorização

### **JWT Authentication**
- Tokens JWT para sessões seguras
- Middleware de autenticação automática
- Renovação de tokens

### **Role-Based Authorization**
- **Noob**: Acesso básico
- **Amador**: Funcionalidades intermediárias  
- **Intermediário**: Pode organizar partidas normais
- **Proplayer**: Acesso total (admin)

### **Endpoints Protegidos**
```python
# Requer autenticação
@router.get("/usuarios/me")
def get_profile(current_user: Usuario = Depends(get_current_active_user))

# Requer nível específico  
@router.delete("/usuarios/{id}")
def delete_user(current_user: Usuario = Depends(require_admin()))
```

## 💾 Persistência de Dados

### **SQLAlchemy ORM**
- Modelos relacionais completos
- Migrations automáticas
- Relacionamentos many-to-many

### **Banco de Dados**
- SQLite (desenvolvimento)
- PostgreSQL (produção) - configurável
- Schemas otimizados

### **Relacionamentos**
```python
# Usuário ↔ Partidas (many-to-many)
usuario.partidas_participadas
partida.participantes

# Usuário → Partidas organizadas (one-to-many) 
usuario.partidas_organizadas
partida.organizador
```

## 🚀 Como Executar

### 1. **Instalação**
```bash
# Clonar repositório
git clone <repo-url>
cd galera-volei

# Instalar dependências
pip install -r requirements.txt
```

### 2. **Configuração**
```bash
# Copiar e editar configurações
cp .env.example .env

# Inicializar banco de dados
python init_db.py
```

### 3. **Execução**
```bash
# Desenvolvimento
uvicorn api:app --reload

# Produção
uvicorn api:app --host 0.0.0.0 --port 8000
```

## 📚 Documentação da API

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

## 🔑 Credenciais Padrão

Após executar `init_db.py`:

```
Admin:
Email: admin@galeravolei.com  
Senha: admin123

Usuário Teste:
Email: joao@exemplo.com
Senha: 123456
```

## 🛣️ Principais Endpoints

### **Autenticação**
```http
POST /api/v1/auth/register     # Registrar
POST /api/v1/auth/login        # Login  
POST /api/v1/auth/refresh      # Renovar token
GET  /api/v1/auth/me           # Perfil atual
```

### **Usuários**
```http
GET    /api/v1/usuarios/              # Listar usuários
GET    /api/v1/usuarios/ranking       # Ranking por pontuação
GET    /api/v1/usuarios/melhores-atletas  # Melhores por taxa de vitória
GET    /api/v1/usuarios/{id}          # Detalhes do usuário
PUT    /api/v1/usuarios/{id}          # Atualizar usuário
```

### **Partidas**
```http
POST   /api/v1/partidas/              # Criar partida
GET    /api/v1/partidas/              # Listar ativas
GET    /api/v1/partidas/proximas      # Próximas partidas
GET    /api/v1/partidas/minhas        # Minhas partidas
PATCH  /api/v1/partidas/{id}/ativar   # Ativar partida
PATCH  /api/v1/partidas/{id}/finalizar # Finalizar com pontuação
```

## 🎯 Funcionalidades Implementadas

✅ **Autenticação JWT completa**  
✅ **CRUD de usuários com roles**  
✅ **CRUD de partidas com validações**  
✅ **Sistema de ranking e estatísticas**  
✅ **Middlewares de autorização**  
✅ **Persistência em banco relacional**  
✅ **Arquitetura SOLID**  
✅ **Documentação automática**  
✅ **Validação de dados com Pydantic**

## 🔮 Próximas Funcionalidades

- [ ] Sistema de candidaturas
- [ ] Avaliações de partidas/jogadores  
- [ ] Gestão de equipes
- [ ] Upload de avatares
- [ ] Notificações push
- [ ] Dashboard analytics

## 🎓 Objetivo Educacional

Projeto desenvolvido para demonstrar:

- **Arquitetura limpa** seguindo SOLID
- **Segurança** com JWT e autorização
- **Persistência** com ORM e relacionamentos
- **APIs REST** profissionais com FastAPI
- **Boas práticas** de desenvolvimento Python

---

**Programação para Internet II**  
**Professor**: Rogério Silva  
**IFPI Campus Teresina Central**