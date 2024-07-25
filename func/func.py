import database.database as dbase
import mysql.connector
from flask import url_for, redirect, session


# Obtener la conexión a la base de datos
connection = dbase.dbConnection()


def obtener_areas(usuario_id):
    """Función para obtener todas las áreas disponibles desde la base de datos."""
    try:
        cursor = connection.cursor()
        query = """
        SELECT IdArea, NombreArea
        FROM Areas
        WHERE id = %s
        """
        cursor.execute(query, (usuario_id,))
        areas = cursor.fetchall()
        return areas
    except mysql.connector.Error as err:
        print(f"Error al obtener áreas desde la base de datos: {err}")
        return []
    
def obtener_departamentos():
    """Función para obtener todas las áreas disponibles desde la base de datos."""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT IdArea, NombreArea FROM Departamentos")
        areas = cursor.fetchall()
        return areas
    except mysql.connector.Error as err:
        print(f"Error al obtener departamentos desde la base de datos: {err}")
        return []
    
def login_required(f):
    def wrap(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return wrap