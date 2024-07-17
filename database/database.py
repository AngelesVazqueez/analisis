import mysql.connector
import os

# Obtener las variables de entorno
MYSQL_HOST = os.environ.get('MYSQL_HOST')
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')

def dbConnection():
    try:
        # Crear la conexión a la base de datos MySQL
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        print("Conexión exitosa a la base de datos MySQL")
        return connection
    except mysql.connector.Error as err:
        print("Error de conexión a la base de datos MySQL:", err)
        return None

dbConnection()