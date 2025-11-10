from enum import Enum as PyEnum


class TipoUsuario(PyEnum):
    INICIANTE = "iniciante"
    INTERMEDIARIO = "intermediario"
    AVANCADO = "avancado"
    PROFISSIONAL = "profissional"


class TipoPartida(PyEnum):
    AMISTOSA = "amistosa"  # Partida casual, sem pontuação
    COMPETITIVA = "competitiva"  # Partida ranqueada, conta pontos


class CategoriaPartida(PyEnum):
    """Categoria que define o nível mínimo dos jogadores"""
    INICIANTE = "iniciante"          # Apenas para jogadores iniciantes
    INTERMEDIARIO = "intermediario"  # Para jogadores intermediários
    AVANCADO = "avancado"            # Para jogadores avançados  
    PROFISSIONAL = "profissional"    # Para jogadores profissionais
    LIVRE = "livre"                  # Qualquer nível pode participar


class StatusPartida(PyEnum):
    ATIVA = "ativa"              # Criada, aguardando participantes
    MARCADA = "marcada"          # Todos confirmaram presença
    EM_ANDAMENTO = "em_andamento"  # Partida acontecendo agora
    FINALIZADA = "finalizada"    # Partida terminada
    CANCELADA = "cancelada"      # Partida cancelada
    INATIVA = "inativa"          # Desativada pelo organizador


class StatusCandidatura(PyEnum):
    PENDENTE = "pendente"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"


class StatusConvite(PyEnum):
    PENDENTE = "pendente"
    ACEITO = "aceito"
    RECUSADO = "recusado"
    EXPIRADO = "expirado"