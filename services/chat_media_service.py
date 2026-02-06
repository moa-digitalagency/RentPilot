import os
import uuid
from datetime import datetime
from PIL import Image
from werkzeug.datastructures import FileStorage
from services.upload_service import UploadService

class ChatMediaService:
    ALLOWED_EXTENSIONS_IMG = {'png', 'jpg', 'jpeg', 'heic'}
    ALLOWED_EXTENSIONS_AUDIO = {'mp3', 'wav'}

    @staticmethod
    def allowed_file(filename: str) -> bool:
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in ChatMediaService.ALLOWED_EXTENSIONS_IMG or \
               ext in ChatMediaService.ALLOWED_EXTENSIONS_AUDIO

    @staticmethod
    def process_and_save(file_storage: FileStorage, subfolder: str = 'chat') -> str:
        """
        Saves a file. Compresses if it's an image.
        Returns the relative path to the saved file.
        """
        if not file_storage or not file_storage.filename:
            raise ValueError("No file provided")

        if not ChatMediaService.allowed_file(file_storage.filename):
            raise ValueError("File type not allowed")

        ext = file_storage.filename.rsplit('.', 1)[1].lower()

        # Directory setup using UploadService configuration
        target_dir = os.path.join(UploadService.UPLOAD_FOLDER, subfolder)
        os.makedirs(target_dir, exist_ok=True)

        unique_name = f"{uuid.uuid4().hex}_{int(datetime.now().timestamp())}.{ext}"
        file_path = os.path.join(target_dir, unique_name)

        if ext in ChatMediaService.ALLOWED_EXTENSIONS_IMG and ext != 'heic':
            # Compress Image (Skip HEIC as it requires extra libs not guaranteed)
            try:
                # Open image
                img = Image.open(file_storage)

                # Convert to RGB if necessary (for JPG saving)
                if img.mode in ('RGBA', 'P') and ext in ['jpg', 'jpeg']:
                    img = img.convert('RGB')

                # Save with compression
                img.save(file_path, optimize=True, quality=70)
            except Exception as e:
                print(f"Image compression failed: {e}. Saving original.")
                file_storage.seek(0)
                file_storage.save(file_path)
        else:
            # Audio or HEIC - just save
            file_storage.seek(0) # Ensure we are at start
            file_storage.save(file_path)

        return file_path
