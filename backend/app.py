import os
import sys


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS

class Config:
    PORT = 3000
    DEBUG = False

# Import Blueprints
# (If this fails next, it means 'routes' folder is also missing!)
from routes.auth import auth_bp
from routes.student import student_bp
from routes.recruiter import recruiter_bp
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Register Blueprints with /api prefix
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(recruiter_bp, url_prefix='/api/recruiter')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    @app.route('/')
    def index():
        return jsonify({"message": "OCS Portal API is running", "status": "online"})

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal Server Error", "success": False}), 500

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint not found", "success": False}), 404

    return app

# GLOBAL APP VARIABLE
config = Config()
app = create_app()

if __name__ == '__main__':
    print(f"✅ Server starting on port {config.PORT}...")
    app.run(host='0.0.0.0', port=config.PORT, debug=config.DEBUG)