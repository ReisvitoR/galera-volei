import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Galera Vôlei API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API para sistema de marcação de partidas de vôlei"
    
    # CORS
    ALLOWED_HOSTS: List[str] = Field(default=["*"])
    
    # Database
    DATABASE_URL: str = "postgresql://koyeb-adm:npg_h9oeRMuWa3Li@ep-broad-rice-a2qzyo05.eu-central-1.pg.koyeb.app/koyebdb"
    
    # Security
    SECRET_KEY: str = "sua-chave-secreta-super-forte-aqui"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Password settings
    PWD_CONTEXT_SCHEMES: List[str] = Field(default=["bcrypt"])
    PWD_CONTEXT_DEPRECATED: str = "auto"
    
    model_config = {
        "env_file": os.getenv("ENV_FILE", ".env"),
        "case_sensitive": True
    }


settings = Settings()