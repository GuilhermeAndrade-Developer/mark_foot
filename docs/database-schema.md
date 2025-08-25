# Database Schema - Mark Foot

## Visão Geral
Estrutura de banco de dados otimizada para armazenar dados de futebol com foco em escalabilidade e performance para análises futuras.

## Diagrama Conceitual

```
Areas (Países/Regiões)
  ├── Competitions (Competições)
  │   ├── Seasons (Temporadas)
  │   │   ├── Teams (Times participantes)
  │   │   ├── Matches (Partidas)
  │   │   │   ├── Match_Events (Eventos da partida)
  │   │   │   └── Match_Lineups (Escalações)
  │   │   └── Standings (Classificações)
  │   └── Competition_Teams (Times históricos)
  └── Teams (Times)
      ├── Players (Jogadores)
      │   ├── Player_Statistics (Estatísticas)
      │   ├── Player_Transfers (Transferências)
      │   └── Player_Match_Performance (Performance por partida)
      └── Team_Statistics (Estatísticas do time)
```

---

## Tabelas Principais

### 1. areas (Países/Regiões)
```sql
CREATE TABLE areas (
    id BIGINT PRIMARY KEY,                    -- ID da API
    name VARCHAR(100) NOT NULL,               -- Nome (Brasil, England, etc.)
    code VARCHAR(10),                         -- Código (BRA, ENG, etc.)
    flag_url VARCHAR(255),                    -- URL da bandeira
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_areas_code (code),
    INDEX idx_areas_name (name)
);
```

### 2. competitions (Competições)
```sql
CREATE TABLE competitions (
    id BIGINT PRIMARY KEY,                    -- ID da API
    area_id BIGINT,                          -- FK para areas
    name VARCHAR(100) NOT NULL,               -- Nome da competição
    code VARCHAR(10) NOT NULL,                -- Código (PL, CL, etc.)
    type ENUM('LEAGUE', 'CUP', 'TOURNAMENT') NOT NULL,
    emblem_url VARCHAR(255),                  -- URL do emblema
    plan ENUM('TIER_ONE', 'TIER_TWO', 'TIER_THREE', 'TIER_FOUR'),
    current_season_id BIGINT,                 -- FK para seasons (temporada atual)
    number_of_available_seasons INT DEFAULT 0,
    last_updated TIMESTAMP,                   -- Última atualização da API
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (area_id) REFERENCES areas(id) ON DELETE SET NULL,
    INDEX idx_competitions_code (code),
    INDEX idx_competitions_area_id (area_id),
    INDEX idx_competitions_type (type)
);
```

### 3. seasons (Temporadas)
```sql
CREATE TABLE seasons (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    competition_id BIGINT NOT NULL,           -- FK para competitions
    start_date DATE NOT NULL,                 -- Data de início
    end_date DATE NOT NULL,                   -- Data de fim
    current_matchday INT DEFAULT 1,           -- Rodada atual
    winner_team_id BIGINT,                    -- FK para teams (campeão)
    available BOOLEAN DEFAULT TRUE,           -- Disponível na API
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (competition_id) REFERENCES competitions(id) ON DELETE CASCADE,
    FOREIGN KEY (winner_team_id) REFERENCES teams(id) ON DELETE SET NULL,
    INDEX idx_seasons_competition_id (competition_id),
    INDEX idx_seasons_dates (start_date, end_date),
    UNIQUE KEY uk_seasons_competition_year (competition_id, start_date)
);
```

### 4. teams (Times)
```sql
CREATE TABLE teams (
    id BIGINT PRIMARY KEY,                    -- ID da API
    area_id BIGINT,                          -- FK para areas
    name VARCHAR(100) NOT NULL,               -- Nome do time
    short_name VARCHAR(50),                   -- Nome abreviado
    tla VARCHAR(10),                         -- Three Letter Abbreviation
    crest_url VARCHAR(255),                   -- URL do escudo
    address TEXT,                            -- Endereço
    phone VARCHAR(20),                       -- Telefone
    website VARCHAR(255),                    -- Website oficial
    email VARCHAR(100),                      -- Email
    founded YEAR,                            -- Ano de fundação
    club_colors VARCHAR(100),                -- Cores do clube
    venue VARCHAR(100),                      -- Estádio
    last_updated TIMESTAMP,                  -- Última atualização da API
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (area_id) REFERENCES areas(id) ON DELETE SET NULL,
    INDEX idx_teams_name (name),
    INDEX idx_teams_short_name (short_name),
    INDEX idx_teams_tla (tla),
    INDEX idx_teams_area_id (area_id)
);
```

