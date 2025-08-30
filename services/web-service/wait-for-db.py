#!/usr/bin/env python3
"""
Script para aguardar a disponibilidade do banco de dados antes de iniciar o Django.
"""
import sys
import time
import MySQLdb
from decouple import config

def wait_for_db():
    """Aguarda até que o banco de dados esteja disponível."""
    db_host = config('DB_HOST', default='mysql_db')
    db_port = config('DB_PORT', default='3306')
    db_name = config('DB_NAME', default='mark_foot_db_dev')
    db_user = config('DB_USER', default='mark_foot_user')
    db_password = config('DB_PASSWORD', default='mark_foot_password')
    
    print(f"Waiting for database {db_name} at {db_host}:{db_port}...")
    
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            conn = MySQLdb.connect(
                host=db_host,
                port=int(db_port),
                user=db_user,
                passwd=db_password,
                db=db_name
            )
            conn.close()
            print("Database is ready!")
            return True
        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt}/{max_attempts}: Database not ready yet ({e})")
            time.sleep(2)
    
    print("Failed to connect to database after all attempts.")
    return False

if __name__ == "__main__":
    if wait_for_db():
        sys.exit(0)
    else:
        sys.exit(1)
