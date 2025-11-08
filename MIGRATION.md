# Migração para uv - Resumo das Mudanças

## Arquivos Criados/Modificados

### 1. **pyproject.toml** (NOVO)
- Configuração moderna do projeto Python
- Dependências definidas no padrão PEP 621
- Separação entre dependências principais e de desenvolvimento
- Configuração do uv para dev-dependencies

### 2. **README.md** (ATUALIZADO)
- Seção sobre benefícios do uv
- Instruções de instalação do uv
- Comandos atualizados para usar `uv run`
- Scripts de desenvolvimento automatizados
- Compatibilidade mantida com pip

### 3. **dev.bat** (NOVO - Windows)
- Script automatizado para desenvolvimento
- Sincroniza dependências, inicializa DB e inicia servidor

### 4. **dev.sh** (NOVO - Linux/macOS)
- Versão do script para sistemas Unix

### 5. **.gitignore** (NOVO)
- Ignora arquivos do uv (.uv/, uv.lock)
- Configuração completa para projetos Python

## Benefícios da Migração

### Performance
- uv é 10-100x mais rápido que pip
- Instalação quase instantânea de dependências

### Reprodutibilidade
- Lock files garantem versões exatas
- Ambientes consistentes entre desenvolvedores

### Facilidade de Uso
- `uv sync` instala tudo automaticamente
- `uv run` executa comandos no ambiente correto
- Criação automática de ambientes virtuais

### Compatibilidade
- Funciona com requirements.txt existente
- Migração gradual possível
- Não quebra workflows existentes

## Como Usar

### Instalação do uv
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Comandos Principais
```bash
uv pip install -r requirements.txt   # Instalar dependências
uv pip install <package>            # Adicionar pacote
uv pip uninstall <package>          # Remover pacote
.venv\Scripts\python.exe <comando>   # Executar no ambiente (Windows)
.venv/bin/python <comando>           # Executar no ambiente (Linux/macOS)
.venv\Scripts\uvicorn.exe api:app --reload  # Iniciar servidor
```

### Scripts de Desenvolvimento
```bash
# Windows
.\dev.bat

# Linux/macOS  
./dev.sh
```

## Compatibilidade

O projeto mantém total compatibilidade com pip:
- `requirements.txt` ainda funciona
- `pip install -r requirements.txt` ainda funciona
- Migração é opcional e gradual

## Próximos Passos

1. Instalar uv no sistema
2. Executar `uv pip install -r requirements.txt` para testar
3. Usar `.venv\Scripts\python.exe` (Windows) ou `.venv/bin/python` (Linux/macOS) para comandos Python
4. Experimentar scripts de desenvolvimento
5. Migrar gradualmente para comandos uv

## Observações Importantes

- O `uv sync` com pyproject.toml teve problemas de compatibilidade
- A abordagem `uv pip install -r requirements.txt` funcionou perfeitamente
- O ambiente virtual `.venv` foi criado automaticamente pelo uv
- Todas as dependências foram instaladas com sucesso, incluindo psycopg2-binary