### 5. matches (Partidas)
```sql
CREATE TABLE matches (
    id BIGINT PRIMARY KEY,                    -- ID da API
    competition_id BIGINT NOT NULL,           -- FK para competitions
    season_id BIGINT NOT NULL,                -- FK para seasons
    home_team_id BIGINT NOT NULL,             -- FK para teams
    away_team_id BIGINT NOT NULL,             -- FK para teams
    utc_date DATETIME NOT NULL,               -- Data/hora UTC
    status ENUM('SCHEDULED', 'LIVE', 'IN_PLAY', 'PAUSED', 'FINISHED', 'POSTPONED', 'SUSPENDED', 'CANCELLED') NOT NULL,
    stage VARCHAR(50),                        -- Fase da competição
    group_name VARCHAR(10),                   -- Grupo (se aplicável)
    matchday INT,                            -- Rodada
    last_updated TIMESTAMP,                   -- Última atualização da API
    
    -- Resultado
    home_team_score INT,                     -- Gols do mandante
    away_team_score INT,                     -- Gols do visitante
    winner ENUM('HOME_TEAM', 'AWAY_TEAM', 'DRAW'),
    duration ENUM('REGULAR', 'EXTRA_TIME', 'PENALTY_SHOOTOUT') DEFAULT 'REGULAR',
    
    -- Estatísticas adicionais (para futuro)
    attendance INT,                          -- Público
    referee_name VARCHAR(100),               -- Árbitro principal
    venue VARCHAR(100),                      -- Local da partida
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (competition_id) REFERENCES competitions(id) ON DELETE CASCADE,
    FOREIGN KEY (season_id) REFERENCES seasons(id) ON DELETE CASCADE,
    FOREIGN KEY (home_team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (away_team_id) REFERENCES teams(id) ON DELETE CASCADE,
    
    INDEX idx_matches_competition_season (competition_id, season_id),
    INDEX idx_matches_teams (home_team_id, away_team_id),
    INDEX idx_matches_date (utc_date),
    INDEX idx_matches_status (status),
    INDEX idx_matches_matchday (matchday)
);
```

### 6. standings (Classificações)
```sql
CREATE TABLE standings (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    competition_id BIGINT NOT NULL,           -- FK para competitions
    season_id BIGINT NOT NULL,                -- FK para seasons
    team_id BIGINT NOT NULL,                  -- FK para teams
    stage VARCHAR(50) DEFAULT 'REGULAR_SEASON', -- Fase da competição
    type ENUM('TOTAL', 'HOME', 'AWAY') DEFAULT 'TOTAL',
    group_name VARCHAR(10),                   -- Grupo (se aplicável)
    
    -- Estatísticas
    position INT NOT NULL,                    -- Posição na tabela
    played_games INT DEFAULT 0,               -- Jogos disputados
    form VARCHAR(10),                        -- Últimos 5 jogos (WWDLL)
    won INT DEFAULT 0,                       -- Vitórias
    draw INT DEFAULT 0,                      -- Empates
    lost INT DEFAULT 0,                      -- Derrotas
    points INT DEFAULT 0,                    -- Pontos
    goals_for INT DEFAULT 0,                 -- Gols marcados
    goals_against INT DEFAULT 0,             -- Gols sofridos
    goal_difference INT DEFAULT 0,           -- Saldo de gols
    
    snapshot_date DATE NOT NULL,             -- Data do snapshot
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (competition_id) REFERENCES competitions(id) ON DELETE CASCADE,
    FOREIGN KEY (season_id) REFERENCES seasons(id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    
    INDEX idx_standings_competition_season (competition_id, season_id),
    INDEX idx_standings_position (position),
    INDEX idx_standings_points (points DESC),
    INDEX idx_standings_snapshot_date (snapshot_date),
    UNIQUE KEY uk_standings_unique (competition_id, season_id, team_id, type, stage, snapshot_date)
);
```

