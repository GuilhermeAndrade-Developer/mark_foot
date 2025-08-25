-- Arquivo de exemplo para inicialização do MySQL
-- Este arquivo será executado automaticamente quando o container MySQL for criado pela primeira vez

-- Exemplo: Criar usuário adicional ou configurações específicas
-- CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED BY 'app_password';
-- GRANT ALL PRIVILEGES ON mark_foot_db.* TO 'app_user'@'%';

-- Configurações de charset
ALTER DATABASE mark_foot_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
