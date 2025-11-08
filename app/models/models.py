from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.enums import TipoUsuario, TipoPartida, StatusPartida, StatusCandidatura, StatusConvite, CategoriaPartida

# Tabela de associação many-to-many para participantes da partida
partida_participantes = Table(
    'partida_participantes',
    Base.metadata,
    Column('partida_id', Integer, ForeignKey('partidas.id'), primary_key=True),
    Column('usuario_id', Integer, ForeignKey('usuarios.id'), primary_key=True)
)

# Tabela de associação many-to-many para membros da equipe
equipe_membros = Table(
    'equipe_membros',
    Base.metadata,
    Column('equipe_id', Integer, ForeignKey('equipes.id'), primary_key=True),
    Column('usuario_id', Integer, ForeignKey('usuarios.id'), primary_key=True)
)


class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    tipo = Column(Enum(TipoUsuario), nullable=False, default=TipoUsuario.NOOB)
    ativo = Column(Boolean, default=True)
    pontuacao_total = Column(Integer, default=0)
    partidas_jogadas = Column(Integer, default=0)
    vitorias = Column(Integer, default=0)
    derrotas = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    partidas_organizadas = relationship("Partida", back_populates="organizador")
    partidas_participadas = relationship(
        "Partida", 
        secondary=partida_participantes, 
        back_populates="participantes"
    )
    candidaturas = relationship("Candidatura", back_populates="usuario")
    avaliacoes_feitas = relationship(
        "Avaliacao", 
        foreign_keys="Avaliacao.avaliador_id", 
        back_populates="avaliador"
    )
    avaliacoes_recebidas = relationship(
        "Avaliacao", 
        foreign_keys="Avaliacao.avaliado_id", 
        back_populates="avaliado"
    )
    equipes = relationship(
        "Equipe", 
        secondary=equipe_membros, 
        back_populates="membros"
    )
    equipes_lideradas = relationship("Equipe", back_populates="lider")
    # Relacionamentos de convites
    convites_enviados = relationship(
        "Convite", 
        foreign_keys="Convite.mandante_id", 
        back_populates="mandante"
    )
    convites_recebidos = relationship(
        "Convite", 
        foreign_keys="Convite.convidado_id", 
        back_populates="convidado"
    )


class Partida(Base):
    __tablename__ = "partidas"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text)
    tipo = Column(Enum(TipoPartida), nullable=False)
    categoria = Column(String(20), nullable=False, default="livre")
    status = Column(Enum(StatusPartida), default=StatusPartida.ATIVA)
    data_partida = Column(DateTime(timezone=True), nullable=False)
    local = Column(String(255))
    max_participantes = Column(Integer, default=12)
    publica = Column(Boolean, default=True)  # True = pública, False = privada
    pontuacao_equipe_a = Column(Integer, default=0)
    pontuacao_equipe_b = Column(Integer, default=0)
    
    organizador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    organizador = relationship("Usuario", back_populates="partidas_organizadas")
    participantes = relationship(
        "Usuario", 
        secondary=partida_participantes, 
        back_populates="partidas_participadas"
    )
    candidaturas = relationship("Candidatura", back_populates="partida")
    avaliacoes = relationship("Avaliacao", back_populates="partida")
    convites = relationship("Convite", back_populates="partida")


class Equipe(Base):
    __tablename__ = "equipes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    pontuacao_total = Column(Integer, default=0)
    partidas_jogadas = Column(Integer, default=0)
    vitorias = Column(Integer, default=0)
    derrotas = Column(Integer, default=0)
    
    lider_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    lider = relationship("Usuario", back_populates="equipes_lideradas")
    membros = relationship(
        "Usuario", 
        secondary=equipe_membros, 
        back_populates="equipes"
    )


class Candidatura(Base):
    __tablename__ = "candidaturas"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(StatusCandidatura), default=StatusCandidatura.PENDENTE)
    mensagem = Column(Text)
    
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    partida_id = Column(Integer, ForeignKey("partidas.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="candidaturas")
    partida = relationship("Partida", back_populates="candidaturas")


class Avaliacao(Base):
    __tablename__ = "avaliacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    nota = Column(Integer, nullable=False)  # 1-5
    comentario = Column(Text)
    tipo_avaliacao = Column(String(50), nullable=False)  # "partida", "organizador", "jogador"
    
    avaliador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    avaliado_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)  # null se for avaliação de partida
    partida_id = Column(Integer, ForeignKey("partidas.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    avaliador = relationship("Usuario", foreign_keys=[avaliador_id], back_populates="avaliacoes_feitas")
    avaliado = relationship("Usuario", foreign_keys=[avaliado_id], back_populates="avaliacoes_recebidas")
    partida = relationship("Partida", back_populates="avaliacoes")


class Convite(Base):
    __tablename__ = "convites"
    
    id = Column(Integer, primary_key=True, index=True)
    mensagem = Column(Text)  # Mensagem opcional do convite
    status = Column(Enum(StatusConvite), default=StatusConvite.PENDENTE)
    data_expiracao = Column(DateTime(timezone=True))  # Opcional, convite pode expirar
    
    # Quem envia o convite (mandante)
    mandante_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    # Quem recebe o convite 
    convidado_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    # Para qual partida é o convite
    partida_id = Column(Integer, ForeignKey("partidas.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    mandante = relationship("Usuario", foreign_keys=[mandante_id], back_populates="convites_enviados")
    convidado = relationship("Usuario", foreign_keys=[convidado_id], back_populates="convites_recebidos")
    partida = relationship("Partida", back_populates="convites")