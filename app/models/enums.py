from enum import Enum as PyEnum


class TipoUsuario(PyEnum):
    NOOB = "noob"
    AMADOR = "amador"
    INTERMEDIARIO = "intermediario"
    PROPLAYER = "proplayer"


class TipoPartida(PyEnum):
    INICIANTE = "iniciante"
    NORMAL = "normal"
    RANKED = "ranked"


class CategoriaPartida(PyEnum):
    """Categoria que define o nível mínimo dos jogadores"""
    NOOB = "noob"          # Apenas para jogadores noob
    AMADOR = "amador"      # Para amadores e acima
    INTERMEDIARIO = "intermediario"  # Para intermediários e avançados
    AVANCADO = "avancado"  # Apenas para jogadores avançados
    LIVRE = "livre"        # Qualquer nível pode participar


class StatusPartida(PyEnum):
    ATIVA = "ativa"
    INATIVA = "inativa"
    FINALIZADA = "finalizada"


class StatusCandidatura(PyEnum):
    PENDENTE = "pendente"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"


class StatusConvite(PyEnum):
    PENDENTE = "pendente"
    ACEITO = "aceito"
    RECUSADO = "recusado"
    EXPIRADO = "expirado"