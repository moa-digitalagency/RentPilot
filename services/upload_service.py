import os
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, upload_folder):
    """
    Saves an uploaded file securely with a unique name.

    Args:
        file: The file storage object from Flask.
        upload_folder: The directory to save the file.

    Returns:
        str: The relative path to the saved file (or absolute if configured), or None if invalid.
    """
    if file and allowed_file(file.filename):
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}.{extension}"
        filepath = os.path.join(upload_folder, unique_filename)

        file.save(filepath)
        return unique_filename
    return None
