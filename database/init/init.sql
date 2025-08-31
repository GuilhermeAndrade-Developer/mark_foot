-- Arquivo de inicialização do MySQL
-- Este arquivo será executado automaticamente quando o container MySQL for criado pela primeira vez

-- Exemplo: Criar usuário adicional ou configurações específicas
-- CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED BY 'app_password';
-- GRANT ALL PRIVILEGES ON mark_foot_db.* TO 'app_user'@'%';

-- Configurações de charset para desenvolvimento
-- Nota: O nome do banco será determinado pela variável MYSQL_DATABASE do docker-compose
-- Para dev: mark_foot_db_dev
-- Para prod: mark_foot_db_prod

-- Esta linha será executada apenas se o banco de desenvolvimento existir
SET @database_name = (SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'mark_foot_db_dev');
SET @sql = IF(@database_name IS NOT NULL, 'ALTER DATABASE mark_foot_db_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci', 'SELECT "Dev database not found" as message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Esta linha será executada apenas se o banco de produção existir
SET @database_name = (SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'mark_foot_db_prod');
SET @sql = IF(@database_name IS NOT NULL, 'ALTER DATABASE mark_foot_db_prod CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci', 'SELECT "Prod database not found" as message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
