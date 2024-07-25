from flask import Blueprint, render_template, redirect, url_for, session

main_routes = Blueprint('main', __name__)


# Ruta principal
@main_routes.route('/')
def index():
    return render_template('index.html')


# Ruta para cerrar sesión
@main_routes.route('/logout/')
def logout():
    session.clear()  # Elimina todas las variables de sesión
    return redirect(url_for('main.index'))
