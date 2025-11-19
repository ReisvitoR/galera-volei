from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.controllers import auth_controller, usuario_controller, partida_controller, convite_controller
from app.middlewares.security import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    InputValidationMiddleware,
    RequestSizeLimitMiddleware
)

# Criar tabelas do banco de dados
Base.metadata.create_all(bind=engine)

# Inicializar aplicação
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar middlewares de segurança (ordem importa: primeiro é executado por último)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)  # 100 req/min por IP
app.add_middleware(InputValidationMiddleware)
app.add_middleware(RequestSizeLimitMiddleware, max_size_mb=10)  # Máximo 10MB por requisição

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas as origens em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Configurar arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    """Redireciona para a página inicial"""
    return RedirectResponse(url="/static/index.html")

@app.get("/health")
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return {
        "status": "ok", 
        "message": "API Galera Vôlei funcionando",
        "version": settings.VERSION
    }

# Incluir routers
app.include_router(auth_controller.router, prefix=settings.API_V1_STR)
app.include_router(usuario_controller.router, prefix=settings.API_V1_STR)
app.include_router(partida_controller.router, prefix=settings.API_V1_STR)
app.include_router(convite_controller.router, prefix=f"{settings.API_V1_STR}/convites", tags=["convites"])
