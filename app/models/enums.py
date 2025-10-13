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


class StatusPartida(PyEnum):
    ATIVA = "ativa"
    INATIVA = "inativa"
    FINALIZADA = "finalizada"


class StatusCandidatura(PyEnum):
    PENDENTE = "pendente"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"