# API de Marcação de Vôlei ⚽

## Sobre o Projeto

Este projeto é uma **API REST** desenvolvida em **FastAPI** para gerenciar partidas de vôlei. O objetivo é permitir que jogadores se organizem, criem partidas, participem de jogos e avaliem suas experiências.

## Funcionalidades Principais

### 👥 Gestão de Jogadores
- **Cadastro de atletas** com diferentes níveis de habilidade
- **Sistema de ranking** por categoria (noob, amador, intermediário, proplayer)
- **Listagem de jogadores** e melhores atletas

### 🏐 Gestão de Partidas  
- **Criação de partidas** com classificação por nível
  - **Iniciante**: apenas jogadores noob
  - **Normal**: jogadores amadores e intermediários
  - **Ranked**: jogadores profissionais
- **Ativar/desativar partidas**
- **Controle de pontuação** durante os jogos

### 🤝 Sistema de Participação
- **Candidatura** para participar de partidas
- **Aprovação/rejeição** de candidaturas pelo organizador
- **Entrada controlada** baseada no nível do jogador

### ⭐ Sistema de Avaliações
- **Avaliar partidas** após o jogo
- **Avaliar organizadores** que criam as partidas  
- **Avaliar outros jogadores** da partida

### 👨‍💼 Gestão de Equipes
- **Criar equipes** associando atletas
- **Ranking de equipes** baseado em desempenho

## Tipos de Usuário

- **Noob**: Jogador iniciante
- **Amador**: Jogador recreativo com experiência básica
- **Intermediário**: Jogador com boa experiência
- **Proplayer**: Jogador profissional/avançado

## Tecnologias Utilizadas

- **FastAPI**: Framework web moderno para APIs
- **Pydantic**: Validação de dados e serialização
- **Python**: Linguagem de programação

## Como Usar

1. **Instale as dependências**:
   ```bash
   pip install fastapi uvicorn
   ```

2. **Execute o servidor**:
   ```bash
   uvicorn api:app --reload
   ```

3. **Acesse a documentação**:
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - Redoc: `http://127.0.0.1:8000/redoc`

## Estrutura da API

A API segue uma estrutura REST com endpoints organizados por funcionalidade:

- `/partidas/*` - Gestão de partidas
- `/atletas/*` - Gestão de jogadores  
- `/equipes/*` - Gestão de equipes
- `/organizadores/*` - Gestão de organizadores

## Objetivo Educacional

Este projeto foi desenvolvido como exercício acadêmico para demonstrar:
- **Mapeamento de APIs REST**
- **Definição de tipos de dados** (Request/Response)
- **Organização de endpoints** por funcionalidade
- **Boas práticas** de desenvolvimento com FastAPI

---

*Projeto desenvolvido para fins educacionais - Programação para internet II*
*Professor Rogério Silva*