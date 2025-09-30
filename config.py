"""
Configuration settings for System Discovery and Researching
"""

import os

# Flask configuration
FLASK_CONFIG = {
    'MAX_CONTENT_LENGTH': 50 * 1024 * 1024,  # 50MB max file size
    'UPLOAD_FOLDER': './uploads',
    'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
}

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'doc', 'docx', 'md', 'rtf', 'odt',
    'csv', 'xlsx', 'xls', 'json', 'xml', 'html', 'htm'
}

# Available models
AVAILABLE_MODELS = ["rag-gemma3", "gemma3", "llama2", "qwen2.5-coder", "Esperto_Python"]

# Default server settings
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080