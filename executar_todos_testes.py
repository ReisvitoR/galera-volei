"""
Script principal para executar toda a suíte de testes
Executa testes unitários, integração, validação e cenários negativos
"""

import subprocess
import sys
import os
import time
from datetime import datetime

class TestRunner:
    """Executor principal da suíte de testes"""
    
    def __init__(self):
        self.resultados = {
            'unitarios': {'executado': False, 'sucesso': False, 'detalhes': ''},
            'integracao': {'executado': False, 'sucesso': False, 'detalhes': ''},
            'validacao': {'executado': False, 'sucesso': False, 'detalhes': ''},
            'negativos': {'executado': False, 'sucesso': False, 'detalhes': ''}
        }
        self.inicio = datetime.now()
    
    def print_header(self, titulo):
        """Imprimir cabeçalho formatado"""
        print("\n" + "="*80)
        print(f"🧪 {titulo}")
        print("="*80)
    
    def print_separator(self):
        """Imprimir separador"""
        print("-" * 80)
    
    def executar_testes_unitarios(self):
        """Executar testes unitários com pytest"""
        self.print_header("EXECUTANDO TESTES UNITÁRIOS")
        
        try:
            # Verificar se pytest está disponível
            try:
                import pytest
                print("✅ pytest encontrado")
            except ImportError:
                print("❌ pytest não encontrado. Instalando...")
                subprocess.run([sys.executable, "-m", "pip", "install", "pytest"], check=True)
                print("✅ pytest instalado")
            
            # Executar testes unitários
            print("🔍 Executando testes unitários...")
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "test_unitarios.py", 
                "-v", "--tb=short", "--color=yes"
            ], capture_output=True, text=True, timeout=60)
            
            self.resultados['unitarios']['executado'] = True
            self.resultados['unitarios']['sucesso'] = result.returncode == 0
            self.resultados['unitarios']['detalhes'] = result.stdout + result.stderr
            
            if result.returncode == 0:
                print("✅ Testes unitários PASSARAM")
            else:
                print("❌ Testes unitários FALHARAM")
                print(f"Saída: {result.stdout}")
                print(f"Erros: {result.stderr}")
            
        except subprocess.TimeoutExpired:
            print("❌ Timeout nos testes unitários")
            self.resultados['unitarios']['detalhes'] = "Timeout após 60 segundos"
        except Exception as e:
            print(f"❌ Erro ao executar testes unitários: {str(e)}")
            self.resultados['unitarios']['detalhes'] = str(e)
    
    def executar_testes_integracao(self):
        """Executar testes de integração"""
        self.print_header("EXECUTANDO TESTES DE INTEGRAÇÃO")
        
        try:
            print("🔍 Executando testes de integração...")
            print("⚠️  Certifique-se de que o servidor está rodando em http://127.0.0.1:8000")
            time.sleep(2)  # Dar tempo para o usuário ver a mensagem
            
            result = subprocess.run([
                sys.executable, "test_integracao_fix.py"
            ], capture_output=True, text=True, timeout=120)
            
            self.resultados['integracao']['executado'] = True
            self.resultados['integracao']['sucesso'] = result.returncode == 0
            self.resultados['integracao']['detalhes'] = result.stdout + result.stderr
            
            print(result.stdout)  # Mostrar output do teste de integração
            
            if result.returncode == 0:
                print("✅ Testes de integração PASSARAM")
            else:
                print("❌ Testes de integração FALHARAM")
                if result.stderr:
                    print(f"Erros: {result.stderr}")
            
        except subprocess.TimeoutExpired:
            print("❌ Timeout nos testes de integração")
            self.resultados['integracao']['detalhes'] = "Timeout após 120 segundos"
        except Exception as e:
            print(f"❌ Erro ao executar testes de integração: {str(e)}")
            self.resultados['integracao']['detalhes'] = str(e)
    
    def executar_testes_validacao(self):
        """Executar testes de validação"""
        self.print_header("EXECUTANDO TESTES DE VALIDAÇÃO")
        
        try:
            print("🔍 Executando testes de validação...")
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "test_validacao.py", 
                "-v", "--tb=short", "--color=yes"
            ], capture_output=True, text=True, timeout=60)
            
            self.resultados['validacao']['executado'] = True
            self.resultados['validacao']['sucesso'] = result.returncode == 0
            self.resultados['validacao']['detalhes'] = result.stdout + result.stderr
            
            if result.returncode == 0:
                print("✅ Testes de validação PASSARAM")
            else:
                print("❌ Testes de validação FALHARAM")
                print(f"Saída: {result.stdout}")
                if result.stderr:
                    print(f"Erros: {result.stderr}")
            
        except subprocess.TimeoutExpired:
            print("❌ Timeout nos testes de validação")
            self.resultados['validacao']['detalhes'] = "Timeout após 60 segundos"
        except Exception as e:
            print(f"❌ Erro ao executar testes de validação: {str(e)}")
            self.resultados['validacao']['detalhes'] = str(e)
    
    def executar_testes_negativos(self):
        """Executar testes de cenários negativos"""
        self.print_header("EXECUTANDO TESTES DE CENÁRIOS NEGATIVOS")
        
        try:
            print("🔍 Executando testes de cenários negativos...")
            print("⚠️  Certifique-se de que o servidor está rodando em http://127.0.0.1:8000")
            time.sleep(2)
            
            result = subprocess.run([
                sys.executable, "test_negativos_fix.py"
            ], capture_output=True, text=True, timeout=120)
            
            self.resultados['negativos']['executado'] = True
            self.resultados['negativos']['sucesso'] = result.returncode == 0
            self.resultados['negativos']['detalhes'] = result.stdout + result.stderr
            
            print(result.stdout)  # Mostrar output dos testes negativos
            
            if result.returncode == 0:
                print("✅ Testes de cenários negativos PASSARAM")
            else:
                print("❌ Testes de cenários negativos FALHARAM")
                if result.stderr:
                    print(f"Erros: {result.stderr}")
            
        except subprocess.TimeoutExpired:
            print("❌ Timeout nos testes de cenários negativos")
            self.resultados['negativos']['detalhes'] = "Timeout após 120 segundos"
        except Exception as e:
            print(f"❌ Erro ao executar testes de cenários negativos: {str(e)}")
            self.resultados['negativos']['detalhes'] = str(e)
    
    def verificar_servidor(self):
        """Verificar se o servidor está rodando"""
        self.print_header("VERIFICANDO SERVIDOR")
        
        try:
            import requests
            response = requests.get("http://127.0.0.1:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Servidor está rodando e respondendo")
                return True
            else:
                print(f"❌ Servidor respondeu com status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Não foi possível conectar ao servidor")
            print("   Por favor, inicie o servidor com:")
            print("   uv run uvicorn api:app --host 127.0.0.1 --port 8000")
            return False
        except Exception as e:
            print(f"❌ Erro ao verificar servidor: {str(e)}")
            return False
    
    def gerar_relatorio_final(self):
        """Gerar relatório final de todos os testes"""
        self.print_header("RELATÓRIO FINAL DA SUÍTE DE TESTES")
        
        fim = datetime.now()
        duracao = fim - self.inicio
        
        print(f"⏱️  Duração total: {duracao}")
        print(f"📅 Executado em: {fim.strftime('%d/%m/%Y %H:%M:%S')}")
        
        self.print_separator()
        
        # Resumo por tipo de teste
        tipos_teste = [
            ("Testes Unitários", "unitarios"),
            ("Testes de Integração", "integracao"),
            ("Testes de Validação", "validacao"),
            ("Testes de Cenários Negativos", "negativos")
        ]
        
        total_executados = 0
        total_sucessos = 0
        
        for nome, key in tipos_teste:
            resultado = self.resultados[key]
            if resultado['executado']:
                total_executados += 1
                status = "✅ PASSOU" if resultado['sucesso'] else "❌ FALHOU"
                print(f"{nome}: {status}")
                if resultado['sucesso']:
                    total_sucessos += 1
            else:
                print(f"{nome}: ⏭️  NÃO EXECUTADO")
        
        self.print_separator()
        
        # Resumo geral
        print(f"📊 RESUMO GERAL:")
        print(f"   Total de tipos de teste: {len(tipos_teste)}")
        print(f"   Executados: {total_executados}")
        print(f"   Sucessos: {total_sucessos}")
        print(f"   Falhas: {total_executados - total_sucessos}")
        
        if total_executados > 0:
            taxa_sucesso = (total_sucessos / total_executados) * 100
            print(f"   Taxa de sucesso: {taxa_sucesso:.1f}%")
            
            if taxa_sucesso == 100:
                print("\n🎉 PERFEITO! Todos os testes passaram!")
                print("   O sistema está funcionando corretamente em todos os aspectos.")
            elif taxa_sucesso >= 75:
                print("\n✅ MUITO BOM! Maioria dos testes passou.")
                print("   O sistema está funcionando bem com alguns ajustes necessários.")
            elif taxa_sucesso >= 50:
                print("\n⚠️  REGULAR! Alguns testes falharam.")
                print("   O sistema precisa de correções antes de ir para produção.")
            else:
                print("\n❌ CRÍTICO! Muitos testes falharam.")
                print("   O sistema precisa de revisão completa.")
        
        # Recomendações
        self.print_separator()
        print("💡 RECOMENDAÇÕES:")
        
        if not self.resultados['unitarios']['sucesso']:
            print("   • Revisar lógica de negócios nas classes Service e Repository")
        
        if not self.resultados['integracao']['sucesso']:
            print("   • Verificar endpoints da API e fluxos de integração")
        
        if not self.resultados['validacao']['sucesso']:
            print("   • Revisar schemas Pydantic e validações de dados")
        
        if not self.resultados['negativos']['sucesso']:
            print("   • Implementar melhor tratamento de erros e casos extremos")
        
        print("   • Manter testes atualizados conforme o sistema evolui")
        print("   • Executar testes regularmente durante o desenvolvimento")
        
        return total_sucessos == total_executados
    
    def executar_suite_completa(self):
        """Executar toda a suíte de testes"""
        print("🚀 INICIANDO SUÍTE COMPLETA DE TESTES DO SISTEMA DE CONVITES")
        print("=" * 80)
        print("Esta suíte executará:")
        print("  1. Testes Unitários (lógica de negócios)")
        print("  2. Testes de Integração (API endpoints)")
        print("  3. Testes de Validação (schemas e dados)")
        print("  4. Testes de Cenários Negativos (casos extremos)")
        print("=" * 80)
        
        # Verificar se o servidor está rodando para testes que precisam
        servidor_rodando = self.verificar_servidor()
        
        # Executar cada tipo de teste
        self.executar_testes_unitarios()
        
        if servidor_rodando:
            self.executar_testes_integracao()
            self.executar_testes_negativos()
        else:
            print("⏭️  Pulando testes que requerem servidor")
        
        self.executar_testes_validacao()
        
        # Gerar relatório final
        sucesso_geral = self.gerar_relatorio_final()
        
        return 0 if sucesso_geral else 1


def main():
    """Função principal"""
    runner = TestRunner()
    return runner.executar_suite_completa()


if __name__ == "__main__":
    exit_code = main()
    print(f"\n🔚 Finalizado com código de saída: {exit_code}")
    sys.exit(exit_code)