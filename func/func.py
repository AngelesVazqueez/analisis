import database.database as dbase
import mysql.connector
from flask import url_for, redirect, session


# Obtener la conexión a la base de datos
connection = dbase.dbConnection()


# Función para obtener un usuario por su correo electrónico
def get_user(email):
    if connection:
        try:
            cursor = connection .cursor(dictionary=True)
            cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
            user = cursor.fetchone()
            return user
        except mysql.connector.Error as err:
            print("Error al obtener usuario:", err)
    return None


# Función para obtener un administrador por su correo electrónico
def get_admin(email):
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
            admin = cursor.fetchone()
            return admin
        except mysql.connector.Error as err:
            print("Error al obtener administrador:", err)
    return None

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