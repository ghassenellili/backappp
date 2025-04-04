from routes.auth_routes import auth_bp
from routes.site_routes import site_bp

def init_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(site_bp, url_prefix='/api')