import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime

class UploadService:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'heic'}
    UPLOAD_FOLDER = 'statics/uploads'

    @staticmethod
    def allowed_file(filename: str) -> bool:
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in UploadService.ALLOWED_EXTENSIONS

    @staticmethod
    def save_file(file_storage, subfolder: str = 'proofs') -> str:
        """
        Saves a file with a secure, unique name.

        :param file_storage: The FileStorage object from Flask (request.files['...'])
        :param subfolder: Subdirectory inside allowed upload folder (e.g., 'proofs', 'avatars')
        :return: The relative path to the saved file (e.g. 'statics/uploads/proofs/abc-123.jpg')
        """
        if not file_storage or file_storage.filename == '':
            raise ValueError("No file provided")

        if not UploadService.allowed_file(file_storage.filename):
            raise ValueError("File type not allowed")

        # Create directory if not exists
        target_dir = os.path.join(UploadService.UPLOAD_FOLDER, subfolder)
        os.makedirs(target_dir, exist_ok=True)

        # Generate unique filename
        ext = file_storage.filename.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}_{int(datetime.now().timestamp())}.{ext}"

        # Full path
        file_path = os.path.join(target_dir, unique_name)
        file_storage.save(file_path)

        return file_path
