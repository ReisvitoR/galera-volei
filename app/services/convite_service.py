from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from app.repositories.convite_repository import ConviteRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.partida_repository import PartidaRepository
from app.schemas.schemas import ConviteCreate, ConviteUpdate, ConviteResponse
from app.models.models import Convite
from app.models.enums import StatusConvite, CategoriaPartida
from app.utils.categoria_utils import usuario_pode_participar, get_descricao_categoria


class ConviteService:
    def __init__(self, db: Session):
        print(f"DEBUG: Inicializando ConviteService")
        self.db = db
        try:
            self.convite_repo = ConviteRepository(db)
            print(f"DEBUG: ConviteRepository criado")
            self.usuario_repo = UsuarioRepository(db)
            print(f"DEBUG: UsuarioRepository criado")
            self.partida_repo = PartidaRepository(db)
            print(f"DEBUG: PartidaRepository criado")
        except Exception as e:
            print(f"DEBUG: Erro na inicialização: {e}")
            raise
    
    def enviar_convite(self, convite_data: ConviteCreate, mandante_id: int) -> ConviteResponse:
        """Enviar um convite para um usuário participar de uma partida privada"""
        
        print(f"DEBUG: Início do envio de convite")
        print(f"DEBUG: convite_data: {convite_data}")
        print(f"DEBUG: mandante_id: {mandante_id}")
        
        # Verificar se a partida existe e é privada
        partida = self.partida_repo.get(convite_data.partida_id)
        print(f"DEBUG: Partida encontrada: {partida}")
        if not partida:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partida não encontrada"
            )
        
        if partida.publica:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível enviar convites para partidas públicas"
            )
        
        # Verificar se o mandante tem permissão (deve ser o organizador)
        if partida.organizador_id != mandante_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o organizador da partida pode enviar convites"
            )
        
        # Verificar se o usuário convidado existe
        convidado = self.usuario_repo.get(convite_data.convidado_id)
        if not convidado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário convidado não encontrado"
            )
        
        # Verificar se não está tentando convidar a si mesmo
        if mandante_id == convite_data.convidado_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Você não pode convidar a si mesmo"
            )
        
        # Verificar se usuário pode participar da categoria da partida
        categoria_enum = CategoriaPartida(partida.categoria) if isinstance(partida.categoria, str) else partida.categoria
        if not usuario_pode_participar(convidado.tipo, categoria_enum):
            categoria_desc = get_descricao_categoria(categoria_enum)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Usuário {convidado.nome} não pode participar desta partida. Categoria: {categoria_desc}. Nível do usuário: {convidado.tipo.value}"
            )
        
        # Verificar se já existe um convite ativo
        if self.convite_repo.convite_existe(mandante_id, convite_data.convidado_id, convite_data.partida_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um convite ativo para este usuário nesta partida"
            )
        
        # Verificar se o convidado já está participando da partida
        if convidado in partida.participantes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O usuário já está participando desta partida"
            )
        
        # Verificar se a partida não está lotada
        if len(partida.participantes) >= partida.max_participantes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A partida já atingiu o número máximo de participantes"
            )
        
        # Criar o convite
        convite_data_dict = {
            "mensagem": convite_data.mensagem,
            "data_expiracao": convite_data.data_expiracao or (datetime.now() + timedelta(days=7)),
            "mandante_id": mandante_id,
            "convidado_id": convite_data.convidado_id,
            "partida_id": convite_data.partida_id,
            "status": StatusConvite.PENDENTE
        }
        
        print(f"DEBUG: Criando convite com dados: {convite_data_dict}")
        print(f"DEBUG: Tipo dos dados: {type(convite_data_dict)}")
        
        try:
            convite_criado = self.convite_repo.create(convite_data_dict)
            print(f"DEBUG: Convite criado: {convite_criado}")
            
            # Retornar objeto simples primeiro
            return {
                "id": convite_criado.id,
                "mensagem": convite_criado.mensagem,
                "status": convite_criado.status.value if convite_criado.status else None,
                "mandante_id": convite_criado.mandante_id,
                "convidado_id": convite_criado.convidado_id,
                "partida_id": convite_criado.partida_id,
                "created_at": convite_criado.created_at.isoformat() if convite_criado.created_at else None,
                "updated_at": convite_criado.updated_at.isoformat() if convite_criado.updated_at else None
            }
        except Exception as e:
            print(f"DEBUG: Erro ao criar convite: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def aceitar_convite(self, convite_id: int, usuario_id: int) -> ConviteResponse:
        """Aceitar um convite e adicionar o usuário à partida"""
        
        # Aceitar o convite
        convite = self.convite_repo.aceitar_convite(convite_id, usuario_id)
        if not convite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Convite não encontrado ou não pode ser aceito"
            )
        
        # Adicionar o usuário à partida
        partida = self.partida_repo.get(convite.partida_id)
        usuario = self.usuario_repo.get(usuario_id)
        
        if partida and usuario:
            # Verificar se não está lotada
            if len(partida.participantes) >= partida.max_participantes:
                # Reverter o status do convite
                convite.status = StatusConvite.PENDENTE
                self.db.commit()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A partida já atingiu o número máximo de participantes"
                )
            
            # Adicionar à partida se ainda não estiver
            if usuario not in partida.participantes:
                partida.participantes.append(usuario)
                self.db.commit()
        
        return convite
    
    def recusar_convite(self, convite_id: int, usuario_id: int) -> ConviteResponse:
        """Recusar um convite"""
        convite = self.convite_repo.recusar_convite(convite_id, usuario_id)
        if not convite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Convite não encontrado ou não pode ser recusado"
            )
        return convite
    
    def get_convites_enviados(self, usuario_id: int, skip: int = 0, limit: int = 100) -> List[ConviteResponse]:
        """Buscar convites enviados por um usuário"""
        return self.convite_repo.get_convites_enviados(usuario_id, skip, limit)
    
    def get_convites_recebidos(self, usuario_id: int, skip: int = 0, limit: int = 100) -> List[ConviteResponse]:
        """Buscar convites recebidos por um usuário"""
        return self.convite_repo.get_convites_recebidos(usuario_id, skip, limit)
    
    def get_convites_pendentes(self, usuario_id: int) -> List[ConviteResponse]:
        """Buscar convites pendentes de um usuário"""
        return self.convite_repo.get_convites_pendentes(usuario_id)
    
    def get_convites_da_partida(self, partida_id: int, usuario_id: int) -> List[ConviteResponse]:
        """Buscar convites de uma partida (apenas o organizador pode ver)"""
        
        # Verificar se o usuário é o organizador da partida
        partida = self.partida_repo.get(partida_id)
        if not partida:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partida não encontrada"
            )
        
        if partida.organizador_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o organizador pode ver os convites da partida"
            )
        
        return self.convite_repo.get_convites_da_partida(partida_id)
    
    def cancelar_convite(self, convite_id: int, usuario_id: int) -> bool:
        """Cancelar um convite (apenas o mandante pode cancelar)"""
        convite = self.convite_repo.get(convite_id)
        if not convite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Convite não encontrado"
            )
        
        if convite.mandante_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas quem enviou o convite pode cancelá-lo"
            )
        
        if convite.status != StatusConvite.PENDENTE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas convites pendentes podem ser cancelados"
            )
        
        return self.convite_repo.delete(convite_id)
    
    def get_convite_by_id(self, convite_id: int, usuario_id: int) -> Optional[ConviteResponse]:
        """Buscar um convite específico por ID"""
        convite = self.convite_repo.get(convite_id)
        if not convite:
            return None
        
        # Verificar se o usuário tem permissão para ver este convite
        if convite.mandante_id != usuario_id and convite.convidado_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para ver este convite"
            )
        
        return ConviteResponse.model_validate(convite)
    
    def expirar_convites_antigos(self) -> int:
        """Expirar convites antigos (para ser executado periodicamente)"""
        return self.convite_repo.expirar_convites_antigos()