---

## Tabelas para Dados de Jogadores (Preparação Futura)

### 7. players (Jogadores)
```sql
CREATE TABLE players (
    id BIGINT PRIMARY KEY,                    -- ID da API externa
    name VARCHAR(100) NOT NULL,               -- Nome completo
    first_name VARCHAR(50),                   -- Primeiro nome
    last_name VARCHAR(50),                    -- Último nome
    date_of_birth DATE,                      -- Data de nascimento
    nationality VARCHAR(50),                 -- Nacionalidade
    position ENUM('Goalkeeper', 'Defence', 'Midfield', 'Offence', 'Coach') NOT NULL,
    shirt_number INT,                        -- Número da camisa atual
    current_team_id BIGINT,                  -- FK para teams (time atual)
    market_value DECIMAL(12,2),              -- Valor de mercado
    contract_until DATE,                     -- Contrato até
    photo_url VARCHAR(255),                  -- URL da foto
    height_cm INT,                           -- Altura em cm
    weight_kg INT,                           -- Peso em kg
    preferred_foot ENUM('left', 'right', 'both'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (current_team_id) REFERENCES teams(id) ON DELETE SET NULL,
    INDEX idx_players_name (name),
    INDEX idx_players_position (position),
    INDEX idx_players_team (current_team_id),
    INDEX idx_players_nationality (nationality)
);
```

### 8. player_statistics (Estatísticas dos Jogadores)
```sql
CREATE TABLE player_statistics (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    player_id BIGINT NOT NULL,               -- FK para players
    competition_id BIGINT NOT NULL,          -- FK para competitions
    season_id BIGINT NOT NULL,               -- FK para seasons
    team_id BIGINT NOT NULL,                 -- FK para teams
    
    -- Estatísticas básicas
    appearances INT DEFAULT 0,               -- Jogos
    goals INT DEFAULT 0,                     -- Gols
    assists INT DEFAULT 0,                   -- Assistências
    yellow_cards INT DEFAULT 0,              -- Cartões amarelos
    red_cards INT DEFAULT 0,                 -- Cartões vermelhos
    minutes_played INT DEFAULT 0,            -- Minutos jogados
    
    -- Estatísticas avançadas (para futuro)
    shots INT DEFAULT 0,                     -- Chutes
    shots_on_target INT DEFAULT 0,           -- Chutes no gol
    passes_completed INT DEFAULT 0,          -- Passes certos
    passes_attempted INT DEFAULT 0,          -- Passes tentados
    tackles_won INT DEFAULT 0,               -- Desarmes certos
    fouls_committed INT DEFAULT 0,           -- Faltas cometidas
    fouls_suffered INT DEFAULT 0,            -- Faltas sofridas
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
    FOREIGN KEY (competition_id) REFERENCES competitions(id) ON DELETE CASCADE,
    FOREIGN KEY (season_id) REFERENCES seasons(id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    
    INDEX idx_player_stats_player (player_id),
    INDEX idx_player_stats_competition_season (competition_id, season_id),
    INDEX idx_player_stats_goals (goals DESC),
    INDEX idx_player_stats_assists (assists DESC),
    UNIQUE KEY uk_player_stats (player_id, competition_id, season_id, team_id)
);
```

---

## Tabelas de Controle e Logs

### 9. api_sync_logs (Logs de Sincronização)
```sql
CREATE TABLE api_sync_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    endpoint VARCHAR(255) NOT NULL,          -- Endpoint consultado
    http_status INT,                         -- Status HTTP da resposta
    records_processed INT DEFAULT 0,         -- Registros processados
    records_inserted INT DEFAULT 0,          -- Registros inseridos
    records_updated INT DEFAULT 0,           -- Registros atualizados
    records_failed INT DEFAULT 0,            -- Registros com falha
    execution_time_ms INT,                   -- Tempo de execução em ms
    error_message TEXT,                      -- Mensagem de erro (se houver)
    request_params JSON,                     -- Parâmetros da requisição
    response_data JSON,                      -- Dados da resposta (sample)
    sync_date DATETIME NOT NULL,             -- Data/hora da sincronização
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_sync_logs_endpoint (endpoint),
    INDEX idx_sync_logs_date (sync_date),
    INDEX idx_sync_logs_status (http_status)
);
```

