from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
# from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_mail import Mail

from igsbill.config import Config

db = SQLAlchemy()
# bcrypt = Bcrypt()
migrate = Migrate()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(Config)

	db.init_app(app)
	# bcrypt.init_app(app)
	migrate.init_app(app, db)
	mail.init_app(app)
	login_manager.init_app(app)

	from igsbill.main.routes import main
	from igsbill.admin.routes import admin
	from igsbill.users.routes import users
	from igsbill.services.routes import services
	from igsbill.bills.routes import bills
	from igsbill.payments.routes import payments
	from igsbill.withdrawals.routes import withdrawals

	app.register_blueprint(main)
	app.register_blueprint(admin)
	app.register_blueprint(users)
	app.register_blueprint(services)
	app.register_blueprint(bills)
	app.register_blueprint(payments)
	app.register_blueprint(withdrawals)

	return app
