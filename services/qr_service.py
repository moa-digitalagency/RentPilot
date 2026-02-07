
"""
* Nom de l'application : RentPilot
* Description : Service logic for qr module.
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
import qrcode
import hashlib
import io
import base64
import os
from typing import Tuple

class QRService:
    @staticmethod
    def _get_secret(provided_key: str = None) -> str:
        if provided_key:
            return provided_key
        # Fallback to environment variable, then to a warning placeholder
        return os.environ.get('SECRET_KEY', 'WARNING_NO_SECRET_SET')

    @staticmethod
    def generate_verification_hash(transaction_id: int, user_id: int, amount: float, secret_key: str = None) -> str:
        """
        Generates a SHA256 hash to verify the integrity of the transaction data.
        """
        key = QRService._get_secret(secret_key)
        data_string = f"{transaction_id}:{user_id}:{amount}:{key}"
        return hashlib.sha256(data_string.encode()).hexdigest()

    @staticmethod
    def generate_qr_code(transaction_id: int, user_id: int, amount: float, secret_key: str = None) -> io.BytesIO:
        """
        Generates a QR Code image (PNG) containing verification data.
        Returns the image as a BytesIO stream.
        """
        verification_hash = QRService.generate_verification_hash(transaction_id, user_id, amount, secret_key)

        # content of the QR code: JSON-like string or URL
        qr_content = f"TRANS_ID:{transaction_id};USER:{user_id};AMT:{amount};HASH:{verification_hash[:16]}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        return img_buffer

    @staticmethod
    def get_base64_qr(transaction_id: int, user_id: int, amount: float) -> str:
        """
        Helper to get Base64 string for HTML embedding.
        """
        img_buffer = QRService.generate_qr_code(transaction_id, user_id, amount)
        img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{img_str}"

    @staticmethod
    def generate_url_qr(url: str) -> io.BytesIO:
        """
        Generates a QR Code image (PNG) for a given URL.
        Returns the image as a BytesIO stream.
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        return img_buffer