### 10. data_quality_checks (Verificações de Qualidade)
```sql
CREATE TABLE data_quality_checks (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    table_name VARCHAR(50) NOT NULL,         -- Tabela verificada
    check_type ENUM('completeness', 'accuracy', 'consistency', 'timeliness') NOT NULL,
    check_description TEXT,                  -- Descrição da verificação
    records_checked INT DEFAULT 0,           -- Registros verificados
    records_passed INT DEFAULT 0,            -- Registros que passaram
    records_failed INT DEFAULT 0,            -- Registros que falharam
    success_rate DECIMAL(5,2),               -- Taxa de sucesso (%)
    details JSON,                           -- Detalhes específicos
    check_date DATETIME NOT NULL,            -- Data/hora da verificação
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_quality_checks_table (table_name),
    INDEX idx_quality_checks_date (check_date),
    INDEX idx_quality_checks_type (check_type)
);
```

---

## Índices de Performance

```sql
-- Índices compostos para consultas frequentes
CREATE INDEX idx_matches_competition_date ON matches(competition_id, utc_date);
CREATE INDEX idx_matches_team_date ON matches(home_team_id, away_team_id, utc_date);
CREATE INDEX idx_standings_competition_position ON standings(competition_id, season_id, position);

-- Índices para relatórios
CREATE INDEX idx_players_stats_goals_season ON player_statistics(season_id, goals DESC);
CREATE INDEX idx_players_stats_assists_season ON player_statistics(season_id, assists DESC);

-- Índices de busca por texto
CREATE FULLTEXT INDEX idx_teams_search ON teams(name, short_name);
CREATE FULLTEXT INDEX idx_players_search ON players(name, first_name, last_name);
```

---

## Views Úteis

```sql
-- View para estatísticas de times por temporada
CREATE VIEW team_season_stats AS
SELECT 
    t.id as team_id,
    t.name as team_name,
    c.id as competition_id,
    c.name as competition_name,
    s.id as season_id,
    COUNT(m.id) as total_matches,
    SUM(CASE WHEN m.winner = 'HOME_TEAM' AND m.home_team_id = t.id THEN 1
             WHEN m.winner = 'AWAY_TEAM' AND m.away_team_id = t.id THEN 1
             ELSE 0 END) as wins,
    SUM(CASE WHEN m.winner = 'DRAW' THEN 1 ELSE 0 END) as draws,
    SUM(CASE WHEN m.winner = 'HOME_TEAM' AND m.away_team_id = t.id THEN 1
             WHEN m.winner = 'AWAY_TEAM' AND m.home_team_id = t.id THEN 1
             ELSE 0 END) as losses
FROM teams t
JOIN matches m ON (t.id = m.home_team_id OR t.id = m.away_team_id)
JOIN competitions c ON m.competition_id = c.id
JOIN seasons s ON m.season_id = s.id
WHERE m.status = 'FINISHED'
GROUP BY t.id, c.id, s.id;
```

---

## Considerações Técnicas

### Performance
- **Particionamento**: Considerar particionamento por ano nas tabelas `matches` e `standings`
- **Archiving**: Implementar estratégia de arquivamento para dados antigos
- **Caching**: Cache de consultas frequentes (classificações atuais, próximos jogos)

### Segurança
- **Backup**: Backup automático diário com retenção de 30 dias
- **Auditoria**: Log de todas as alterações em tabelas críticas
- **Validação**: Constraints para garantir integridade dos dados

### Escalabilidade
- **Read Replicas**: Para consultas analíticas pesadas
- **Sharding**: Possível sharding por competição para grandes volumes
- **Indexação**: Monitoramento contínuo de performance de queries
