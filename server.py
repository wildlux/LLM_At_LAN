"""
Flask server for System Discovery and Researching
"""

from flask import Flask, request, jsonify, render_template
import os
import argparse
import signal
import sys

from config import FLASK_CONFIG, AVAILABLE_MODELS, DEFAULT_HOST, DEFAULT_PORT
from utils import allowed_file, validate_file_content, ensure_upload_folder, safe_save_file
from RAG.rag_engine import SDREngine

class SDRServer:
    """Flask server wrapper for System Discovery and Researching"""

    def __init__(self):
        print("Initializing SDRServer...")
        self.app = Flask(__name__)
        self.app.config.update(FLASK_CONFIG)
        self.upload_folder = self.app.config['UPLOAD_FOLDER']
        ensure_upload_folder(self.upload_folder)

        print("Creating SDREngine...")
        self.sdr_engine = SDREngine(self.upload_folder, AVAILABLE_MODELS)
        print("Setting up routes...")
        self.setup_routes()
        print("SDRServer initialized successfully")

    def setup_routes(self):
        """Setup Flask routes"""

        @self.app.route("/")
        def home():
            """Homepage"""
            return render_template("index.html")

        @self.app.route("/models", methods=["GET"])
        def get_models():
            """Get available models"""
            return jsonify({"models": self.sdr_engine.get_available_models()})

        @self.app.route("/upload", methods=["POST"])
        def upload_files():
            """Upload files"""
            if 'file' not in request.files:
                return jsonify({"error": "No file part"}), 400

            file = request.files['file']
            if file.filename == '' or file.filename is None:
                return jsonify({"error": "No selected file"}), 400

            # Security checks
            if not allowed_file(file.filename):
                return jsonify({"error": "File type not allowed"}), 400

            if not validate_file_content(file):
                return jsonify({"error": "Invalid file content"}), 400

            try:
                filename = safe_save_file(file, self.upload_folder, file.filename)
                return jsonify({"message": f"File '{filename}' uploaded successfully!"}), 200
            except Exception as e:
                return jsonify({"error": f"Upload failed: {str(e)}"}), 500

        @self.app.route("/query", methods=["POST"])
        def query():
            """Process query"""
            data = request.json
            if data is None:
                return jsonify({"error": "Invalid JSON"}), 400

            query_text = data.get("query", "")
            selected_model = data.get("model", "llama2")

            if not query_text:
                return jsonify({"error": "Query text is required"}), 400

            try:
                response = self.sdr_engine.query(query_text, selected_model)
                return jsonify({"response": response}), 200
            except Exception as e:
                return jsonify({"error": f"Query failed: {str(e)}"}), 500

    def run(self, host=DEFAULT_HOST, port=DEFAULT_PORT, debug=True):
        """Run the server"""
        def signal_handler(sig, frame):
            print('\nShutting down server...')
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        print(f"Starting server on {host}:{port}")
        print("Press Ctrl+C to stop the server.")
        self.app.run(host=host, port=port, debug=debug)

# For backward compatibility
app = SDRServer().app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the RAG system server")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host to bind to")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to bind to")
    args = parser.parse_args()

    server = SDRServer()
    server.run(args.host, args.port)