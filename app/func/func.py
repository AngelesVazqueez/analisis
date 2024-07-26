from flask import current_app, session, redirect, url_for
from functools import wraps
import pymysql

def obtener_areas(usuario_id):
    """Función para obtener todas las áreas disponibles desde la base de datos."""
    connection = current_app.get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = """
            SELECT IdArea, NombreArea
            FROM Areas
            WHERE id = %s
            """
            cursor.execute(query, (usuario_id,))
            areas = cursor.fetchall()
            return areas
    except pymysql.MySQLError as err:
        print(f"Error al obtener áreas desde la base de datos: {err.args[0]}, {err.args[1]}")
        return []

def obtener_departamentos():
    """Función para obtener todas las áreas disponibles desde la base de datos."""
    connection = current_app.get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT IdArea, NombreArea FROM Departamentos")
            areas = cursor.fetchall()
            return areas
    except pymysql.MySQLError as err:
        print(f"Error al obtener departamentos desde la base de datos: {err.args[0]}, {err.args[1]}")
        return []


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return wrap