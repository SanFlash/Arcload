"""
Main Flask application factory
Entry point for Arcaload
"""

import os
from flask import Flask, render_template, session
from config import active_config
from models import db, Admin, Game, GameRequest
from datetime import timedelta

def create_app(config=None):
    """Application factory function"""
    
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    if config is None:
        app.config.from_object(active_config)
    else:
        app.config.from_object(config)
    # Create instance folder if it doesn't exist (ensure writable path for sqlite)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # If no external DATABASE_URL is provided, point SQLite to the instance folder
    # This avoids attempting to write to a read-only location created during build
    if not os.environ.get('DATABASE_URL'):
        db_file = os.path.join(app.instance_path, 'arcaload.db')
        sqlite_uri = f"sqlite:///{db_file}"
        app.config.setdefault('SQLALCHEMY_DATABASE_URI', sqlite_uri)

        # Ensure the DB file exists and has permissive write permissions
        try:
            # create empty file if missing
            if not os.path.exists(db_file):
                open(db_file, 'a').close()
            # attempt to set writable permissions (best-effort; may fail on some hosts)
            try:
                os.chmod(db_file, 0o660)
            except Exception:
                pass
        except Exception:
            pass

    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    from routes import register_blueprints
    register_blueprints(app)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
    
    # Before request handler
    @app.before_request
    def before_request():
        """Make session permanent and update lifetime"""
        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=24)
    
    # Context processors
    @app.context_processor
    def inject_config():
        """Inject config into templates"""
        return {
            'app_name': 'Arcaload',
            'app_version': '1.0.0'
        }
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin if not exists
        if Admin.query.first() is None:
            admin = Admin()
            admin.username = os.environ.get('ADMIN_USERNAME', 'admin')
            admin.email = os.environ.get('ADMIN_EMAIL', 'admin@arcaload.com')
            admin.set_password(os.environ.get('ADMIN_PASSWORD', 'Admin@123'))
            db.session.add(admin)
            db.session.commit()
            print("✓ Default admin user created")
    
    return app


# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
