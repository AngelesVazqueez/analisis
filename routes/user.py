from flask import Blueprint, render_template, url_for, redirect, session, request, flash, make_response, jsonify
from func.func import obtener_areas
from database.database import dbConnection
import mysql.connector
from bson.binary import Binary
import base64
from io import BytesIO
from xhtml2pdf import pisa
import bcrypt

user_routes = Blueprint('user', __name__)
# Obtener la conexión a la base de datos
db = dbConnection()


def get_user(email):
    if db:
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
            user = cursor.fetchone()
            return user
        except mysql.connector.Error as err:
            print("Error al obtener usuario:", err)
    return None


@user_routes.route('/login/', methods=['POST'])
def iniciar():
    connection = mysql.connector.connect(
        host='sql5.freemysqlhosting.net',
        user='sql5720463',
        password='EUTLx1IP9A',
        database='sql5720463'
    )
    cursor = connection.cursor(dictionary=True)
    try:
        email = request.form['email']
        password = request.form['password']

        # Buscar en la tabla de admin
        cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
        login_admin = cursor.fetchone()
        if login_admin and bcrypt.checkpw(password.encode('utf-8'), login_admin['password']):
            session['email'] = email
            return redirect(url_for('admin.admin'))

        # Buscar en la tabla de users
        cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
        login_user = cursor.fetchone()
        if login_user and bcrypt.checkpw(password.encode('utf-8'), login_user['password']):
            session['email'] = email
            return redirect(url_for('user.user'))

        flash('Correo o contraseña incorrectos')
        return redirect(url_for('main.index'))
    except mysql.connector.Error as err:
        print("Error al iniciar sesión:", err)
        flash('Hubo un error al iniciar sesión. Inténtalo de nuevo.')
        return redirect(url_for('main.index'))
    finally:
        cursor.close()


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


@user_routes.route('/user/area/')
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
                            "SELECT * FROM areas WHERE NombreArea = %s AND id = %s",
                            (nombre_area, user['id'])
                        )
                        existearea = cursor.fetchone()

                        if existearea is None:
                            sql = "INSERT INTO areas (NombreArea, id) VALUES (%s, %s)"
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


