from flask import Blueprint, render_template, url_for, redirect, session, request, flash, current_app
from func.func import get_user, obtener_areas
from database.database import dbConnection
import mysql.connector
from datetime import datetime


user_routes = Blueprint('user', __name__)
# Obtener la conexión a la base de datos
db = dbConnection()


# Ruta para inicio de usuarios
@user_routes.route('/user/')
def user():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde la d
        user = get_user(email)
        if user:
            return render_template('user.html', user=user)
    else:
        return redirect(url_for('main.index'))
        
    
@user_routes.route('/area/')
def area():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde bd
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
                    with db.cursor() as cursor:
                        # Verificar si el área ya existe en la base de datos para este usuario
                        cursor.execute(
                            "SELECT * FROM Areas WHERE NombreArea = %s AND id = %s",
                            (nombre_area, user['id'])
                        )
                        existearea = cursor.fetchone()

                        if existearea is None:
                            sql = "INSERT INTO Areas (NombreArea, id) VALUES (%s, %s)"
                            cursor.execute(sql, (nombre_area, user['id']))
                            db.commit()
                            flash('Se registró el área correctamente')
                        else:
                            flash('El área ya existe')
                        return redirect(url_for('user.area'))
                except mysql.connector.Error as err:
                    print("Error al registrar área:", err)
                    db.rollback()
        else:
            return redirect(url_for('main.index'))
    return redirect(url_for('user.area'))


#Función para obtener las áreas del usuario disponibles desde la base de datos.
def obtener_areas(usuario_id):
    """Función para obtener las áreas del usuario disponibles desde la base de datos."""
    try:
        cursor = db.cursor()
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

# Ruta para ingresar un departamento en un área
@user_routes.route('/departamento/', methods=['GET', 'POST'])
def departamento():
   if 'email' in session:
        email = session['email']
        user = get_user(email)  # Función para obtener detalles del usuario desde desde bd

        if user:
            if request.method == 'POST':
                nombre_departamento = request.form['nombre_departamento']
                id_area = request.form['id_area']  # Id del área al que pertenece
                try:
                    with db.cursor() as cursor:
                        # Verificar si el departamento ya existe en la misma área
                        cursor.execute("""
                            SELECT * FROM Departamento 
                            WHERE NombreDepartamento = %s AND IdArea = %s AND id = %s
                        """, (nombre_departamento, id_area, user['id']))
                        existedepto = cursor.fetchone()

                        if existedepto is None:
                            # Insertar el departamento en la base de datos
                            sql = "INSERT INTO Departamento (NombreDepartamento, IdArea, id) VALUES (%s, %s, %s)"
                            cursor.execute(sql, (nombre_departamento, id_area, user['id']))
                            db.commit()
                            flash('Se registró el departamento correctamente', 'success')
                        else:
                            flash('El departamento ya existe en esta área', 'warning')

                        return redirect(url_for('user.departamento'))

                except mysql.connector.Error as err:
                    print("Error al registrar departamento:", err)
                    db.rollback()
            usuario_id = user['id']

            # Obtener áreas disponibles utilizando la función obtener_areas()
            areas = obtener_areas(usuario_id)

            return render_template('departamento.html', areas=areas, user=user)
        else:
            return redirect(url_for('main.index'))  # Redirigir si no hay sesión
        

def obtener_departamentos(usuario_id):
    """Función para obtener los departamentos del usuario disponibles desde la base de datos."""
    try:
        cursor = db.cursor()
        query = """
        SELECT IdDepartamento, NombreDepartamento
        FROM Departamento
        WHERE id = %s
        """
        cursor.execute(query, (usuario_id,))
        departamentos = cursor.fetchall()
        print("Departamentos obtenidos:", departamentos)  # Debug
        return departamentos
    except mysql.connector.Error as err:
        print(f"Error al obtener departamentos desde la base de datos: {err}")
        return []
    
def obtener_puestos(usuario_id):
    """Función para obtener los puestos del usuario disponibles desde la base de datos."""
    try:
        cursor = db.cursor()
        query = """
        SELECT IdPuesto, NombrePuesto
        FROM puestos
        WHERE DepartamentoId IN (
            SELECT IdDepartamento
            FROM departamento
            WHERE id = %s
        )
        """
        cursor.execute(query, (usuario_id,))
        puestos = cursor.fetchall()
        print("Puestos obtenidos:", puestos)  # Debug
        return puestos
    except mysql.connector.Error as err:
        print(f"Error al obtener puestos desde la base de datos: {err}")
        return []
    
        
