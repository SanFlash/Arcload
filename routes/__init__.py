"""
Routes blueprint registration
"""

def register_blueprints(app):
    """Register all blueprints"""
    from routes.main import main_bp
    from routes.admin import admin_bp
    from routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')