# Función para obtener las áreas del usuario disponibles desde la base de datos.
def obtener_areas(usuario_id):
    """Función para obtener las áreas del usuario disponibles desde la base de datos."""
    try:
        cursor = db.cursor()
        query = """
        SELECT IdArea, NombreArea
        FROM areas
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
        # Función para obtener detalles del usuario desde desde bd
        user = get_user(email)

        if user:
            if request.method == 'POST':
                nombre_departamento = request.form['nombre_departamento']
                # Id del área al que pertenece
                id_area = request.form['id_area']
                try:
                    with db.cursor() as cursor:
                        # Verificar si el departamento ya existe en la misma área
                        cursor.execute("""
                            SELECT * FROM departamento 
                            WHERE NombreDepartamento = %s AND IdArea = %s AND id = %s
                        """, (nombre_departamento, id_area, user['id']))
                        existedepto = cursor.fetchone()

                        if existedepto is None:
                            # Insertar el departamento en la base de datos
                            sql = "INSERT INTO departamento (NombreDepartamento, IdArea, id) VALUES (%s, %s, %s)"
                            cursor.execute(
                                sql, (nombre_departamento, id_area, user['id']))
                            db.commit()
                            flash(
                                'Se registró el departamento correctamente', 'success')
                        else:
                            flash(
                                'El departamento ya existe en esta área', 'warning')

                        return redirect(url_for('user.departamento'))

                except mysql.connector.Error as err:
                    print("Error al registrar departamento:", err)
                    db.rollback()
            usuario_id = user['id']

            # Obtener áreas disponibles utilizando la función obtener_areas()
            areas = obtener_areas(usuario_id)

            return render_template('departamento.html', areas=areas, user=user)
        else:
            # Redirigir si no hay sesión
            return redirect(url_for('main.index'))


def obtener_departamentos(usuario_id):
    """Función para obtener los departamentos del usuario disponibles desde la base de datos."""
    try:
        cursor = db.cursor()
        query = """
        SELECT IdDepartamento, NombreDepartamento
        FROM departamento
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
        reemplaza = request.form.get('reemplaza')
        reemplazado = request.form.get('reemplazado')
        nota = request.form.get('nota')

        equipo_trabajo = request.form.get(
            'equipo_trabajo')  # Captura del campo funciones
        equipo_lista = [r.strip() for r in equipo_trabajo.split(
            ',')] if equipo_trabajo else []  # Convertir a lista
        equipo_str = ','.join(equipo_lista)  # Convertir a cadena

        fecha = request.form.get('fecha')

        # Captura del campo Relaciones
        relaciones = request.form.get('Relaciones')
        relaciones_lista = [r.strip() for r in relaciones.split(
            '.')] if relaciones else []  # Convertir a lista
        relaciones_str = '.'.join(relaciones_lista)  # Convertir a cadena

        # Captura del campo funciones
        funciones = request.form.get('Funciones')
        funciones_lista = [r.strip() for r in funciones.split(
            '.')] if funciones else []  # Convertir a lista
        funciones_str = '.'.join(funciones_lista)  # Convertir a cadena

        edad = request.form.get('edad')
        sexo = request.form.get('sexo')
        estado_civil = request.form.get('estado_civil')
        experiencia = request.form.get('experiencia')
        escolaridad = request.form.get('escolaridad')

        # Captura del campo conocimientos
        conocimientos = request.form.get('conocimientos')
        conocimientos_lista = [r.strip() for r in conocimientos.split(
            ',')] if conocimientos else []  # Convertir a lista
        conocimientos_str = ','.join(conocimientos_lista)  # Convertir a cadena

        esfuerzo_fisico = request.form.get('esfuerzo_fisico')
        esfuerzo_mental = request.form.get('esfuerzo_mental')
        riesgo_accidente = request.form.get('riesgo_accidente')
        ambiente = request.form.get('ambiente')
        responsabilidad = request.form.get('responsabilidad')
        compromiso = request.form.get('compromiso')
        empatia = request.form.get('empatia')
        trabajo_equipo = request.form.get('trabajo_equipo')
        energia = request.form.get('energia')
        ubicacion = request.files.get('ubicacion')

        # Validaciones básicas de los campos del formulario
        if not nombre_puesto or not id_departamento:
            flash('El nombre del puesto y el departamento son obligatorios', 'warning')
            return redirect(request.url)

        try:
            with db.cursor() as cursor:
                # Verificar si el puesto ya existe en este departamento para este usuario
                cursor.execute("""
                    SELECT * FROM puestos 
                    WHERE NombrePuesto = %s AND DepartamentoId = %s AND id = %s
                """, (nombre_puesto, id_departamento, user['id']))
                existe_puesto = cursor.fetchone()

                if not existe_puesto:
                    # Comenzar transacción
                    cursor.execute("START TRANSACTION")

                    # Insertar el puesto
                    sql_puesto = """
                    INSERT INTO puestos 
                    (NombrePuesto, DepartamentoId, Jefe, Clave, NoPlazas, Objetivo, FuncionesEspecificas, EquipoTrabajo, Fecha, Reemplazar, Reemplazado, Ubicacion, id, Relaciones, Nota) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_puesto, (
                        nombre_puesto, id_departamento, jefe, clave, no_plazas, objetivo, funciones_str, equipo_str, fecha, reemplaza, reemplazado, ubicacion.read(
                        ) if ubicacion else None, user['id'], relaciones_str, nota
                    ))
                    id_puesto = cursor.lastrowid

                    # Insertar el perfil del puesto
                    sql_perfil = """
                    INSERT INTO perfilpuesto 
                    (Edad, Sexo, EstadoCivil, Experiencia, Escolaridad, ConocimientosEspecificos, IdPuesto) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_perfil, (
                        edad, sexo, estado_civil, experiencia, escolaridad, conocimientos_str, id_puesto
                    ))
                    id_perfil = cursor.lastrowid

                    # Insertar condiciones de trabajo
                    sql_condiciones = """
                    INSERT INTO condicionestrabajo
                    (EsfuerzoFisico, EsfuerzoMental, RiesgoAccidente, Ambiente, IdPerfil)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_condiciones, (
                        esfuerzo_fisico, esfuerzo_mental, riesgo_accidente, ambiente, id_perfil
                    ))

                    # Insertar competencias
                    sql_competencias = """
                    INSERT INTO competencias
                    (Responsabilidad, Compromiso, Empatia, TrabajoEquipo, Energia, IdPerfil)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_competencias, (
                        responsabilidad, compromiso, empatia, trabajo_equipo, energia, id_perfil
                    ))

                    # Confirmar transacción
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


@user_routes.route('/api/puestos/<int:departamento_id>', methods=['GET'])
def obtener_puestos_por_departamento(departamento_id):
    try:
        with db.cursor() as cursor:
            # Consulta para obtener los puestos por departamento
            cursor.execute("""
                SELECT id, NombrePuesto FROM puestos
                WHERE DepartamentoId = %s
            """, (departamento_id,))
            puestos = cursor.fetchall()

            # Formatear los resultados para devolverlos como JSON
            puestos_json = [{'id': puesto[0], 'nombre': puesto[1]}
                            for puesto in puestos]

            return jsonify(puestos_json)

    except mysql.connector.Error as err:
        # Manejo de errores
        return jsonify({'error': f'Error al obtener puestos por departamento: {err}'}), 500


