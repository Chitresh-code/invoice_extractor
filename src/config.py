import hashlib
import re
from pathlib import Path
from typing import Optional
from src.logger import setup_logger

# Configure logging
logger = setup_logger(__name__)

def hash_password(password: str) -> str:
    """Hashes a password using SHA-256."""
    logger.info("Hashing password")
    sha_signature = hashlib.sha256(password.encode()).hexdigest()
    logger.info("Password hashed successfully")
    return sha_signature

def is_valid_email(email: str) -> bool:
    """Verifies if the entered email is valid."""
    logger.info("Validating email: %s", email)
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    is_valid = re.match(email_regex, email) is not None
    if is_valid:
        logger.info("Email is valid")
    else:
        logger.warning("Email is invalid")
    return is_valid

def is_strong_password(password: str) -> bool:
    """Checks if the password is strong."""
    logger.info("Checking password strength")
    if len(password) < 8:
        logger.warning("Password is too short")
        return False
    if not re.search(r'[A-Z]', password):
        logger.warning("Password lacks an uppercase letter")
        return False
    if not re.search(r'[a-z]', password):
        logger.warning("Password lacks a lowercase letter")
        return False
    if not re.search(r'[0-9]', password):
        logger.warning("Password lacks a digit")
        return False
    if not re.search(r'[\W_]', password):
        logger.warning("Password lacks a special character")
        return False
    logger.info("Password is strong")
    return True

def create_temp_dir() -> Optional[Path]:
    """Creates a directory named 'tempDir'."""
    logger.info("Creating 'tempDir' directory in the 'backend' folder")
    
    try:
        # Define the path for the new directory
        backend_dir = Path(__file__).parent.parent
        temp_dir_path = backend_dir / 'tempDir'
        
        # Create the directory if it doesn't exist
        temp_dir_path.mkdir(exist_ok=True)
        
        logger.info("Directory 'tempDir' created at: %s", temp_dir_path)
        return temp_dir_path
    except Exception as e:
        logger.error("Error creating 'tempDir' directory: %s", e)
        return None
    
def delete_temp_dir() -> None:
    """Deletes the directory named 'tempDir'."""
    logger.info("Deleting 'tempDir' directory in the 'backend' folder")
    
    try:
        # Define the path for the directory to be deleted
        backend_dir = Path(__file__).parent.parent
        temp_dir_path = backend_dir / 'tempDir'
        
        # Delete the directory if it exists
        if temp_dir_path.exists():
            for file in temp_dir_path.iterdir():
                if file.is_file():
                    file.unlink()
            temp_dir_path.rmdir()
            logger.info("Directory 'tempDir' deleted successfully")
        else:
            logger.warning("Directory 'tempDir' does not exist")
    except Exception as e:
        logger.error("Error deleting 'tempDir' directory: %s", e)
        return None
    
def delete_log_dir() -> None:
    """Deletes all files in the directory named 'logs'."""
    
    try:
        backend_dir = Path(__file__).parent.parent
        log_dir_path = backend_dir / 'logs'
        
        if log_dir_path.exists():
            for file in log_dir_path.iterdir():
                if file.is_file():
                    with open(file, 'w') as f:
                        pass
        else:
            return
    except Exception as e:
        return