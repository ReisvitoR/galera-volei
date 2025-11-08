"""
Testes unitários para o sistema de convites
Testa a lógica de negócios das classes Service e Repository
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from fastapi import HTTPException

# Adicionar o diretório raiz ao path para importações
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.convite_service import ConviteService
from app.repositories.convite_repository import ConviteRepository
from app.models.models import Convite, Usuario, Partida
from app.models.enums import StatusConvite
from app.schemas.schemas import ConviteCreate, ConviteUpdate


class TestConviteRepository:
    """Testes para ConviteRepository"""
    
    def setup_method(self):
        """Setup executado antes de cada teste"""
        self.mock_db = Mock(spec=Session)
        self.repo = ConviteRepository(self.mock_db)
    
    def test_init_repository(self):
        """Teste de inicialização do repository"""
        assert self.repo.db == self.mock_db
        assert self.repo.model_class == Convite
    
    def test_get_convites_enviados(self):
        """Teste buscar convites enviados por um usuário"""
        usuario_id = 1
        mock_convites = [Mock(), Mock()]
        
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_convites
        
        resultado = self.repo.get_convites_enviados(usuario_id, skip=0, limit=10)
        
        assert resultado == mock_convites
        self.mock_db.query.assert_called_once_with(Convite)
    
    def test_get_convites_recebidos(self):
        """Teste buscar convites recebidos por um usuário"""
        usuario_id = 2
        mock_convites = [Mock(), Mock()]
        
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_convites
        
        resultado = self.repo.get_convites_recebidos(usuario_id, skip=0, limit=10)
        
        assert resultado == mock_convites
        self.mock_db.query.assert_called_once_with(Convite)
    
    def test_aceitar_convite_sucesso(self):
        """Teste aceitar convite com sucesso"""
        convite_id = 1
        usuario_id = 2
        
        mock_convite = Mock()
        mock_convite.convidado_id = usuario_id
        mock_convite.status = StatusConvite.PENDENTE
        mock_convite.data_expiracao = datetime.now() + timedelta(days=1)
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_convite
        
        resultado = self.repo.aceitar_convite(convite_id, usuario_id)
        
        assert resultado == mock_convite
        assert mock_convite.status == StatusConvite.ACEITO
        self.mock_db.commit.assert_called_once()
    
    def test_aceitar_convite_nao_encontrado(self):
        """Teste aceitar convite que não existe"""
        convite_id = 999
        usuario_id = 2
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        resultado = self.repo.aceitar_convite(convite_id, usuario_id)
        
        assert resultado is None
    
    def test_recusar_convite_sucesso(self):
        """Teste recusar convite com sucesso"""
        convite_id = 1
        usuario_id = 2
        
        mock_convite = Mock()
        mock_convite.convidado_id = usuario_id
        mock_convite.status = StatusConvite.PENDENTE
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_convite
        
        resultado = self.repo.recusar_convite(convite_id, usuario_id)
        
        assert resultado == mock_convite
        assert mock_convite.status == StatusConvite.RECUSADO
        self.mock_db.commit.assert_called_once()
    
    def test_convite_existe_true(self):
        """Teste verificar se convite existe (retorna True)"""
        mock_convite = Mock()
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_convite
        
        resultado = self.repo.convite_existe(1, 2, 3)
        
        assert resultado is True
    
    def test_convite_existe_false(self):
        """Teste verificar se convite existe (retorna False)"""
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        resultado = self.repo.convite_existe(1, 2, 3)
        
        assert resultado is False


class TestConviteService:
    """Testes para ConviteService"""
    
    def setup_method(self):
        """Setup executado antes de cada teste"""
        self.mock_db = Mock(spec=Session)
        self.mock_convite_repo = Mock(spec=ConviteRepository)
        self.mock_usuario_repo = Mock()
        self.mock_partida_repo = Mock()
        
        # Criar service com mocks
        self.service = ConviteService(self.mock_db)
        self.service.convite_repo = self.mock_convite_repo
        self.service.usuario_repo = self.mock_usuario_repo
        self.service.partida_repo = self.mock_partida_repo
    
    def test_enviar_convite_sucesso(self):
        """Teste enviar convite com dados válidos"""
        # Setup
        mandante_id = 1
        convite_data = ConviteCreate(
            mensagem="Convite de teste",
            convidado_id=2,
            partida_id=3,
            data_expiracao=datetime.now() + timedelta(days=7)
        )
        
        # Mock partida privada
        mock_partida = Mock()
        mock_partida.publica = False
        mock_partida.organizador_id = mandante_id
        mock_partida.participantes = []
        mock_partida.max_participantes = 12
        
        # Mock convidado
        mock_convidado = Mock()
        
        # Configurar mocks
        self.mock_partida_repo.get.return_value = mock_partida
        self.mock_usuario_repo.get.return_value = mock_convidado
        self.mock_convite_repo.convite_existe.return_value = False
        self.mock_convite_repo.create.return_value = Mock()
        
        # Executar
        resultado = self.service.enviar_convite(convite_data, mandante_id)
        
        # Verificar
        assert resultado is not None
        self.mock_convite_repo.create.assert_called_once()
    
    def test_enviar_convite_partida_publica_falha(self):
        """Teste enviar convite para partida pública (deve falhar)"""
        mandante_id = 1
        convite_data = ConviteCreate(
            mensagem="Convite inválido",
            convidado_id=2,
            partida_id=3
        )
        
        # Mock partida pública
        mock_partida = Mock()
        mock_partida.publica = True
        
        self.mock_partida_repo.get.return_value = mock_partida
        
        # Deve gerar exceção
        with pytest.raises(HTTPException) as exc_info:
            self.service.enviar_convite(convite_data, mandante_id)
        
        assert exc_info.value.status_code == 400
        assert "partidas públicas" in str(exc_info.value.detail)
    
    def test_enviar_convite_partida_nao_encontrada(self):
        """Teste enviar convite para partida inexistente"""
        mandante_id = 1
        convite_data = ConviteCreate(
            mensagem="Convite para partida inexistente",
            convidado_id=2,
            partida_id=999
        )
        
        self.mock_partida_repo.get.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            self.service.enviar_convite(convite_data, mandante_id)
        
        assert exc_info.value.status_code == 404
        assert "Partida não encontrada" in str(exc_info.value.detail)
    
    def test_enviar_convite_sem_permissao(self):
        """Teste enviar convite sem ser organizador"""
        mandante_id = 1
        convite_data = ConviteCreate(
            mensagem="Convite sem permissão",
            convidado_id=2,
            partida_id=3
        )
        
        # Mock partida onde mandante não é organizador
        mock_partida = Mock()
        mock_partida.publica = False
        mock_partida.organizador_id = 999  # ID diferente do mandante
        
        self.mock_partida_repo.get.return_value = mock_partida
        
        with pytest.raises(HTTPException) as exc_info:
            self.service.enviar_convite(convite_data, mandante_id)
        
        assert exc_info.value.status_code == 403
        assert "organizador" in str(exc_info.value.detail)
    
    def test_enviar_convite_usuario_inexistente(self):
        """Teste enviar convite para usuário inexistente"""
        mandante_id = 1
        convite_data = ConviteCreate(
            mensagem="Convite para usuário inexistente",
            convidado_id=999,
            partida_id=3
        )
        
        # Mock partida válida
        mock_partida = Mock()
        mock_partida.publica = False
        mock_partida.organizador_id = mandante_id
        
        self.mock_partida_repo.get.return_value = mock_partida
        self.mock_usuario_repo.get.return_value = None  # Usuário não existe
        
        with pytest.raises(HTTPException) as exc_info:
            self.service.enviar_convite(convite_data, mandante_id)
        
        assert exc_info.value.status_code == 404
        assert "convidado não encontrado" in str(exc_info.value.detail)
    
    def test_enviar_convite_auto_convite(self):
        """Teste auto-convite (deve falhar)"""
        mandante_id = 1
        convite_data = ConviteCreate(
            mensagem="Auto-convite",
            convidado_id=1,  # Mesmo ID do mandante
            partida_id=3
        )
        
        # Mock partida válida
        mock_partida = Mock()
        mock_partida.publica = False
        mock_partida.organizador_id = mandante_id
        
        self.mock_partida_repo.get.return_value = mock_partida
        self.mock_usuario_repo.get.return_value = Mock()
        
        with pytest.raises(HTTPException) as exc_info:
            self.service.enviar_convite(convite_data, mandante_id)
        
        assert exc_info.value.status_code == 400
        assert "convidar a si mesmo" in str(exc_info.value.detail)
    
    def test_enviar_convite_duplicado(self):
        """Teste enviar convite duplicado"""
        mandante_id = 1
        convite_data = ConviteCreate(
            mensagem="Convite duplicado",
            convidado_id=2,
            partida_id=3
        )
        
        # Mock partida válida
        mock_partida = Mock()
        mock_partida.publica = False
        mock_partida.organizador_id = mandante_id
        mock_partida.participantes = []
        mock_partida.max_participantes = 12
        
        # Mock convidado
        mock_convidado = Mock()
        
        self.mock_partida_repo.get.return_value = mock_partida
        self.mock_usuario_repo.get.return_value = mock_convidado
        self.mock_convite_repo.convite_existe.return_value = True  # Convite já existe
        
        with pytest.raises(HTTPException) as exc_info:
            self.service.enviar_convite(convite_data, mandante_id)
        
        assert exc_info.value.status_code == 400
        assert "convite ativo" in str(exc_info.value.detail)
    
    def test_aceitar_convite_sucesso(self):
        """Teste aceitar convite com sucesso"""
        convite_id = 1
        usuario_id = 2
        
        # Mock convite aceito
        mock_convite = Mock()
        mock_convite.partida_id = 3
        
        # Mock partida e usuário
        mock_partida = Mock()
        mock_partida.participantes = []
        mock_partida.max_participantes = 12
        
        mock_usuario = Mock()
        
        self.mock_convite_repo.aceitar_convite.return_value = mock_convite
        self.mock_partida_repo.get.return_value = mock_partida
        self.mock_usuario_repo.get.return_value = mock_usuario
        
        resultado = self.service.aceitar_convite(convite_id, usuario_id)
        
        assert resultado == mock_convite
        assert mock_usuario in mock_partida.participantes
        self.mock_db.commit.assert_called_once()
    
    def test_aceitar_convite_nao_encontrado(self):
        """Teste aceitar convite inexistente"""
        convite_id = 999
        usuario_id = 2
        
        self.mock_convite_repo.aceitar_convite.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            self.service.aceitar_convite(convite_id, usuario_id)
        
        assert exc_info.value.status_code == 404
        assert "não encontrado" in str(exc_info.value.detail)
    
    def test_recusar_convite_sucesso(self):
        """Teste recusar convite com sucesso"""
        convite_id = 1
        usuario_id = 2
        
        mock_convite = Mock()
        self.mock_convite_repo.recusar_convite.return_value = mock_convite
        
        resultado = self.service.recusar_convite(convite_id, usuario_id)
        
        assert resultado == mock_convite
    
    def test_get_convites_enviados(self):
        """Teste buscar convites enviados"""
        usuario_id = 1
        mock_convites = [Mock(), Mock()]
        
        self.mock_convite_repo.get_convites_enviados.return_value = mock_convites
        
        resultado = self.service.get_convites_enviados(usuario_id)
        
        assert resultado == mock_convites
        self.mock_convite_repo.get_convites_enviados.assert_called_once_with(usuario_id, 0, 100)
    
    def test_get_convites_recebidos(self):
        """Teste buscar convites recebidos"""
        usuario_id = 2
        mock_convites = [Mock(), Mock()]
        
        self.mock_convite_repo.get_convites_recebidos.return_value = mock_convites
        
        resultado = self.service.get_convites_recebidos(usuario_id)
        
        assert resultado == mock_convites
        self.mock_convite_repo.get_convites_recebidos.assert_called_once_with(usuario_id, 0, 100)


def run_tests():
    """Executar todos os testes unitários"""
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes"
    ])


if __name__ == "__main__":
    run_tests()