@user_routes.route('/pdf/<int:IdPuesto>')
def pdf(IdPuesto):
    try:
        # Recuperar datos del usuario desde la base de datos
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
                        SELECT 
                    p1.IdPuesto, 
                    p1.NombrePuesto, 
                    p1.Departamento, 
                    p1.Jefe, 
                    p1.Clave, 
                    p1.NoPlazas, 
                    p1.Objetivo, 
                    p1.Ubicacion, 
                    p1.FuncionesEspecificas, 
                    p1.EquipoTrabajo, 
                    p1.Fecha, 
                    p1.Reemplazar, 
                    p1.Reemplazado, 
                    p1.Relaciones,
                    p1.Nota,
                    perfilpuesto.Edad, 
                    perfilpuesto.Sexo, 
                    perfilpuesto.EstadoCivil, 
                    perfilpuesto.Experiencia,
                    perfilpuesto.Escolaridad, 
                    perfilpuesto.ConocimientosEspecificos,
                    condicionestrabajo.EsfuerzoFisico, 
                    condicionestrabajo.EsfuerzoMental, 
                    condicionestrabajo.RiesgoAccidente, 
                    condicionestrabajo.Ambiente,
                    competencias.Responsabilidad, 
                    competencias.Compromiso, 
                    competencias.Empatia, 
                    competencias.TrabajoEquipo,
                    competencias.Energia,
                    departamento.NombreDepartamento, 
                    areas.NombreArea
                FROM 
                    puestos p1
                LEFT JOIN 
                    perfilpuesto ON perfilpuesto.IdPuesto = p1.IdPuesto
                LEFT JOIN 
                    condicionestrabajo ON condicionestrabajo.IdPerfil = perfilpuesto.Idperfil
                LEFT JOIN 
                    competencias ON competencias.IdPerfil = perfilpuesto.Idperfil
                LEFT JOIN 
                    departamento ON p1.DepartamentoId = departamento.IdDepartamento
                LEFT JOIN 
                    areas ON departamento.IdArea = areas.IdArea
                WHERE 
                    p1.IdPuesto = %s;
                    """, (IdPuesto,))
        puesto = cursor.fetchone()

        if puesto and 'Ubicacion' in puesto:
            ubicacion_bin = puesto['Ubicacion']
            if ubicacion_bin:
                # Convertir la ubicación binaria a base64
                puesto['Ubicacion'] = base64.b64encode(
                    ubicacion_bin).decode('utf-8')

        # Convertir el campo Relaciones a una lista
                if puesto['Relaciones']:
                    puesto['Relaciones'] = puesto['Relaciones'].split('.')

        # Convertir el campo FuncionesEspecificas a una lista
                if puesto['FuncionesEspecificas']:
                    puesto['FuncionesEspecificas'] = puesto['FuncionesEspecificas'].split(
                        '.')

        # Convertir el campo EquipoTrabajo a una lista
                if puesto['EquipoTrabajo']:
                    puesto['EquipoTrabajo'] = puesto['EquipoTrabajo'].split(
                        ',')

        # Convertir el campo ConocimientosEspecificos a una lista
                if puesto['ConocimientosEspecificos']:
                    puesto['ConocimientosEspecificos'] = puesto['ConocimientosEspecificos'].split(
                        ',')

        cursor.close()

        if not puesto:
            return "Puesto no encontrado", 404

        # Renderizar la plantilla HTML con los datos del usuario
        rendered = render_template('pdf_template.html', puesto=puesto)

        # Convertir la plantilla HTML a PDF
        pdf = convert_html_to_pdf(rendered)

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=user_{}.pdf'.format(
            IdPuesto)
        return response

    except mysql.connector.Error as err:
        print(f"Error al obtener el puesto de la base de datos: {err}")
        return "Error en la consulta a la base de datos", 500


def convert_html_to_pdf(source_html):
    # Convertir HTML a PDF usando xhtml2pdf
    output = BytesIO()
    pisa_status = pisa.CreatePDF(source_html, dest=output)
    return output.getvalue() if not pisa_status.err else None

# Ruta para ver áreas y departamentos


@user_routes.route('/areas/', methods=['GET', 'POST'])
def areas():
    insertObjeto = []
    cursor = None

    try:
        if 'email' in session:
            email = session['email']
            # Función para obtener detalles del usuario desde la base de datos
            user = get_user(email)

            if user:
                cursor = db.cursor()
                cursor.execute("""
                    SELECT areas.IdArea, areas.NombreArea, GROUP_CONCAT(departamento.NombreDepartamento ORDER BY departamento.NombreDepartamento SEPARATOR ', ') AS Departamentos
                    FROM areas
                    LEFT JOIN departamento ON departamento.IdArea = areas.IdArea
                    WHERE areas.id = %s  
                    GROUP BY areas.IdArea;
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


