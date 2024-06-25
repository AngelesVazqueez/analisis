from flask import Blueprint, render_template, url_for, redirect, session, request, flash
from func.func import get_user, obtener_areas
import database.database as dbase
import mysql.connector


user_routes = Blueprint('user', __name__)
# Obtener la conexión a la base de datos
connection = dbase.dbConnection()

# Ruta para inicio de usuarios
@user_routes.route('/user/')
def user():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MongoDB
        user = get_user(email)
        if user:
            return render_template('user.html', user=user)
    else:
        return redirect(url_for('main.index'))
        
    
@user_routes.route('/area/')
def area():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MongoDB
        user = get_user(email)
        if user:
            return render_template('area.html')
    else:
        return redirect(url_for('main.index'))
    

    
@user_routes.route('/RegistrarArea/', methods=['GET', 'POST'])
def RegistrarArea():
    if 'email' in session:
        email = session['email']
        user = get_user(email)
        if user:
            if request.method == 'POST':
                nombre_area = request.form['nombre_area']
                try:
                    with connection.cursor() as cursor:
                        # Verificar si el area ya existe en la base de datos
                        cursor.execute("SELECT * FROM Areas WHERE NombreArea = %s", (nombre_area,))
                        existearea = cursor.fetchone()

                        if existearea is None:
                            sql = "INSERT INTO Areas (NombreArea) VALUES (%s)"
                            cursor.execute(sql, (nombre_area,))
                            connection.commit()
                            flash('Se registró el área correctamente')
                        else:
                            flash('El área ya existe')
                        return redirect(url_for('user.area'))
                except mysql.connector.Error as err:
                    print("Error al registrar área:", err)
                    cursor.rollback()
                finally:
                    cursor.close() 
        else:
            return redirect(url_for('main.index'))
    return redirect(url_for('user.area'))


# Ruta para ingresar un departamento en un área
@user_routes.route('/departamento/', methods=['GET', 'POST'])
def departamento():
   if 'email' in session:
        email = session['email']
        user = get_user(email)  # Función para obtener detalles del usuario desde MongoDB

        if user:
            if request.method == 'POST':
                nombre_departamento = request.form['nombre_departamento']
                id_area = request.form['id_area']  # Id del área al que pertenece

                try:
                    with connection.cursor() as cursor:
                        # Verificar si el departamento ya existe en la misma área
                        cursor.execute("""
                            SELECT * FROM Departamento 
                            WHERE NombreDepartamento = %s AND IdArea = %s
                        """, (nombre_departamento, id_area))
                        existedepto = cursor.fetchone()

                        if existedepto is None:
                            # Insertar el departamento en la base de datos
                            sql = "INSERT INTO Departamento (NombreDepartamento, IdArea) VALUES (%s, %s)"
                            cursor.execute(sql, (nombre_departamento, id_area))
                            connection.commit()
                            flash('Se registró el departamento correctamente', 'success')
                        else:
                            flash('El departamento ya existe en esta área', 'warning')

                        return redirect(url_for('user.departamento'))

                except mysql.connector.Error as err:
                    print("Error al registrar departamento:", err)
                    connection.rollback()
                finally:
                    # Cerrar conexión con la base de datos
                    cursor.close()

            # Obtener áreas disponibles utilizando la función obtener_areas()
            areas = obtener_areas()

            return render_template('departamento.html', areas=areas, user=user)
        else:
            return redirect(url_for('main.index'))  # Redirigir si no hay sesión
        
@user_routes.route('/puesto/', methods=['GET', 'POST'])
def puesto():
   if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MongoDB
        user = get_user(email)
        if user:
            return render_template('puesto.html')
        else:
            return redirect(url_for('main.index'))
    