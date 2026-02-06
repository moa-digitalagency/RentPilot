import qrcode
import os
import hashlib
import base64
from io import BytesIO

def generate_payment_qr(transaction_id, secret_key="rentpilot_secret"):
    """
    Generates a QR Code containing a verification hash for the transaction.

    Args:
        transaction_id: The ID of the transaction.
        secret_key: Secret key to salt the hash.

    Returns:
        BytesIO: The image data of the QR code.
    """
    # Create a simple verification string
    data_to_hash = f"{transaction_id}:{secret_key}"
    hash_verify = hashlib.sha256(data_to_hash.encode()).hexdigest()

    qr_content = f"RP:TX:{transaction_id}:{hash_verify[:10]}" # RentPilot:Transaction:ID:ShortHash

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_content)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return img_io
