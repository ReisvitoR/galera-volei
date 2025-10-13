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
# Configurar variáveis de ambiente
# Edite o arquivo .env com suas configurações
# SECRET_KEY deve ser alterada em produção

# Inicializar banco com dados de exemplo
python init_db.py
```

**Variáveis de Ambiente Principais:**
```env
PROJECT_NAME="Galera Vôlei API"
SECRET_KEY="sua-chave-secreta-personalizada"
DATABASE_URL="sqlite:///./galera_volei.db"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> **⚠️ Importante**: Sempre utilize uma `SECRET_KEY` única e segura em ambiente de produção.

### 3. **Execução**
```bash
# Desenvolvimento (com hot-reload)
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Produção
uvicorn api:app --host 0.0.0.0 --port 8000
```

### 4. **Testes**
```bash
# Testes rápidos e diretos
python test_simple.py

# Testes profissionais com pytest
pytest test_pytest.py -v

# Testes específicos por categoria
pytest test_pytest.py::TestAuthentication -v
pytest test_pytest.py::TestUsers -v
pytest test_pytest.py::TestMatches -v
```

## 📚 Documentação da API

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

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

✅ **Autenticação JWT completa** com refresh tokens  
✅ **CRUD de usuários** com sistema de roles hierárquico  
✅ **CRUD de partidas** com validações de negócio  
✅ **Sistema de ranking** e estatísticas de performance  
✅ **Middlewares de autorização** baseados em níveis  
✅ **Persistência relacional** com SQLAlchemy ORM  
✅ **Arquitetura SOLID** com separação clara de responsabilidades  
✅ **Documentação automática** OpenAPI/Swagger  
✅ **Validação robusta** com Pydantic schemas  
✅ **Cobertura de testes** completa (21 cenários validados)

## 🧪 Qualidade e Testes

O projeto implementa uma **estratégia de testes abrangente** para garantir confiabilidade:

### **Cobertura de Testes**
- **21 cenários de teste** automatizados
- **100% dos endpoints** validados
- **Status codes** verificados para todos os casos
- **Autenticação e autorização** completamente testadas
- **Testes de performance** básicos incluídos

### **Tipos de Teste**
- **Health Check**: Verificação da saúde da aplicação
- **Autenticação**: Login, registro, validação de tokens
- **Autorização**: Acesso baseado em roles
- **CRUD**: Operações de usuários e partidas
- **Error Handling**: Casos de erro e validação
- **Performance**: Tempos de resposta aceitáveis

## 🔮 Roadmap Futuro

**Funcionalidades Planejadas:**
- [ ] Sistema avançado de candidaturas para partidas
- [ ] Módulo de avaliações pós-jogo
- [ ] Gestão de equipes e formação automática
- [ ] Upload e gerenciamento de avatares
- [ ] Sistema de notificações em tempo real
- [ ] Dashboard analytics com métricas avançadas
- [ ] API mobile com endpoints otimizados

## 🎓 Contexto Educacional

Esta aplicação foi desenvolvida como **projeto prático** para demonstrar competências em:

### **Arquitetura de Software**
- Implementação dos **princípios SOLID**
- **Clean Architecture** com separação de camadas
- **Dependency Injection** e inversão de dependências

### **Segurança em APIs**
- **Autenticação JWT** com tokens seguros
- **Autorização baseada em roles** (RBAC)
- **Middleware** customizado para controle de acesso

### **Persistência e Dados**
- **ORM SQLAlchemy** com relacionamentos complexos
- **Migrations** e versionamento de schema
- **Otimização de queries** e performance

### **Desenvolvimento Profissional**
- **APIs REST** seguindo padrões da indústria
- **Documentação automática** OpenAPI/Swagger
- **Testes automatizados** com cobertura completa
- **Versionamento** e práticas DevOps básicas

### **Tecnologias Aplicadas**
- **FastAPI** - Framework web moderno
- **Pydantic** - Validação e serialização
- **SQLAlchemy** - ORM Python robusto
- **JWT** - Autenticação stateless
- **Pytest** - Framework de testes

---

**📚 Programação para Internet II**  
**👨‍🏫 Professor**: Rogério Silva  
**🏛️ IFPI Campus Teresina Central**  