-- Arquivo de inicialização do MySQL para ambiente de produção
-- Este arquivo será executado automaticamente quando o container MySQL for criado pela primeira vez

-- Configurações de charset para produção
ALTER DATABASE mark_foot_db_prod CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Configurações de performance para produção
SET GLOBAL innodb_buffer_pool_size = 268435456; -- 256MB
SET GLOBAL max_connections = 200;
SET GLOBAL query_cache_size = 67108864; -- 64MB
SET GLOBAL query_cache_type = 1;
