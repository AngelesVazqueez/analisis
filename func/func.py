import database.database as dbase
import mysql.connector


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
