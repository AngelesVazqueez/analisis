from flask import Blueprint, render_template, redirect, url_for, flash, request, session
import database.database as dbase
import mysql.connector
import bcrypt


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
        if login_user and bcrypt.checkpw(password.encode('utf-8'), login_user['password'].encode('utf-8') if isinstance(login_user['password'], str) else login_user['password']):
            session['email'] = email
            return redirect(url_for('user.user'))

        # Buscar en la tabla de admin
        cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
        login_admin = cursor.fetchone()
        if login_admin and bcrypt.checkpw(password.encode('utf-8'), login_admin['password'].encode('utf-8') if isinstance(login_admin['password'], str) else login_admin['password']):
            session['email'] = email
            return redirect(url_for('admin.admin'))

        flash('Correo o contraseña incorrectos')
        return redirect(url_for('main.index'))
    except mysql.connector.Error as err:
        print("Error al iniciar sesión:", err)
        flash('Hubo un error al iniciar sesión. Inténtalo de nuevo.')
        return redirect(url_for('main.index'))
    finally:
        cursor.close()


# Ruta para cerrar sesión
@main_routes.route('/logout/')
def logout():
    session.clear()  # Elimina todas las variables de sesión
    return redirect(url_for('main.index'))