@user_routes.route('/puesto/', methods=['GET', 'POST'])
def puesto():
    if 'email' not in session:
        return redirect(url_for('main.index'))
    
    email = session['email']
    user = get_user(email)
    if not user:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # Obtener datos del formulario
        nombre_puesto = request.form.get('nombre_puesto')
        id_departamento = request.form.get('id_departamento')
        jefe = request.form.get('jefe')
        clave = request.form.get('clave')
        no_plazas = request.form.get('no_plazas')
        objetivo = request.form.get('objetivo')
        funciones = request.form.get('funciones')
        reemplaza = request.form.get('reemplaza')
        reemplazado = request.form.get('reemplazado')
        equipo_trabajo = request.form.get('equipo_trabajo')
        fecha = request.form.get('fecha')
        nombre_relacion = request.form.get('nombre_relacion')
        objetivo_relacion = request.form.get('objetivo_relacion')
        edad = request.form.get('edad')
        sexo = request.form.get('sexo')
        estado_civil = request.form.get('estado_civil')
        experiencia = request.form.get('experiencia')
        escolaridad = request.form.get('escolaridad')
        conocimientos = request.form.get('conocimientos')
        esfuerzo_fisico = request.form.get('esfuerzo_fisico')
        esfuerzo_mental = request.form.get('esfuerzo_mental')
        riesgo_accidente = request.form.get('riesgo_accidente')
        ambiente = request.form.get('ambiente')
        responsabilidad = request.form.get('responsabilidad')
        compromiso = request.form.get('compromiso')
        empatia = request.form.get('empatia')
        trabajo_equipo = request.form.get('trabajo_equipo')
        energia = request.form.get('energia')
        
        # Validaciones básicas de los campos del formulario
        if not nombre_puesto or not id_departamento:
            flash('El nombre del puesto y el departamento son obligatorios', 'warning')
            return redirect(request.url)

        try:
            with db.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM Puestos 
                    WHERE NombrePuesto = %s AND DepartamentoId = %s
                """, (nombre_puesto, id_departamento))
                existepuesto = cursor.fetchone()

                if existepuesto is None:
                    # Inserción del puesto
                    sql_puesto = """
                    INSERT INTO Puestos 
                    (NombrePuesto, DepartamentoId, Jefe, Clave, NoPlazas, Objetivo, FuncionesEspecificas, EquipoTrabajo, Fecha, Reemplazar, Reemplazado, id) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_puesto, (
                        nombre_puesto, id_departamento, jefe, clave, no_plazas, objetivo, funciones, equipo_trabajo, fecha, reemplaza, reemplazado, user['id']
                    ))
                    id_puesto = cursor.lastrowid

                    # Inserción del perfil del puesto
                    sql_perfil = """
                    INSERT INTO PerfilPuesto 
                    (Edad, Sexo, EstadoCivil, Experiencia, Escolaridad, ConocimientosEspecificos, IdPuesto) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_perfil, (
                        edad, sexo, estado_civil, experiencia, escolaridad, conocimientos, id_puesto
                    ))
                    id_perfil = cursor.lastrowid

                    # Inserción de relaciones
                    sql_relaciones = """
                    INSERT INTO Relaciones 
                    (Nombre, Objetivo, IdPuesto)
                    VALUES (%s, %s, %s)
                    """
                    cursor.execute(sql_relaciones, (
                        nombre_relacion, objetivo_relacion, id_puesto
                    ))

                    # Inserción de condiciones de trabajo
                    sql_condiciones = """
                    INSERT INTO CondicionesTrabajo
                    (EsfuerzoFisico, EsfuerzoMental, RiesgoAccidente, Ambiente, IdPerfil)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_condiciones, (
                        esfuerzo_fisico, esfuerzo_mental, riesgo_accidente, ambiente, id_perfil
                    ))

                    # Inserción de competencias
                    sql_competencias = """
                    INSERT INTO Competencias
                    (Responsabilidad, Compromiso, Empatia, TrabajoEquipo, Energia, IdPerfil)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_competencias, (
                        responsabilidad, compromiso, empatia, trabajo_equipo, energia, id_perfil
                    ))

                    db.commit()
                    flash('Se registró el puesto correctamente', 'success')
                else:
                    flash('El puesto ya existe en este departamento', 'warning')

        except mysql.connector.Error as err:
            flash(f'Error al registrar puesto: {err}', 'danger')
            db.rollback()

        return redirect(url_for('user.puesto'))

    usuario_id = user['id']
    departamentos = obtener_departamentos(usuario_id)
    puestos = obtener_puestos(usuario_id)

    return render_template('puesto.html', departamentos=departamentos, puestos=puestos, user=user)

    
    
#Ruta para ver áreas y departamentos  
@user_routes.route('/areas/', methods=['GET', 'POST'])
def areas():
    insertObjeto = []
    cursor = None

    try:
        if 'email' in session:
            email = session['email']
            user = get_user(email)  # Función para obtener detalles del usuario desde la base de datos

            if user:
                cursor = db.cursor()
                cursor.execute("""
                    SELECT Areas.IdArea, Areas.NombreArea, GROUP_CONCAT(Departamento.NombreDepartamento ORDER BY Departamento.NombreDepartamento SEPARATOR ', ') AS Departamentos
                    FROM Areas
                    LEFT JOIN Departamento ON Departamento.IdArea = Areas.IdArea
                    WHERE Areas.id = %s  
                    GROUP BY Areas.IdArea;
                """, (user['id'],))
                datosDB = cursor.fetchall()
                columName = [column[0] for column in cursor.description]
                for registro in datosDB:
                    insertObjeto.append(dict(zip(columName, registro)))

    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
        return "Error en la consulta a la base de datos", 500

    finally:
        if cursor is not None:
            cursor.close()  # Asegúrate de cerrar el cursor

    return render_template("mostrar.html", data=insertObjeto)

#Ruta para eliminar áreas.
@user_routes.route('/eliminar_area/<int:IdArea>/')
def eliminar_area(IdArea):
    cursor = db.cursor()
    try:
         #Eliminar condiciones de trabajo de perfiles relacionados con el área
        cursor.execute("""
            DELETE FROM CondicionesTrabajo 
            WHERE IdPerfil IN (SELECT IdPerfil 
                               FROM PerfilPuesto 
                               WHERE IdPuesto IN (SELECT IdPuesto 
                                                  FROM Puestos 
                                                  WHERE DepartamentoId IN (SELECT IdDepartamento 
                                                                           FROM Departamento 
                                                                           WHERE IdArea = %s)))
        """, (IdArea,))
        #Eliminar competencias de perfiles relacionados con el área
        cursor.execute("""
            DELETE FROM Competencias 
            WHERE IdPerfil IN (SELECT IdPerfil 
                               FROM PerfilPuesto 
                               WHERE IdPuesto IN (SELECT IdPuesto 
                                                  FROM Puestos 
                                                  WHERE DepartamentoId IN (SELECT IdDepartamento 
                                                                           FROM Departamento 
                                                                           WHERE IdArea = %s)))
        """, (IdArea,))
        #Eliminar perfiles de puesto relacionados con el área
        cursor.execute("DELETE FROM PerfilPuesto WHERE IdPuesto IN (SELECT IdPuesto FROM Puestos WHERE DepartamentoId IN (SELECT IdDepartamento FROM Departamento WHERE IdArea = %s))", (IdArea,))
        # Eliminar puestos relacionados con el área
        cursor.execute("DELETE FROM Puestos WHERE DepartamentoId IN (SELECT IdDepartamento FROM Departamento WHERE IdArea = %s)", (IdArea,))
        # Eliminar departamentos relacionados con el área
        cursor.execute("DELETE FROM Departamento WHERE IdArea = %s", (IdArea,))
        # Luego eliminar el área
        cursor.execute("DELETE FROM Areas WHERE IdArea = %s", (IdArea,))
        db.commit()
        flash('Área eliminada correctamente', 'success')
    except mysql.connector.Error as err:
        print("Error al eliminar area:", err)
        db.rollback()
        flash('Error al eliminar area', 'error')
    finally:
        cursor.close()
    return redirect(url_for('user.areas'))