# Ruta para eliminar áreas.
@user_routes.route('/eliminar_area/<int:IdArea>/')
def eliminar_area(IdArea):
    cursor = db.cursor()
    try:
        # Eliminar condiciones de trabajo de perfiles relacionados con el área
        cursor.execute("""
            DELETE FROM condicionestrabajo 
            WHERE IdPerfil IN (SELECT IdPerfil 
                               FROM perfilpuesto 
                               WHERE IdPuesto IN (SELECT IdPuesto 
                                                  FROM puestos 
                                                  WHERE DepartamentoId IN (SELECT IdDepartamento 
                                                                           FROM departamento 
                                                                           WHERE IdArea = %s)))
        """, (IdArea,))
        # Eliminar competencias de perfiles relacionados con el área
        cursor.execute("""
            DELETE FROM competencias 
            WHERE IdPerfil IN (SELECT IdPerfil 
                               FROM perfilpuesto 
                               WHERE IdPuesto IN (SELECT IdPuesto 
                                                  FROM puestos 
                                                  WHERE DepartamentoId IN (SELECT IdDepartamento 
                                                                           FROM departamento 
                                                                           WHERE IdArea = %s)))
        """, (IdArea,))
        # Eliminar perfiles de puesto relacionados con el área
        cursor.execute("DELETE FROM perfilpuesto WHERE IdPuesto IN (SELECT IdPuesto FROM puestos WHERE DepartamentoId IN (SELECT IdDepartamento FROM departamento WHERE IdArea = %s))", (IdArea,))
        # Eliminar puestos relacionados con el área
        cursor.execute(
            "DELETE FROM puestos WHERE DepartamentoId IN (SELECT IdDepartamento FROM departamento WHERE IdArea = %s)", (IdArea,))
        # Eliminar departamentos relacionados con el área
        cursor.execute("DELETE FROM departamento WHERE IdArea = %s", (IdArea,))
        # Luego eliminar el área
        cursor.execute("DELETE FROM areas WHERE IdArea = %s", (IdArea,))
        db.commit()
        flash('Área eliminada correctamente', 'success')
    except mysql.connector.Error as err:
        print("Error al eliminar area:", err)
        db.rollback()
        flash('Error al eliminar area', 'error')
    finally:
        cursor.close()
    return redirect(url_for('user.areas'))


