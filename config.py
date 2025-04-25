import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configurações da aplicação Flask
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Configurações do banco de dados MySQL
    MYSQL_DATABASE_HOST = os.getenv('MYSQL_HOST')
    MYSQL_DATABASE_USER = os.getenv('MYSQL_USER')
    MYSQL_DATABASE_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_DATABASE_DB = os.getenv('MYSQL_DB')
