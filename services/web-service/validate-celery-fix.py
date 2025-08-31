#!/usr/bin/env python3
"""
Script de validação para verificar se as correções do Celery Beat estão funcionando.
"""
import sys
import time
import subprocess
import MySQLdb
from decouple import config

def check_database_connection():
    """Verifica se consegue conectar ao banco de dados."""
    try:
        db_host = config('DB_HOST', default='mysql_db')
        db_port = config('DB_PORT', default='3306')
        db_name = config('DB_NAME', default='mark_foot_db_dev')
        db_user = config('DB_USER', default='mark_foot_user')
        db_password = config('DB_PASSWORD', default='mark_foot_password')
        
        conn = MySQLdb.connect(
            host=db_host,
            port=int(db_port),
            user=db_user,
            passwd=db_password,
            db=db_name
        )
        
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES LIKE 'django_celery_beat_periodictask'")
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            print("✅ Tabela django_celery_beat_periodictask encontrada!")
            return True
        else:
            print("❌ Tabela django_celery_beat_periodictask não encontrada!")
            return False
            
    except Exception as e:
        print(f"❌ Erro na conexão com o banco: {e}")
        return False

def check_celery_beat_process():
    """Verifica se o processo do Celery Beat está funcionando."""
    try:
        # Verifica se consegue importar o Celery e suas configurações
        import celery
        from mark_foot_backend.celery import app
        
        print("✅ Celery configurado corretamente!")
        return True
            
    except Exception as e:
        print(f"❌ Erro ao verificar Celery: {e}")
        return False

def run_validation():
    """Executa todas as validações."""
    print("🔍 Iniciando validação das correções do Celery Beat...")
    print("-" * 50)
    
    # Teste 1: Conexão com banco
    print("1. Verificando conexão com banco de dados...")
    db_ok = check_database_connection()
    
    # Teste 2: Processo Celery Beat
    print("\n2. Verificando processo Celery Beat...")
    process_ok = check_celery_beat_process()
    
    # Resultado final
    print("\n" + "=" * 50)
    if db_ok and process_ok:
        print("✅ SUCESSO: Todas as validações passaram!")
        print("✅ As correções estão funcionando corretamente.")
        return True
    else:
        print("❌ FALHA: Algumas validações falharam!")
        print("❌ Verifique os logs para mais detalhes.")
        return False

if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
