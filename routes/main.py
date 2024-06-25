from flask import Blueprint, render_template, redirect, url_for, flash, request, session
import database.database as dbase
import mysql.connector


# Obtener la conexión a la base de datos
connection = dbase.dbConnection()

main_routes = Blueprint('main', __name__)


# Ruta principal
@main_routes.route('/')
def index():
    return render_template('index.html')
  

# Ruta para iniciar usuario o admin
@main_routes.route('/login/', methods=['POST'])
def iniciar():
    cursor = connection.cursor(dictionary=True)
    try:
        email = request.form['email']
        password = request.form['password']

        # Buscar en la tabla de users
        cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
        login_user = cursor.fetchone()
        if login_user and login_user['password'] == password:
            session['email'] = email
            return redirect(url_for('user.user'))

        # Buscar en la tabla de admin
        cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
        login_admin = cursor.fetchone()
        if login_admin and login_admin['password'] == password:
            session['email'] = email
            return redirect(url_for('admin.admin'))

        flash('Correo o contraseña incorrectos')
        return redirect(url_for('session.login'))
    except mysql.connector.Error as err:
        print("Error al iniciar sesión:", err)
    finally:
        cursor.close()


# Ruta para cerrar sesión
@main_routes.route('/logout/')
def logout():
    session.clear()  # Elimina todas las variables de sesión
    return redirect(url_for('main.index'))
