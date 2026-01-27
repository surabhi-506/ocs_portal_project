
from flask import Flask, jsonify
from flask_cors import CORS
from config import config

# Import Blueprints
from routes.auth import auth_bp
from routes.student import student_bp
from routes.recruiter import recruiter_bp
from routes.admin import admin_bp


def create_app():
    # Initialize Flask
    app = Flask(__name__)

    # Enable CORS (Allows your frontend to talk to this backend)
    CORS(app)

    # Register Blueprints (The API Routes)
    # FIX: We added url_prefix='/api' to auth_bp so it matches the frontend request
    app.register_blueprint(auth_bp, url_prefix='/api')

    # These were already correct, but good to double-check!
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(recruiter_bp, url_prefix='/api/recruiter')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # Basic Health Check Route
    @app.route('/')
    def index():
        return jsonify({
            "message": "OCS Portal API is running",
            "status": "online"
        })

    # Global Error Handler
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal Server Error", "success": False}), 500

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint not found", "success": False}), 404

    return app


# Run the Server
if __name__ == '__main__':
    # Validate Config (check if .env is loaded)
    try:
        config.validate()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        exit(1)

app = create_app()


if __name__ == '__main__':
    print(f"✅ Server starting on port {config.PORT}...")
    app.run(host='0.0.0.0', port=config.PORT, debug=config.DEBUG)