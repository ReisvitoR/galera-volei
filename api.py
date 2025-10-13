from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.controllers import auth_controller, usuario_controller, partida_controller

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

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
