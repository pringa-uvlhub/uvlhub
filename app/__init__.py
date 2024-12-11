import os
import threading

from app.discord.pringa_bot import start_bot
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_migrate import Migrate
from core.configuration.configuration import get_app_version
from core.managers.module_manager import ModuleManager
from core.managers.config_manager import ConfigManager
from core.managers.error_handler_manager import ErrorHandlerManager
from core.managers.logging_manager import LoggingManager
from flask_mail import Mail, Message
from flask_login import LoginManager

# Cargar variables de entorno
load_dotenv()

# Crear las instancias
db = SQLAlchemy()
migrate = Migrate()

# Configurar Mail
mail = Mail()

# Evento para controlar si el bot ya está iniciado
bot_event = threading.Event()


def create_app(config_name='development'):
    app = Flask(__name__)
    # Configuración del servidor de correo
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'pringauvlhub@gmail.com'
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = 'pringauvlhub@gmail.com'
    mail.init_app(app)  # Inicializamos el mail con la aplicación

    # Cargar la configuración según el entorno
    config_manager = ConfigManager(app)
    config_manager.load_config(config_name=config_name)

    # Inicializar SQLAlchemy y Migrate con la app
    db.init_app(app)
    migrate.init_app(app, db)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Registrar módulos
    module_manager = ModuleManager(app)
    module_manager.register_modules()

    # Registrar login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        from app.modules.auth.models import User
        return User.query.get(int(user_id))

    # Configuración del logging
    logging_manager = LoggingManager(app)
    logging_manager.setup_logging()

    # Inicializar el error handler
    error_handler_manager = ErrorHandlerManager(app)
    error_handler_manager.register_error_handlers()

    # Inyectar variables de entorno en el contexto de Jinja
    @app.context_processor
    def inject_vars_into_jinja():
        return {
            'FLASK_APP_NAME': os.getenv('FLASK_APP_NAME'),
            'FLASK_ENV': os.getenv('FLASK_ENV'),
            'DOMAIN': os.getenv('DOMAIN', 'localhost'),
            'APP_VERSION': get_app_version()
        }

    @app.before_request
    def start_discord_bot():
        if not bot_event.is_set():
            bot_event.set()  # Marca el evento como iniciado
            threading.Thread(target=start_bot, daemon=True).start()  # Inicia el bot en un hilo separado

    return app


# Función para enviar correos de restablecimiento de contraseña
def send_reset_email(to_email, reset_url):
    msg = Message("Restablece tu contraseña", recipients=[to_email])
    msg.body = f"Para restablecer tu contraseña, sigue este enlace: {reset_url}"
    mail.send(msg)


# Crear la app
app = create_app()

# discord_thread = threading.Thread(target=start_bot, args=(1,))
# discord_thread.daemon = True  # Esto permitirá que el hilo termine cuando la aplicación Flask termine
# discord_thread.start()
'''
# Función para iniciar Flask y Discord simultáneamente
async def start_flask_and_discord():
    # Iniciar el bot de Discord
    discord_task = asyncio.create_task(start_bot())
    # Iniciar Flask en un hilo de ejecución
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5000, app, use_reloader=False, use_debugger=True)
    # Esperar que el bot termine de ejecutarse
    await discord_task
if __name__ == "__main__":
    asyncio.run(start_flask_and_discord())
'''
