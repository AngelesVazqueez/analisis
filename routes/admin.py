from flask import Blueprint, render_template, url_for, redirect, session
from func.func import get_admin

admin_routes = Blueprint('admin', __name__)


# Ruta para el administrador
@admin_routes.route('/admin/')
def admin():
    if 'email' in session:
        email = session['email']
        # Función para obtener datos del usuario desde MongoDB
        admin = get_admin(email)
        if admin:
            return render_template('admin.html', admin=admin)
    else:
        return redirect(url_for('main.index'))