from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from routes.site_routes import site_bp
from routes.auth_routes import auth_bp
import os
import socket

def get_local_ip():
    """Get the local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "0.0.0.0"

def init_database(app, force=False):
    """Initialize database and demo data"""
    with app.app_context():
        try:
            if force or os.environ.get('RESET_DB') == 'true':
                db.drop_all()
                print("Database reset completed")
            
            db.create_all()
            from init_db import init_demo_data
            init_demo_data()
        except Exception as e:
            print(f"Database initialization error: {e}")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smartaqua.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    CORS(app)
    db.init_app(app)
    
    app.register_blueprint(site_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    
    # Initialize database only on first run
    if not hasattr(app, '_db_initialized'):
        init_database(app)
        app.config['LOCAL_IP'] = get_local_ip()
        app._db_initialized = True
    
    return app

if __name__ == '__main__':
    app = create_app()
    if app:
        print(f"\nServer running at:")
        print(f"- Local:   http://127.0.0.1:5000")
        print(f"- Network: http://{app.config['LOCAL_IP']}:5000\n")
        app.run(
            debug=True, 
            host='0.0.0.0', 
            port=int(os.environ.get('PORT', 5000)),
            use_reloader=False
        )
    else:
        print("L'application n'a pas pu être démarrée")