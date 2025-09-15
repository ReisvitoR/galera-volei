from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from datetime import datetime

app = FastAPI()

# Configurar arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    """Redireciona para a página inicial"""
    return RedirectResponse(url="/static/index.html")

# Enums
class TipoPartida(str, Enum):
    iniciante = "iniciante"
    normal = "normal"
    ranked = "ranked"

class TipoUsuario(str, Enum):
    noob = "noob"
    amador = "amador"
    intermediario = "intermediario"
    proplayer = "proplayer"

# Modelos
class StatusPartidaRequest(BaseModel):
    ativa: bool

class StatusPartidaResponse(BaseModel):
    partida_id: int
    ativa: bool

class CandidaturaRequest(BaseModel):
    usuario_id: int

class CandidaturaResponse(BaseModel):
    partida_id: int
    usuario_id: int
    status: str

class DecisaoCandidaturaRequest(BaseModel):
    usuario_id: int
    aceitar: bool

class DecisaoCandidaturaResponse(BaseModel):
    partida_id: int
    usuario_id: int
    status: str

class AvaliacaoRequest(BaseModel):
    nota: int
    comentario: Optional[str] = None

class AvaliacaoResponse(BaseModel):
    id: int
    nota: int
    comentario: Optional[str] = None

class AtletaRequest(BaseModel):
    nome: str
    tipo: TipoUsuario

class AtletaResponse(BaseModel):
    id: int
    nome: str
    tipo: TipoUsuario
    ranking: int

class EquipeCreateRequest(BaseModel):
    nome: str
    atletas: List[int]

class EquipeResponse(BaseModel):
    id: int
    nome: str
    atletas: List[AtletaResponse]
    ranking: int

class PartidaCreateRequest(BaseModel):
    data: datetime
    local: str
    equipes: List[str]
    tipo_partida: TipoPartida

class PartidaResponse(BaseModel):
    id: int
    data: datetime
    local: str
    equipes: List[str]
    status: str
    tipo_partida: TipoPartida
    nivel_minimo: TipoUsuario
    equipe_vencedora: Optional[str] = None
    equipe_perdedora: Optional[str] = None

class UsuarioRequest(BaseModel):
    nome: str
    tipo: TipoUsuario

class SolicitarEntradaRequest(BaseModel):
    usuario: UsuarioRequest

class SolicitarEntradaResponse(BaseModel):
    partida_id: int
    usuario: UsuarioRequest
    permitido: bool
    motivo: str

class MarcarPontoRequest(BaseModel):
    partida_id: int
    equipe: str

class MarcarPontoResponse(BaseModel):
    partida_id: int
    equipe: str
    pontos: int

# Endpoints principais
@app.post("/partidas", response_model=PartidaResponse)
def criar_partida(request: PartidaCreateRequest):
    """
    Cria uma nova partida de vôlei.
    """
    pass

@app.post("/partidas/{partida_id}/status", response_model=StatusPartidaResponse)
def alterar_status_partida(partida_id: int, request: StatusPartidaRequest):
    """
    Ativa ou desativa uma partida.
    """
    pass

@app.post("/partidas/{partida_id}/candidatar", response_model=CandidaturaResponse)
def candidatar_partida(partida_id: int, request: CandidaturaRequest):
    """
    Usuário se candidata para participar de uma partida.
    """
    pass

@app.post("/partidas/{partida_id}/decisao-candidatura", response_model=DecisaoCandidaturaResponse)
def decisao_candidatura(partida_id: int, request: DecisaoCandidaturaRequest):
    """
    Organizador aceita ou rejeita candidatura de um usuário.
    """
    pass

@app.post("/partidas/{partida_id}/avaliar", response_model=AvaliacaoResponse)
def avaliar_partida(partida_id: int, request: AvaliacaoRequest):
    """
    Avaliar uma partida.
    """
    pass

@app.post("/organizadores/{organizador_id}/avaliar", response_model=AvaliacaoResponse)
def avaliar_organizador(organizador_id: int, request: AvaliacaoRequest):
    """
    Avaliar um organizador.
    """
    pass

@app.post("/atletas/{atleta_id}/avaliar", response_model=AvaliacaoResponse)
def avaliar_jogador(atleta_id: int, request: AvaliacaoRequest):
    """
    Avaliar um jogador.
    """
    pass

@app.post("/atletas", response_model=AtletaResponse)
def criar_atleta(request: AtletaRequest):
    """
    Cria um novo atleta (jogador).
    """
    pass

@app.post("/equipes", response_model=EquipeResponse)
def criar_equipe(request: EquipeCreateRequest):
    """
    Cria uma nova equipe e associa atletas.
    """
    pass

@app.get("/atletas/ranking/{tipo}", response_model=List[AtletaResponse])
def ranking_atletas(tipo: TipoUsuario):
    """
    Lista o ranking dos atletas de acordo com sua classificação.
    """
    pass

@app.post("/partidas/{partida_id}/solicitar-entrada", response_model=SolicitarEntradaResponse)
def solicitar_entrada(partida_id: int, request: SolicitarEntradaRequest):
    """
    Usuário solicita para entrar em uma partida.
    """
    pass

@app.post("/partidas/{partida_id}/ponto", response_model=MarcarPontoResponse)
def marcar_ponto(partida_id: int, request: MarcarPontoRequest):
    """
    Marca um ponto para uma equipe em uma partida.
    """
    pass

# Listagens
@app.get("/atletas", response_model=List[AtletaResponse])
def listar_jogadores():
    """
    Lista todos os jogadores cadastrados.
    """
    pass

@app.get("/atletas/melhores", response_model=List[AtletaResponse])
def listar_melhores_jogadores(limit: int = Query(10, description="Quantidade de jogadores a retornar")):
    """
    Lista os melhores jogadores ranqueados.
    """
    pass

@app.get("/partidas/melhores", response_model=List[PartidaResponse])
def listar_melhores_partidas(limit: int = Query(10, description="Quantidade de partidas a retornar")):
    """
    Lista as melhores partidas avaliadas.
    """
    pass

@app.get("/organizadores", response_model=List[AtletaResponse])
def listar_organizadores():
    """
    Lista todos os organizadores (jogadores que criaram partidas).
    """
    pass

@app.get("/organizadores/{organizador_id}/partidas", response_model=List[PartidaResponse])
def listar_partidas_criadas(organizador_id: int):
    """
    Lista todas as partidas criadas por um organizador.
    """
    pass
