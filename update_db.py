"""
Script para atualizar estrutura do banco sem remover dados existentes
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import engine, SessionLocal, Base
from app.models import Convite
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_db():
    """Atualizar estrutura do banco de dados"""
    logger.info(" Atualizando estrutura do banco de dados...")
    
    try:
        # Criar apenas as tabelas que não existem
        Base.metadata.create_all(bind=engine)
        logger.info(" Estrutura do banco atualizada com sucesso")
        
        # Verificar se a tabela de convites existe
        db = SessionLocal()
        try:
            # Tentar fazer uma query simples na tabela convites
            result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='convites';"))
            tables = result.fetchall()
            
            if tables:
                logger.info(" Tabela 'convites' existe")
            else:
                logger.warning(" Tabela 'convites' não encontrada")
            
            # Verificar se a coluna 'publica' existe na tabela partidas
            result = db.execute(text("PRAGMA table_info(partidas);"))
            columns = result.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'publica' in column_names:
                logger.info(" Coluna 'publica' existe na tabela partidas")
            else:
                logger.warning(" Coluna 'publica' não encontrada na tabela partidas")
                logger.info(" Tentando adicionar coluna 'publica'...")
                try:
                    db.execute(text("ALTER TABLE partidas ADD COLUMN publica BOOLEAN DEFAULT TRUE;"))
                    db.commit()
                    logger.info(" Coluna 'publica' adicionada com sucesso")
                except Exception as e:
                    logger.error(f" Erro ao adicionar coluna 'publica': {e}")
            
            logger.info("\n Verificação da estrutura do banco concluída!")
            logger.info(" Tabelas verificadas:")
            logger.info("   - Tabela convites")
            logger.info("   - Coluna partidas.publica")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f" Erro ao atualizar banco: {e}")
        raise


if __name__ == "__main__":
    update_db()