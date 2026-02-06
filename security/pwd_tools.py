from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password):
    """Hash a password for storing."""
    return generate_password_hash(password)

def check_password(pwhash, password):
    """Check a hashed password against a plain text password."""
    return check_password_hash(pwhash, password)
