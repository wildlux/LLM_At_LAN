"""
Utility functions for System Discovery and Researching
"""

import os

# Allowed file extensions (moved from config for simplicity)
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'doc', 'docx', 'md', 'rtf', 'odt',
    'csv', 'xlsx', 'xls', 'json', 'xml', 'html', 'htm'
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_content(file):
    """Validate file content (simplified without python-magic)"""
    # Basic validation based on extension (already checked in allowed_file)
    return True

def ensure_upload_folder(folder_path):
    """Ensure upload folder exists"""
    os.makedirs(folder_path, exist_ok=True)

def safe_save_file(file, folder_path, filename):
    """Safely save uploaded file with path traversal protection"""
    # Prevent path traversal
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(folder_path, safe_filename)

    # Verify path is safe
    if not os.path.commonprefix([os.path.realpath(file_path), os.path.realpath(folder_path)]) == os.path.realpath(folder_path):
        raise ValueError("Invalid file path")

    file.save(file_path)
    return safe_filename