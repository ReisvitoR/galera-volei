"""
Utilitários para validação de categorias e classificações
"""
from app.models.enums import TipoUsuario, CategoriaPartida


def usuario_pode_participar(tipo_usuario: TipoUsuario, categoria_partida: CategoriaPartida) -> bool:
    """
    Verifica se um usuário pode participar de uma partida baseado na categoria.
    
    Regras:
    - LIVRE: Qualquer jogador pode participar
    - INICIANTE: Apenas jogadores iniciantes
    - INTERMEDIARIO: Intermediários e jogadores acima
    - AVANCADO: Avançados e profissionais
    - PROFISSIONAL: Apenas jogadores profissionais
    """
    
    if categoria_partida == CategoriaPartida.LIVRE:
        return True
    
    if categoria_partida == CategoriaPartida.INICIANTE:
        return tipo_usuario == TipoUsuario.INICIANTE
    
    if categoria_partida == CategoriaPartida.INTERMEDIARIO:
        return tipo_usuario in [TipoUsuario.INTERMEDIARIO, TipoUsuario.AVANCADO, TipoUsuario.PROFISSIONAL]
    
    if categoria_partida == CategoriaPartida.AVANCADO:
        return tipo_usuario in [TipoUsuario.AVANCADO, TipoUsuario.PROFISSIONAL]
    
    if categoria_partida == CategoriaPartida.PROFISSIONAL:
        return tipo_usuario == TipoUsuario.PROFISSIONAL
    
    return False


def get_categorias_permitidas(tipo_usuario: TipoUsuario) -> list[CategoriaPartida]:
    """
    Retorna as categorias de partidas que um usuário pode participar
    """
    categorias = [CategoriaPartida.LIVRE]
    
    if tipo_usuario == TipoUsuario.INICIANTE:
        categorias.append(CategoriaPartida.INICIANTE)
    
    elif tipo_usuario == TipoUsuario.INTERMEDIARIO:
        categorias.extend([CategoriaPartida.INICIANTE, CategoriaPartida.INTERMEDIARIO])
    
    elif tipo_usuario == TipoUsuario.AVANCADO:
        categorias.extend([
            CategoriaPartida.INICIANTE, 
            CategoriaPartida.INTERMEDIARIO, 
            CategoriaPartida.AVANCADO
        ])
    
    elif tipo_usuario == TipoUsuario.PROFISSIONAL:
        categorias.extend([
            CategoriaPartida.INICIANTE,
            CategoriaPartida.INTERMEDIARIO, 
            CategoriaPartida.AVANCADO,
            CategoriaPartida.PROFISSIONAL
        ])
    
    return categorias


def get_nivel_minimo_categoria(categoria: CategoriaPartida) -> TipoUsuario:
    """
    Retorna o nível mínimo necessário para uma categoria
    """
    nivel_minimo = {
        CategoriaPartida.LIVRE: TipoUsuario.INICIANTE,
        CategoriaPartida.INICIANTE: TipoUsuario.INICIANTE,
        CategoriaPartida.INTERMEDIARIO: TipoUsuario.INTERMEDIARIO,
        CategoriaPartida.AVANCADO: TipoUsuario.AVANCADO,
        CategoriaPartida.PROFISSIONAL: TipoUsuario.PROFISSIONAL
    }
    
    return nivel_minimo.get(categoria, TipoUsuario.INICIANTE)


def get_descricao_categoria(categoria: CategoriaPartida) -> str:
    """
    Retorna uma descrição amigável da categoria
    """
    descricoes = {
        CategoriaPartida.LIVRE: "Aberto para todos os níveis",
        CategoriaPartida.INICIANTE: "Apenas para iniciantes",
        CategoriaPartida.INTERMEDIARIO: "Para intermediários e níveis acima",
        CategoriaPartida.AVANCADO: "Para jogadores avançados e profissionais",
        CategoriaPartida.PROFISSIONAL: "Apenas para jogadores profissionais"
    }
    
    return descricoes.get(categoria, "Categoria não definida")