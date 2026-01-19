from flask import Flask, redirect, url_for, session, render_template
from config import Config
from extensions import db
from models.user import User

from jinja2.ext import do
from blueprints.auth.routes import auth_bp
from blueprints.diets.routes import diets_bp
from blueprints.residents.routes import residents_bp
from blueprints.import_csv.routes import import_csv_bp
from blueprints.documents.routes import documents_bp
from blueprints.dashboard.routes import dashboard_bp
from blueprints.stats.routes import bp as stats_bp
from blueprints.print.routes import bp as print_bp


import os

# Import blueprinta fileexplorer
from blueprints.fileexplorer import file_explorer_bp
from blueprints.fileexplorer.filters import register_filters




def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    os.makedirs('uploads', exist_ok=True)
    os.makedirs('generated', exist_ok=True)

    app.register_blueprint(auth_bp)
    app.register_blueprint(diets_bp)
    app.register_blueprint(residents_bp)
    app.register_blueprint(import_csv_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(file_explorer_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(print_bp)
    
    # Konfiguracja file explorера na folder uploads
    app.config['FFE_BASE_DIRECTORY'] = os.path.abspath('uploads')
    register_filters(app)
    
    app.jinja_env.add_extension('jinja2.ext.do')

    return app


if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('admin_diety')
            db.session.add(admin)
            db.session.commit()

    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"]
    )
