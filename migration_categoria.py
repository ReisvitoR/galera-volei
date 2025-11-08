"""
Script para atualizar o banco de dados com o campo categoria
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import Settings
from app.models.enums import CategoriaPartida

def add_categoria_field():
    """Adicionar campo categoria à tabela partidas"""
    print("=== ADICIONANDO CAMPO CATEGORIA ===")
    
    settings = Settings()
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Verificar se a coluna já existe
            result = conn.execute(text("PRAGMA table_info(partidas)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'categoria' not in columns:
                print("Adicionando coluna 'categoria' à tabela partidas...")
                
                # Adicionar coluna categoria com valor padrão 'livre'
                conn.execute(text("ALTER TABLE partidas ADD COLUMN categoria VARCHAR(20) DEFAULT 'livre'"))
                
                # Atualizar todas as partidas existentes para categoria 'livre'
                conn.execute(text("UPDATE partidas SET categoria = 'livre' WHERE categoria IS NULL"))
                
                conn.commit()
                print("✅ Campo 'categoria' adicionado com sucesso!")
            else:
                print("✅ Campo 'categoria' já existe na tabela partidas")
    
    except Exception as e:
        print(f"❌ Erro ao adicionar campo categoria: {e}")
        raise

def verificar_tipos_usuario():
    """Verificar se os usuários têm tipos válidos"""
    print("\n=== VERIFICANDO TIPOS DE USUÁRIO ===")
    
    settings = Settings()
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Verificar usuários e seus tipos
            result = conn.execute(text("SELECT id, nome, tipo FROM usuarios"))
            usuarios = result.fetchall()
            
            print(f"Encontrados {len(usuarios)} usuários:")
            for usuario in usuarios:
                id_user, nome, tipo = usuario
                print(f"  ID: {id_user}, Nome: {nome}, Tipo: {tipo}")
            
            # Atualizar usuários que podem ter tipos None ou inválidos
            conn.execute(text("UPDATE usuarios SET tipo = 'noob' WHERE tipo IS NULL"))
            conn.commit()
            
            print("✅ Tipos de usuário verificados e atualizados!")
    
    except Exception as e:
        print(f"❌ Erro ao verificar tipos de usuário: {e}")
        raise

def exibir_categorias():
    """Exibir informações sobre as categorias disponíveis"""
    print("\n=== CATEGORIAS DISPONÍVEIS ===")
    
    categorias_info = {
        CategoriaPartida.LIVRE: "Aberto para todos os níveis",
        CategoriaPartida.NOOB: "Apenas para iniciantes",
        CategoriaPartida.AMADOR: "Para amadores e jogadores experientes", 
        CategoriaPartida.INTERMEDIARIO: "Para intermediários e avançados",
        CategoriaPartida.AVANCADO: "Apenas para jogadores avançados"
    }
    
    for categoria, descricao in categorias_info.items():
        print(f"  {categoria.value}: {descricao}")

if __name__ == "__main__":
    try:
        add_categoria_field()
        verificar_tipos_usuario()
        exibir_categorias()
        print("\n🎉 Migração concluída com sucesso!")
    except Exception as e:
        print(f"\n💥 Erro na migração: {e}")
        sys.exit(1)