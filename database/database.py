import mysql.connector
import os


def dbConnection():
    try:
        # Crear la conexión a la base de datos MySQL
        connection = mysql.connector.connect(
            host='sql5.freemysqlhosting.net',
            user='sql5720463',
            password='EUTLx1IP9A',
            database='sql5720463'
        )
        print("Conexión exitosa a la base de datos MySQL")
        return connection
    except mysql.connector.Error as err:
        print("Error de conexión a la base de datos MySQL:", err)
        return None
