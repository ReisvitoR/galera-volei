from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import pytz  # type: ignore
from app.models import Partida, Usuario
from app.models.enums import StatusPartida, TipoPartida, TipoUsuario, CategoriaPartida
from app.repositories import PartidaRepository
from app.schemas import PartidaCreate, PartidaUpdate, StatusResponse
from app.utils.categoria_utils import usuario_pode_participar, get_descricao_categoria
from app.utils.partida_status import (
    atualizar_status_partida, 
    verificar_confirmacoes,
    confirmar_presenca,
    cancelar_confirmacao
)


def get_horario_brasil() -> datetime:
    """Retorna o horário atual no timezone do Brasil (America/Sao_Paulo)"""
    tz_brasil = pytz.timezone('America/Sao_Paulo')
    return datetime.now(tz_brasil)


class PartidaService:
    """
    Service para lógica de negócio das partidas
    Implementa Single Responsibility Principle (SRP) do SOLID
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = PartidaRepository(db)
    
    def create_partida(self, partida_data: PartidaCreate, organizador: Usuario) -> Partida:
        """Criar nova partida"""
        # Validar se organizador pode criar partida do tipo especificado
        self._validate_organizador_permissions(organizador, partida_data.tipo)
        
        # Validar data da partida usando horário do Brasil
        # Permite criar partida no mesmo dia, desde que seja pelo menos 1 minuto no futuro
        agora_brasil = get_horario_brasil()
        minimo_permitido = agora_brasil + timedelta(minutes=1)
        
        # Tornar data_partida aware se não for
        data_partida = partida_data.data_partida
        if data_partida.tzinfo is None:
            # Se não tem timezone, assume que é horário do Brasil
            tz_brasil = pytz.timezone('America/Sao_Paulo')
            data_partida = tz_brasil.localize(data_partida)
        
        if data_partida < minimo_permitido:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Data da partida deve ser pelo menos 1 minuto no futuro. Horário atual (Brasil): {agora_brasil.strftime('%d/%m/%Y %H:%M')}"
            )
        
        # Criar partida
        partida_dict = partida_data.dict()
        partida_dict['organizador_id'] = organizador.id
        
        return self.repository.create(partida_dict)
    
    def update_partida(self, partida_id: int, partida_data: PartidaUpdate, current_user: Usuario) -> Partida:
        """Atualizar partida"""
        partida = self.get_partida(partida_id)
        
        # Verificar se usuário pode alterar a partida
        if partida.organizador_id != current_user.id and current_user.tipo != TipoUsuario.PROFISSIONAL:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para alterar esta partida"
            )
        
        # Validar mudança de tipo se especificada
        if partida_data.tipo:
            self._validate_organizador_permissions(current_user, partida_data.tipo)
        
        # Validar nova data se especificada (horário do Brasil, pelo menos 1 minuto no futuro)
        if partida_data.data_partida:
            agora_brasil = get_horario_brasil()
            minimo_permitido = agora_brasil + timedelta(minutes=1)
            
            # Tornar data_partida aware se não for
            data_partida = partida_data.data_partida
            if data_partida.tzinfo is None:
                tz_brasil = pytz.timezone('America/Sao_Paulo')
                data_partida = tz_brasil.localize(data_partida)
            
            if data_partida < minimo_permitido:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Data da partida deve ser pelo menos 1 minuto no futuro. Horário atual (Brasil): {agora_brasil.strftime('%d/%m/%Y %H:%M')}"
                )
        
        # Atualizar apenas campos não nulos
        update_data = {k: v for k, v in partida_data.dict().items() if v is not None}
        
        return self.repository.update(partida, update_data)
    
    def get_partida(self, partida_id: int) -> Partida:
        """Buscar partida por ID e atualizar seu status automaticamente"""
        partida = self.repository.get_with_details(partida_id)
        if not partida:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partida não encontrada"
            )
        
        # Atualizar status automaticamente baseado no horário e confirmações
        atualizar_status_partida(partida, self.db)
        
        # Adicionar informações de confirmação
        confirmacoes = verificar_confirmacoes(partida, self.db)
        partida.participantes_confirmados = confirmacoes['participantes_confirmados']
        partida.todos_confirmaram = confirmacoes['todos_confirmaram']
        
        return partida
    
    def get_partidas_ativas(self, skip: int = 0, limit: int = 100, categoria: Optional[str] = None, usuario: Optional[Usuario] = None) -> List[Partida]:
        """Listar TODAS as partidas (independente do status) com filtros opcionais"""
        if categoria:
            partidas = self.repository.get_by_categoria_todas(categoria, skip=skip, limit=limit)
        else:
            partidas = self.repository.get_todas(skip=skip, limit=limit)
        
        # Filtrar partidas acessíveis ao usuário se solicitado
        if usuario:
            partidas_acessiveis = []
            for partida in partidas:
                # Verificar se a partida tem categoria definida
                if hasattr(partida, 'categoria') and partida.categoria:
                    try:
                        categoria_enum = CategoriaPartida(partida.categoria) if isinstance(partida.categoria, str) else partida.categoria
                        if usuario_pode_participar(usuario.tipo, categoria_enum):
                            partidas_acessiveis.append(partida)
                    except ValueError:
                        # Se não conseguir converter, assume LIVRE para retrocompatibilidade
                        if usuario_pode_participar(usuario.tipo, CategoriaPartida.LIVRE):
                            partidas_acessiveis.append(partida)
                else:
                    # Se não tem categoria, assume LIVRE (para retrocompatibilidade)
                    if usuario_pode_participar(usuario.tipo, CategoriaPartida.LIVRE):
                        partidas_acessiveis.append(partida)
            return partidas_acessiveis
        
        return partidas
    
    def get_partidas_by_tipo(self, tipo: TipoPartida, skip: int = 0, limit: int = 100) -> List[Partida]:
        """Listar partidas por tipo"""
        return self.repository.get_by_tipo(tipo, skip=skip, limit=limit)
    
    def get_proximas_partidas(self, skip: int = 0, limit: int = 100) -> List[Partida]:
        """Listar próximas partidas"""
        return self.repository.get_proximas(datetime.now(), skip=skip, limit=limit)
    
    def get_minhas_partidas(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Partida]:
        """Listar partidas organizadas pelo usuário"""
        return self.repository.get_by_organizador(user_id, skip=skip, limit=limit)
    
    def get_partidas_participando(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Partida]:
        """Listar partidas onde usuário está participando"""
        return self.repository.get_participando(user_id, skip=skip, limit=limit)
    
    def ativar_partida(self, partida_id: int, current_user: Usuario) -> Partida:
        """Ativar partida"""
        partida = self.get_partida(partida_id)
        
        if partida.organizador_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o organizador pode ativar a partida"
            )
        
        return self.repository.update(partida, {"status": StatusPartida.ATIVA})
    
    def desativar_partida(self, partida_id: int, current_user: Usuario) -> Partida:
        """Desativar partida"""
        partida = self.get_partida(partida_id)
        
        if partida.organizador_id != current_user.id and current_user.tipo != TipoUsuario.PROFISSIONAL:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para desativar esta partida"
            )
        
        return self.repository.update(partida, {"status": StatusPartida.INATIVA})
    
    def participar_partida(self, partida_id: int, usuario: Usuario) -> Partida:
        """Usuário se inscreve para participar de uma partida pública"""
        partida = self.get_partida(partida_id)
        
        # Verificar se a partida está finalizada ou cancelada
        if partida.status in [StatusPartida.FINALIZADA, StatusPartida.CANCELADA]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é possível entrar em uma partida {partida.status.value}"
            )
        
        # Verificar se a partida já começou ou está em andamento
        if partida.status == StatusPartida.EM_ANDAMENTO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível entrar em uma partida que já está em andamento"
            )
        
        # Verificar se a partida é pública
        if not partida.publica:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta partida é privada. Participação apenas por convite."
            )
        
        # Verificar se usuário pode participar da categoria
        categoria_enum = CategoriaPartida(partida.categoria) if isinstance(partida.categoria, str) else partida.categoria
        if not usuario_pode_participar(usuario.tipo, categoria_enum):
            categoria_desc = get_descricao_categoria(categoria_enum)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Seu nível não permite participar desta partida. Categoria: {categoria_desc}. Seu nível: {usuario.tipo.value}"
            )
        
        # Verificar se não está lotada
        if len(partida.participantes) >= partida.max_participantes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Partida já atingiu o número máximo de participantes"
            )
        
        # Verificar se usuário já está participando
        if usuario in partida.participantes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Você já está participando desta partida"
            )
        
        # Adicionar usuário à partida (sem convidado_por_id - entrada direta)
        # CONFIRMA AUTOMATICAMENTE ao entrar
        from app.models.models import partida_participantes
        from sqlalchemy import insert
        from app.utils.partida_status import get_horario_brasil
        
        agora = get_horario_brasil()
        
        stmt = insert(partida_participantes).values(
            partida_id=partida.id,
            usuario_id=usuario.id,
            convidado_por_id=None,  # Entrada direta, sem convite
            confirmado=True,  # JÁ CONFIRMADO AUTOMATICAMENTE
            data_confirmacao=agora  # Data da confirmação
        )
        self.db.execute(stmt)
        self.db.commit()
        self.db.refresh(partida)
        
        # Atualizar status da partida (pode mudar para MARCADA se todos confirmaram)
        from app.utils.partida_status import atualizar_status_partida
        atualizar_status_partida(partida, self.db)
        
        return partida
    
    def sair_partida(self, partida_id: int, usuario: Usuario) -> Partida:
        """Usuário sai de uma partida"""
        partida = self.get_partida(partida_id)
        
        # Verificar se a partida está finalizada ou cancelada
        if partida.status in [StatusPartida.FINALIZADA, StatusPartida.CANCELADA]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é possível sair de uma partida {partida.status.value}"
            )
        
        # Verificar se usuário está participando
        if usuario not in partida.participantes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Você não está participando desta partida"
            )
        
        # Remover usuário da partida
        partida.participantes.remove(usuario)
        self.db.commit()
        self.db.refresh(partida)
        
        return partida
    
    def remover_participante(self, partida_id: int, usuario_id: int, current_user: Usuario) -> Partida:
        """Organizador remove um participante da partida"""
        partida = self.get_partida(partida_id)
        
        # Verificar se quem está removendo é o organizador
        if partida.organizador_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o organizador pode remover participantes"
            )
        
        # Verificar se não está tentando remover a si mesmo
        if usuario_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Você não pode remover a si mesmo. Use o endpoint de sair da partida."
            )
        
        # Buscar o usuário a ser removido
        from app.repositories import UsuarioRepository
        usuario_repo = UsuarioRepository(self.db)
        usuario = usuario_repo.get(usuario_id)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Verificar se usuário está participando
        if usuario not in partida.participantes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este usuário não está participando desta partida"
            )
        
        # Remover usuário da partida
        partida.participantes.remove(usuario)
        self.db.commit()
        self.db.refresh(partida)
        
        return partida
    
    def finalizar_partida(self, partida_id: int, pontos_a: int, pontos_b: int, current_user: Usuario) -> Partida:
        """Finalizar partida com pontuação"""
        partida = self.get_partida(partida_id)
        
        if partida.organizador_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas o organizador pode finalizar a partida"
            )
        
        # Atualizar pontuação e status
        success = self.repository.atualizar_pontuacao(partida_id, pontos_a, pontos_b)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao atualizar pontuação"
            )
        
        # Atualizar estatísticas dos participantes
        self._update_participant_stats(partida, pontos_a, pontos_b)
        
        return self.get_partida(partida_id)
    
    def _validate_organizador_permissions(self, organizador: Usuario, tipo_partida: TipoPartida):
        """Validar se organizador pode criar partida do tipo especificado"""
        if tipo_partida == TipoPartida.COMPETITIVA and organizador.tipo not in [TipoUsuario.INTERMEDIARIO, TipoUsuario.AVANCADO, TipoUsuario.PROFISSIONAL]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas usuários intermediários, avançados ou profissionais podem organizar partidas competitivas"
            )
    
    def _update_participant_stats(self, partida: Partida, pontos_a: int, pontos_b: int):
        """Atualizar estatísticas dos participantes após finalizar partida"""
        from app.repositories import UsuarioRepository
        
        user_repo = UsuarioRepository(self.db)
        
        # Determinar equipe vencedora
        vencedor_equipe_a = pontos_a > pontos_b
        
        # Atualizar stats dos participantes (assumindo divisão meio a meio)
        total_participantes = len(partida.participantes)
        meio = total_participantes // 2
        
        for i, participante in enumerate(partida.participantes):
            eh_equipe_a = i < meio
            venceu = (eh_equipe_a and vencedor_equipe_a) or (not eh_equipe_a and not vencedor_equipe_a)
            
            pontos_ganhos = 10 if venceu else 5  # Pontos base
            if partida.tipo == TipoPartida.COMPETITIVA:
                pontos_ganhos *= 2  # Dobra pontos em partidas competitivas
            
            user_repo.update_stats(
                participante.id,
                partidas_jogadas=1,
                vitorias=1 if venceu else 0,
                pontos=pontos_ganhos
            )
    
    def confirmar_presenca_usuario(self, partida_id: int, usuario: Usuario) -> StatusResponse:
        """Confirmar presença do usuário na partida"""
        partida = self.get_partida(partida_id)
        
        # Verificar se usuário está participando (comparar IDs)
        participante_ids = [p.id for p in partida.participantes]
        if usuario.id not in participante_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Você não está participando desta partida"
            )
        
        # Verificar se partida ainda não começou
        agora = get_horario_brasil()
        if partida.data_partida <= agora:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível confirmar presença após o início da partida"
            )
        
        # Confirmar presença
        if confirmar_presenca(partida_id, usuario.id, self.db):
            # Atualizar status da partida (pode mudar para MARCADA)
            atualizar_status_partida(partida, self.db)
            
            return StatusResponse(
                success=True,
                message="Presença confirmada com sucesso",
                data=verificar_confirmacoes(partida, self.db)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao confirmar presença"
            )
    
    def cancelar_confirmacao_usuario(self, partida_id: int, usuario: Usuario) -> StatusResponse:
        """Cancelar confirmação de presença do usuário"""
        partida = self.get_partida(partida_id)
        
        # Verificar se usuário está participando (comparar IDs)
        participante_ids = [p.id for p in partida.participantes]
        if usuario.id not in participante_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Você não está participando desta partida"
            )
        
        # Verificar se partida ainda não começou
        agora = get_horario_brasil()
        if partida.data_partida <= agora:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível cancelar confirmação após o início da partida"
            )
        
        # Cancelar confirmação
        if cancelar_confirmacao(partida_id, usuario.id, self.db):
            # Atualizar status da partida (pode voltar para ATIVA)
            atualizar_status_partida(partida, self.db)
            
            return StatusResponse(
                success=True,
                message="Confirmação cancelada com sucesso",
                data=verificar_confirmacoes(partida, self.db)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao cancelar confirmação"
            )