from flask import Blueprint, render_template, url_for, redirect, flash, session, request
import database.database as dbase
import mysql.connector
from func.func import get_admin
import bcrypt


# Obtener la conexión a la base de datos
connection = dbase.dbConnection()

admin_routes = Blueprint('admin', __name__)


# Ruta para el administrador
@admin_routes.route('/admin/')
def admin():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MySQL
        admin = get_admin(email)
        if admin:
            return render_template('admin.html', admin=admin)
    else:
        return redirect(url_for('main.index'))


# Ruta para registrar
@admin_routes.route('/admin/registro/')
def registro():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MySQL
        admin = get_admin(email)
        if admin:
            return render_template('registro.html')
    else:
        return redirect(url_for('main.login'))


# Ruta para registrar a los usuarios
@admin_routes.route('/register_user/', methods=['POST', 'GET'])
def register_user():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MySQL
        admin = get_admin(email)
        if admin:
            if request.method == 'POST':
                cursor = connection.cursor()
                try:
                    existing_user = request.form['email']
                    name = request.form['name']
                    email = request.form['email']
                    password = request.form['password']
                    phone = request.form['phone']

                    # Verificar si el Usuario ya existe en la base de datos
                    cursor.execute(
                        "SELECT * FROM user WHERE email = %s", (email,))
                    existing_user = cursor.fetchone()

                    if existing_user is None:
                        # Hash de la contraseña
                        hashpass = bcrypt.hashpw(
                            password.encode('utf-8'), bcrypt.gensalt())

                        # Insertar el nuevo Usuario en la base de datos
                        cursor.execute(
                            "INSERT INTO user (name, email, password, phone) VALUES (%s, %s, %s, %s)", (name, email, hashpass, phone))
                        connection.commit()

                        flash('Se registró el Usuario correctamente')
                        return redirect(url_for('admin.registro'))
                    else:
                        flash('El correo ya está en uso')
                        return redirect(url_for('admin.registro'))
                except mysql.connector.Error as err:
                    print("Error al registrar Usuario:", err)
                    connection.rollback()
                finally:
                    cursor.close()
        else:
            return redirect(url_for('main.login'))

    return redirect(url_for('admin.registro'))


# Ruta para registrar administradores
@admin_routes.route('/register_admin/', methods=['POST', 'GET'])
def register_admin():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MySQL
        admin = get_admin(email)
        if admin:
            if request.method == 'POST':
                cursor = connection.cursor()
                try:
                    existing_admin = request.form['email']
                    name = request.form['name']
                    email = request.form['email']
                    password = request.form['password']
                    phone = request.form['phone']

                    # Verificar si el administrador ya existe en la base de datos
                    cursor.execute(
                        "SELECT * FROM admin WHERE email = %s", (email,))
                    existing_admin = cursor.fetchone()

                    if existing_admin is None:
                        # Hash de la contraseña
                        hashpass = bcrypt.hashpw(
                            password.encode('utf-8'), bcrypt.gensalt())

                        # Insertar el nuevo administrador en la base de datos
                        cursor.execute(
                            "INSERT INTO admin (name, email, password, phone) VALUES (%s, %s, %s, %s)", (name, email, hashpass, phone))
                        connection.commit()

                        flash('Se registró el administrador correctamente')
                        return redirect(url_for('admin.registro'))
                    else:
                        flash('El correo ya está en uso')
                        return redirect(url_for('admin.registro'))
                except mysql.connector.Error as err:
                    print("Error al registrar administrador:", err)
                    connection.rollback()
                finally:
                    cursor.close()
        else:
            return redirect(url_for('main.login'))

    return redirect(url_for('admin.registro'))


# Ruta para ver Usuarios
@admin_routes.route('/admin/listas/usuarios/')
def users():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MySQL
        admin = get_admin(email)
        if admin:
            return render_template('users.html')
    else:
        return redirect(url_for('main.login'))
    

# Ruta para ver Administradores
@admin_routes.route('/admin/listas/administradores/')
def admins():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MySQL
        admin = get_admin(email)
        if admin:
            return render_template('admins.html')
    else:
        return redirect(url_for('main.login'))