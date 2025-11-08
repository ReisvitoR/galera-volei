"""
Utilitários para validação de categorias e classificações
"""
from app.models.enums import TipoUsuario, CategoriaPartida


def usuario_pode_participar(tipo_usuario: TipoUsuario, categoria_partida: CategoriaPartida) -> bool:
    """
    Verifica se um usuário pode participar de uma partida baseado na categoria.
    
    Regras:
    - LIVRE: Qualquer jogador pode participar
    - NOOB: Apenas jogadores noob
    - AMADOR: Amadores e jogadores de nível superior
    - INTERMEDIARIO: Intermediários e avançados
    - AVANCADO: Apenas jogadores avançados
    """
    
    if categoria_partida == CategoriaPartida.LIVRE:
        return True
    
    if categoria_partida == CategoriaPartida.NOOB:
        return tipo_usuario == TipoUsuario.NOOB
    
    if categoria_partida == CategoriaPartida.AMADOR:
        return tipo_usuario in [TipoUsuario.AMADOR, TipoUsuario.INTERMEDIARIO, TipoUsuario.PROPLAYER]
    
    if categoria_partida == CategoriaPartida.INTERMEDIARIO:
        return tipo_usuario in [TipoUsuario.INTERMEDIARIO, TipoUsuario.PROPLAYER]
    
    if categoria_partida == CategoriaPartida.AVANCADO:
        return tipo_usuario == TipoUsuario.PROPLAYER
    
    return False


def get_categorias_permitidas(tipo_usuario: TipoUsuario) -> list[CategoriaPartida]:
    """
    Retorna as categorias de partidas que um usuário pode participar
    """
    categorias = [CategoriaPartida.LIVRE]
    
    if tipo_usuario == TipoUsuario.NOOB:
        categorias.append(CategoriaPartida.NOOB)
    
    elif tipo_usuario == TipoUsuario.AMADOR:
        categorias.append(CategoriaPartida.AMADOR)
    
    elif tipo_usuario == TipoUsuario.INTERMEDIARIO:
        categorias.extend([CategoriaPartida.AMADOR, CategoriaPartida.INTERMEDIARIO])
    
    elif tipo_usuario == TipoUsuario.PROPLAYER:
        categorias.extend([
            CategoriaPartida.AMADOR, 
            CategoriaPartida.INTERMEDIARIO, 
            CategoriaPartida.AVANCADO
        ])
    
    return categorias


def get_nivel_minimo_categoria(categoria: CategoriaPartida) -> TipoUsuario:
    """
    Retorna o nível mínimo necessário para uma categoria
    """
    nivel_minimo = {
        CategoriaPartida.LIVRE: TipoUsuario.NOOB,
        CategoriaPartida.NOOB: TipoUsuario.NOOB,
        CategoriaPartida.AMADOR: TipoUsuario.AMADOR,
        CategoriaPartida.INTERMEDIARIO: TipoUsuario.INTERMEDIARIO,
        CategoriaPartida.AVANCADO: TipoUsuario.PROPLAYER
    }
    
    return nivel_minimo.get(categoria, TipoUsuario.NOOB)


def get_descricao_categoria(categoria: CategoriaPartida) -> str:
    """
    Retorna uma descrição amigável da categoria
    """
    descricoes = {
        CategoriaPartida.LIVRE: "Aberto para todos os níveis",
        CategoriaPartida.NOOB: "Apenas para iniciantes",
        CategoriaPartida.AMADOR: "Para amadores e jogadores experientes",
        CategoriaPartida.INTERMEDIARIO: "Para intermediários e avançados",
        CategoriaPartida.AVANCADO: "Apenas para jogadores avançados"
    }
    
    return descricoes.get(categoria, "Categoria não definida")