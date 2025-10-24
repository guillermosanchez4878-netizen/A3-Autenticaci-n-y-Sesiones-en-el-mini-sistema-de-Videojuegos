from flask import Flask, render_template, request, redirect, flash, url_for
from db_setup import db
import controllers 
from models import User # Importamos el nuevo modelo User
from auth import auth as auth_blueprint # Importar el Blueprint

# Importar para autenticación
from flask_login import LoginManager, login_required
# La importación de generate_password_hash/check_password_hash se movió a models.py

app = Flask(__name__)

# --- CONFIGURACIÓN DE FLASK-SQLALCHEMY ---
# ¡Asegúrate de que la URI sea la correcta para tu base de datos!
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:memo123.@localhost/juegos' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db.init_app(app) 

# --- CONFIGURACIÓN DE AUTENTICACIÓN ---
app.config['SECRET_KEY'] = 'una_clave_secreta_muy_dificil_de_adivinar' 

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login' # Vista a la que redirige si no hay login
login_manager.session_protection = 'strong' 

# Función callback: User Loader
@login_manager.user_loader 
def load_user(user_id):
    return User.query.get(int(user_id))
# ----------------------------------------


# --- RUTAS DE JUEGOS (PROTEGIDAS) ---

@app.route("/")
@app.route("/juegos")
@login_required # Protege la ruta
def juegos():
    juegos = controllers.obtener_juegos()
    return render_template("juegos.html", juegos=juegos)

@app.route("/agregar_juego")
@login_required # Protege la ruta
def formulario_agregar_juego():
    return render_template("agregar_juego.html")

@app.route("/guardar_juego", methods=["POST"])
@login_required # Protege la ruta
def guardar_juego():
    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]
    precio = request.form["precio"]
    controllers.insertar_juego(nombre, descripcion, precio)
    flash(f"Juego '{nombre}' guardado exitosamente.", "success")
    return redirect("/juegos")

@app.route("/eliminar_juego", methods=["POST"])
@login_required # Protege la ruta
def eliminar_juego():
    juego = controllers.obtener_juego_por_id(request.form["id"])
    if juego:
        nombre_juego = juego.nombre
        controllers.eliminar_juego(request.form["id"])
        flash(f"Juego '{nombre_juego}' eliminado exitosamente.", "success")
    return redirect("/juegos")

@app.route("/formulario_editar_juego/<int:id>")
@login_required # Protege la ruta
def editar_juego(id):
    juego = controllers.obtener_juego_por_id(id)
    return render_template("editar_juego.html", juego=juego)

@app.route("/actualizar_juego", methods=["POST"])
@login_required # Protege la ruta
def actualizar_juego():
    id = request.form["id"]
    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]
    precio = request.form["precio"]
    controllers.actualizar_juego(nombre, descripcion, precio, id)
    flash(f"Juego '{nombre}' actualizado exitosamente.", "success")
    return redirect("/juegos")


# --- REGISTRO DEL BLUEPRINT DE AUTENTICACIÓN ---
# Registra las rutas de login y logout con el prefijo /auth
app.register_blueprint(auth_blueprint, url_prefix='/auth')
# -----------------------------------------------

# Crea las tablas (juegos y users)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(port=8000, debug=True)