@user_routes.route('/mostrarDepartamentos/', methods=['GET', 'POST'])
def mostrarDepartamentos():
    insertObjeto = []
    cursor = None

    try:
        if 'email' in session:
            email = session['email']
            # Función para obtener detalles del usuario desde la base de datos
            user = get_user(email)

            if user:
                cursor = db.cursor()
                cursor.execute("""
                    SELECT departamento.IdDepartamento, departamento.NombreDepartamento, areas.NombreArea, 
                           GROUP_CONCAT(puestos.NombrePuesto ORDER BY puestos.NombrePuesto SEPARATOR ', ') AS Puestos
                    FROM departamento
                    LEFT JOIN areas ON departamento.IdArea = areas.IdArea
                    LEFT JOIN puestos ON puestos.DepartamentoId = departamento.IdDepartamento
                    WHERE areas.id = %s
                    GROUP BY departamento.IdDepartamento;
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

    areas = obtener_areas(user['id'],)
    return render_template("departamentos.html", data=insertObjeto, areas=areas)


# Ruta para eliminar departamentos.
@user_routes.route('/eliminar_depa/<int:IdDepartamento>/')
def eliminar_depa(IdDepartamento):
    cursor = db.cursor()
    try:
        # Eliminar condiciones de trabajo de perfiles relacionados con el departamento
        cursor.execute("""
            DELETE FROM condicionestrabajo 
            WHERE IdPerfil IN (SELECT IdPerfil 
                               FROM perfilpuesto 
                               WHERE IdPuesto IN (SELECT IdPuesto 
                                                  FROM puestos 
                                                  WHERE DepartamentoId IN (SELECT IdDepartamento 
                                                                           FROM departamento 
                                                                           WHERE IdDepartamento = %s)))
        """, (IdDepartamento,))
        # Eliminar competencias de perfiles relacionados con el departamento
        cursor.execute("""
            DELETE FROM competencias 
            WHERE IdPerfil IN (SELECT IdPerfil 
                               FROM perfilpuesto 
                               WHERE IdPuesto IN (SELECT IdPuesto 
                                                  FROM puestos 
                                                  WHERE DepartamentoId IN (SELECT IdDepartamento 
                                                                           FROM departamento 
                                                                           WHERE IdDepartamento = %s)))
        """, (IdDepartamento,))
        # Eliminar perfiles de puesto relacionados con el departamento
        cursor.execute("DELETE FROM perfilpuesto WHERE IdPuesto IN (SELECT IdPuesto FROM puestos WHERE DepartamentoId IN (SELECT IdDepartamento FROM departamento WHERE IdDepartamento = %s))", (IdDepartamento,))
        # Eliminar puestos relacionados con el departamento
        cursor.execute(
            "DELETE FROM puestos WHERE DepartamentoId IN (SELECT IdDepartamento FROM departamento WHERE IdDepartamento = %s)", (IdDepartamento,))
        # Eliminar departamentos relacionados con el área
        cursor.execute(
            "DELETE FROM departamento WHERE IdDepartamento = %s", (IdDepartamento,))
        db.commit()
        flash('Departamento eliminado correctamente', 'success')
    except mysql.connector.Error as err:
        print("Error al eliminar departamento:", err)
        db.rollback()
        flash('Error al eliminar departamento', 'error')
    finally:
        cursor.close()
    return redirect(url_for('user.mostrarDepartamentos'))


@user_routes.route('/mostrarPuestos/', methods=['GET'])
def mostrarPuestos():
    puestos_completos = []
    cursor = None

    try:
        if 'email' in session:
            email = session['email']
            user = get_user(email)

            if user:
                cursor = db.cursor()
                query = """
                SELECT 
                    p1.IdPuesto, 
                    p1.NombrePuesto, 
                    p1.Departamento, 
                    p1.DepartamentoId,
                    p1.Jefe, 
                    p1.Clave, 
                    p1.NoPlazas, 
                    p1.Objetivo, 
                    p1.Ubicacion, 
                    p1.FuncionesEspecificas, 
                    p1.EquipoTrabajo, 
                    p1.Fecha, 
                    p1.Reemplazar, 
                    p1.Reemplazado,
                    p1.Nota, 
                    p1.Relaciones,
                    perfilpuesto.Edad, 
                    perfilpuesto.Sexo, 
                    perfilpuesto.EstadoCivil, 
                    perfilpuesto.Experiencia,
                    perfilpuesto.Escolaridad, 
                    perfilpuesto.ConocimientosEspecificos,
                    condicionestrabajo.EsfuerzoFisico, 
                    condicionestrabajo.EsfuerzoMental, 
                    condicionestrabajo.RiesgoAccidente, 
                    condicionestrabajo.Ambiente,
                    competencias.Responsabilidad, 
                    competencias.Compromiso, 
                    competencias.Empatia, 
                    competencias.TrabajoEquipo,
                    competencias.Energia,
                    departamento.NombreDepartamento, 
                    areas.NombreArea
                FROM 
                    puestos p1
                LEFT JOIN 
                    perfilpuesto ON perfilpuesto.IdPuesto = p1.IdPuesto
                LEFT JOIN 
                    condicionestrabajo ON condicionestrabajo.IdPerfil = perfilpuesto.Idperfil
                LEFT JOIN 
                    competencias ON competencias.IdPerfil = perfilpuesto.Idperfil
                LEFT JOIN 
                    departamento ON p1.DepartamentoId = departamento.IdDepartamento
                LEFT JOIN 
                    areas ON departamento.IdArea = areas.IdArea
                WHERE 
                    p1.id = %s;
                """
                cursor.execute(query, (user['id'],))
                datosDB = cursor.fetchall()
                columName = [column[0] for column in cursor.description]
                for registro in datosDB:
                    puesto = dict(zip(columName, registro))

                    # Convertir la ubicación binaria a base64 si es necesario
                    ubicacion_bin = puesto.get('Ubicacion')
                    if ubicacion_bin:
                        puesto['Ubicacion'] = base64.b64encode(
                            ubicacion_bin).decode('utf-8')
                    else:
                        puesto['Ubicacion'] = None

                    # Convertir el campo equipo de trabajo a una lista
                    if puesto['EquipoTrabajo']:
                        puesto['EquipoTrabajo'] = puesto['EquipoTrabajo'].split(
                            ',')
                    else:
                        puesto['EquipoTrabajo'] = []

                    # Convertir el campo equipo de ConocimientosEspecificos a una lista
                    if puesto['ConocimientosEspecificos']:
                        puesto['ConocimientosEspecificos'] = puesto['ConocimientosEspecificos'].split(
                            ',')
                    else:
                        puesto['ConocimientosEspecificos'] = []

                    # Convertir el campo Relaciones a una lista
                    if puesto['Relaciones']:
                        puesto['Relaciones'] = puesto['Relaciones'].split('.')
                    else:
                        puesto['Relaciones'] = []

                    # Convertir el campo FuncionesEspecificas a una lista
                    if puesto['FuncionesEspecificas']:
                        puesto['FuncionesEspecificas'] = puesto['FuncionesEspecificas'].split(
                            '.')
                    else:
                        puesto['FuncionesEspecificas'] = []

                    puestos_completos.append(puesto)

    except mysql.connector.Error as err:
        print(f"Error al obtener puestos completos: {err}")
        return "Error en la consulta a la base de datos", 500

    finally:
        if cursor is not None:
            cursor.close()

    usuario_id = user['id']
    departamentos = obtener_departamentos(usuario_id)
    puestos = obtener_puestos(usuario_id)

    return render_template("puestos.html", data=puestos_completos, departamentos=departamentos, puestos=puestos)

# Ruta para eliminar puestos.


@user_routes.route('/eliminar_puesto/<int:IdPuesto>/')
def eliminar_puesto(IdPuesto):
    cursor = db.cursor()
    try:
        # Eliminar condiciones de trabajo de perfiles relacionados con el puesto
        cursor.execute("""
            DELETE FROM condicionestrabajo 
            WHERE IdPerfil IN (SELECT IdPerfil 
                               FROM perfilpuesto 
                               WHERE IdPuesto = %s)
        """, (IdPuesto,))

        # Eliminar competencias de perfiles relacionados con el puesto
        cursor.execute("""
            DELETE FROM competencias 
            WHERE IdPerfil IN (SELECT IdPerfil 
                               FROM perfilpuesto 
                               WHERE IdPuesto = %s)
        """, (IdPuesto,))

        # Eliminar perfiles de puesto relacionados con el puesto
        cursor.execute(
            "DELETE FROM perfilpuesto WHERE IdPuesto = %s", (IdPuesto,))

        # Eliminar el puesto en la tabla Puestos
        cursor.execute("DELETE FROM puestos WHERE IdPuesto = %s", (IdPuesto,))

        db.commit()
        flash('Puesto eliminado correctamente', 'success')
    except mysql.connector.Error as err:
        print("Error al eliminar Puesto:", err)
        db.rollback()
        flash('Error al eliminar Puesto', 'error')
    finally:
        cursor.close()
    return redirect(url_for('user.mostrarPuestos'))

# Ruta para actualizar Área


@user_routes.route('/actualizarArea/<string:IdArea>', methods=['GET', 'POST'])
def actualizarArea(IdArea):
    if 'email' in session:
        email = session['email']
        user = get_user(email)
        if user:
            if request.method == 'POST':
                NombreArea = request.form["NombreArea"]
                try:
                    with db.cursor() as cursor:
                        # Verificar si el nombre del área ya existe para este usuario, excluyendo el área actual
                        cursor.execute(
                            "SELECT * FROM areas WHERE NombreArea = %s AND id = %s AND IdArea != %s",
                            (NombreArea, user['id'], IdArea)
                        )
                        existearea = cursor.fetchone()

                        if existearea is None:
                            # Proceder con la actualización si no se repite el nombre
                            sql_update = "UPDATE areas SET NombreArea = %s WHERE IdArea = %s"
                            cursor.execute(sql_update, (NombreArea, IdArea))
                            db.commit()
                            flash('Área actualizada correctamente', 'success')
                        else:
                            flash('El nombre del área ya existe', 'error')
                        return redirect(url_for('user.areas'))
                except mysql.connector.Error as err:
                    print("Error al editar área:", err)
                    db.rollback()
                    flash('Error al editar área', 'error')
        else:
            return redirect(url_for('main.index'))
    return redirect(url_for('user.areas'))


# Ruta para actualizar Departamento
@user_routes.route('/actualizarDepa/<string:IdDepartamento>', methods=['GET', 'POST'])
def actualizarDepa(IdDepartamento):
    if 'email' in session:
        email = session['email']
        user = get_user(email)
        if user:
            if request.method == 'POST':
                print(request.form)
                try:
                    NombreDepartamento = request.form["NombreDepartamento"]
                    Area = request.form["Area"]
                    if IdDepartamento and NombreDepartamento and Area:
                        with db.cursor() as cursor:
                            # Verificar si el nombre del departamento ya existe en esta área para este usuario, excluyendo el departamento actual
                            cursor.execute(
                                "SELECT * FROM departamento WHERE NombreDepartamento = %s AND IdArea = %s AND id = %s AND IdDepartamento != %s",
                                (NombreDepartamento, Area,
                                 user['id'], IdDepartamento)
                            )
                            existeDepartamento = cursor.fetchone()

                            if existeDepartamento is None:
                                # Proceder con la actualización si no se repite el nombre en la misma área
                                sql_update = "UPDATE departamento SET NombreDepartamento = %s, IdArea = %s WHERE IdDepartamento = %s"
                                cursor.execute(
                                    sql_update, (NombreDepartamento, Area, IdDepartamento))
                                db.commit()
                                flash(
                                    'Departamento actualizado correctamente', 'success')
                            else:
                                flash(
                                    'El nombre del departamento ya existe en esta área', 'error')
                            return redirect(url_for('user.mostrarDepartamentos'))
                    else:
                        flash('Todos los campos son requeridos', 'error')
                except KeyError as e:
                    flash(f'Error: campo requerido {e} no encontrado', 'error')
                except mysql.connector.Error as err:
                    print("Error al editar Departamento:", err)
                    db.rollback()
                    flash('Error al editar Departamento', 'error')
        else:
            return redirect(url_for('main.index'))
    return redirect(url_for('user.mostrarDepartamentos'))


@user_routes.route('/actualizar_datos/', methods=['POST'])
def actualizar_datos():
    if 'email' in session:
        email = session['email']
        user = get_user(email)
        if user:
            if request.method == 'POST':
                # Recoger datos del formulario
                IdPuesto = request.form.get('IdPuesto')
                NombrePuesto = request.form.get('NombrePuesto')
                Jefe = request.form.get('Jefe')
                Clave = request.form.get('Clave')
                NoPlazas = request.form.get('NoPlazas')
                Fecha = request.form.get('Fecha')
                nueva_ubicacion = request.files['nueva_foto']
                Objetivo = request.form.get('Objetivo')
                EquipoTrabajo = request.form.get('EquipoTrabajo')
                Reemplazar = request.form.get('Reemplazar')
                Reemplazado = request.form.get('Reemplazado')
                Nota = request.form.get('Nota')
                EsfuerzoFisico = request.form.get('EsfuerzoFisico')
                EsfuerzoMental = request.form.get('EsfuerzoMental')
                RiesgoAccidente = request.form.get('RiesgoAccidente')
                Ambiente = request.form.get('Ambiente')
                Edad = request.form.get('Edad')
                Sexo = request.form.get('Sexo')
                EstadoCivil = request.form.get('EstadoCivil')
                Experiencia = request.form.get('Experiencia')
                Escolaridad = request.form.get('Escolaridad')
                ConocimientosEspecificos = request.form.get(
                    'ConocimientosEspecificos')
                Responsabilidad = request.form.get('Responsabilidad')
                Compromiso = request.form.get('Compromiso')
                Empatia = request.form.get('Empatia')
                TrabajoEquipo = request.form.get('TrabajoEquipo')
                Energia = request.form.get('Energia')

                if nueva_ubicacion and nueva_ubicacion.filename.endswith('.jpg'):
                    nueva_ubicacion_data = nueva_ubicacion.read()
                    nueva_ubicacion_bin = nueva_ubicacion_data
                elif nueva_ubicacion and not nueva_ubicacion.filename.endswith('.jpg'):
                    flash('El archivo debe ser JPG')
                    return redirect(url_for('user.mostrarPuestos'))
                else:
                    nueva_ubicacion_bin = None

                try:
                    cursor = db.cursor()

                    # Verificar si el nombre del puesto ya existe para este usuario
                    cursor.execute(
                        "SELECT * FROM puestos WHERE NombrePuesto = %s AND id = %s",
                        (NombrePuesto, user['id'])
                    )
                    existe_puesto = cursor.fetchone()

                    if existe_puesto:
                        flash(
                            'El nombre del puesto ya existe para este usuario', 'error')
                    else:
                        # Actualización de la tabla Puestos
                        update_fields_puestos = []
                        update_values_puestos = []

                        if NombrePuesto:
                            update_fields_puestos.append("NombrePuesto = %s")
                            update_values_puestos.append(NombrePuesto)
                        if Jefe:
                            update_fields_puestos.append("Jefe = %s")
                            update_values_puestos.append(Jefe)
                        if Clave:
                            update_fields_puestos.append("Clave = %s")
                            update_values_puestos.append(Clave)
                        if NoPlazas:
                            update_fields_puestos.append("NoPlazas = %s")
                            update_values_puestos.append(NoPlazas)
                        if Fecha:
                            update_fields_puestos.append("Fecha = %s")
                            update_values_puestos.append(Fecha)
                        if nueva_ubicacion_bin:
                            update_fields_puestos.append("Ubicacion = %s")
                            update_values_puestos.append(nueva_ubicacion_bin)
                        if Objetivo:
                            update_fields_puestos.append("Objetivo = %s")
                            update_values_puestos.append(Objetivo)
                        if EquipoTrabajo:
                            update_fields_puestos.append("EquipoTrabajo = %s")
                            update_values_puestos.append(EquipoTrabajo)
                        if Reemplazar:
                            update_fields_puestos.append("Reemplazar = %s")
                            update_values_puestos.append(Reemplazar)
                        if Reemplazado:
                            update_fields_puestos.append("Reemplazado = %s")
                            update_values_puestos.append(Reemplazado)
                        if Nota:
                            update_fields_puestos.append("Nota = %s")
                            update_values_puestos.append(Nota)

                        update_values_puestos.append(IdPuesto)

                        if update_fields_puestos:
                            query_puestos = f"UPDATE puestos SET {', '.join(update_fields_puestos)} WHERE IdPuesto = %s"
                            cursor.execute(query_puestos, update_values_puestos)

                        # Obtener el IdPerfil relacionado con el IdPuesto
                        cursor.execute(
                            "SELECT IdPerfil FROM perfilpuesto WHERE IdPuesto = %s", (IdPuesto,))
                        IdPerfil = cursor.fetchone()
                        if IdPerfil:
                            IdPerfil = IdPerfil[0]
                        else:
                            IdPerfil = None

                        if IdPerfil:
                            # Actualización de la tabla PerfilPuesto
                            update_fields_perfil = []
                            update_values_perfil = []

                            if Edad:
                                update_fields_perfil.append("Edad = %s")
                                update_values_perfil.append(Edad)
                            if Sexo:
                                update_fields_perfil.append("Sexo = %s")
                                update_values_perfil.append(Sexo)
                            if EstadoCivil:
                                update_fields_perfil.append("EstadoCivil = %s")
                                update_values_perfil.append(EstadoCivil)
                            if Experiencia:
                                update_fields_perfil.append("Experiencia = %s")
                                update_values_perfil.append(Experiencia)
                            if Escolaridad:
                                update_fields_perfil.append("Escolaridad = %s")
                                update_values_perfil.append(Escolaridad)
                            if ConocimientosEspecificos:
                                update_fields_perfil.append(
                                    "ConocimientosEspecificos = %s")
                                update_values_perfil.append(
                                    ConocimientosEspecificos)

                            update_values_perfil.append(IdPerfil)

                            if update_fields_perfil:
                                query_perfil = f"UPDATE perfilpuesto SET {
                                    ', '.join(update_fields_perfil)} WHERE IdPerfil = %s"
                                cursor.execute(
                                    query_perfil, update_values_perfil)

                            # Actualización de la tabla CondicionesTrabajo
                            update_fields_condiciones = []
                            update_values_condiciones = []

                            if EsfuerzoFisico:
                                update_fields_condiciones.append(
                                    "EsfuerzoFisico = %s")
                                update_values_condiciones.append(
                                    EsfuerzoFisico)
                            if EsfuerzoMental:
                                update_fields_condiciones.append(
                                    "EsfuerzoMental = %s")
                                update_values_condiciones.append(
                                    EsfuerzoMental)
                            if RiesgoAccidente:
                                update_fields_condiciones.append(
                                    "RiesgoAccidente = %s")
                                update_values_condiciones.append(
                                    RiesgoAccidente)
                            if Ambiente:
                                update_fields_condiciones.append(
                                    "Ambiente = %s")
                                update_values_condiciones.append(Ambiente)

                            update_values_condiciones.append(IdPerfil)

                            if update_fields_condiciones:
                                query_condiciones = f"UPDATE condicionestrabajo SET {
                                    ', '.join(update_fields_condiciones)} WHERE IdPerfil = %s"
                                cursor.execute(query_condiciones,
                                               update_values_condiciones)

                            # Actualización de la tabla Competencias
                            update_fields_competencias = []
                            update_values_competencias = []

                            if Responsabilidad:
                                update_fields_competencias.append(
                                    "Responsabilidad = %s")
                                update_values_competencias.append(
                                    Responsabilidad)
                            if Compromiso:
                                update_fields_competencias.append(
                                    "Compromiso = %s")
                                update_values_competencias.append(Compromiso)
                            if Empatia:
                                update_fields_competencias.append(
                                    "Empatia = %s")
                                update_values_competencias.append(Empatia)
                            if TrabajoEquipo:
                                update_fields_competencias.append(
                                    "TrabajoEquipo = %s")
                                update_values_competencias.append(
                                    TrabajoEquipo)
                            if Energia:
                                update_fields_competencias.append(
                                    "Energia = %s")
                                update_values_competencias.append(Energia)

                            update_values_competencias.append(IdPerfil)

                            if update_fields_competencias:
                                query_competencias = f"UPDATE competencias SET {
                                    ', '.join(update_fields_competencias)} WHERE IdPerfil = %s"
                                cursor.execute(
                                    query_competencias, update_values_competencias)

                        db.commit()
                        flash('Datos actualizados correctamente')
                except mysql.connector.Error as err:
                    flash(f"Error al actualizar datos: {err}")
                    db.rollback()
                finally:
                    cursor.close()

    return redirect(url_for('user.mostrarPuestos'))
