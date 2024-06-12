import os
import mysql.connector

# Conexion a la base de datos
conexion = mysql.connector.connect(
   host = os.environ.get("DB_HOST"), 
   port = os.environ.get("DB_PORT") ,
   user = os.environ.get("DB_USER") ,
   password = os.environ.get("DB_PASSWORD"),
   db = os.environ.get("DB_NAME"),
)