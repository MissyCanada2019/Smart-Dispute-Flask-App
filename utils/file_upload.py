import os
import uuid
import hashlib
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import current_app
from typing import Tuple, Optional, Dict, Any
import mimetypes

class FileUploadError(Exception):
    """Custom exception for file upload errors"""
    pass

class FileUploadHandler:
    """Handles secure file uploads with validation and storage"""
    
    # Allowed file extensions and their corresponding MIME types
    ALLOWED_EXTENSIONS = {
        'pdf': ['application/pdf'],
        'jpg': ['image/jpeg'],
        'jpeg': ['image/jpeg'],
        'png': ['image/png'],
        'gif': ['image/gif'],
        'bmp': ['image/bmp'],
        'tiff': ['image/tiff'],
        'tif': ['image/tiff'],
        'webp': ['image/webp']
    }
    
    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        'pdf': 50 * 1024 * 1024,  # 50MB for PDFs
        'image': 20 * 1024 * 1024,  # 20MB for images
        'default': 10 * 1024 * 1024  # 10MB default
    }
    
    def __init__(self, upload_folder: str = None):
        """Initialize file upload handler"""
        self.upload_folder = upload_folder or current_app.config.get('UPLOAD_FOLDER', 'uploads')
        self.ensure_upload_folder_exists()
    
    def ensure_upload_folder_exists(self):
        """Create upload folder if it doesn't exist"""
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder, exist_ok=True)
            
        # Create subdirectories for organization
        subdirs = ['evidence', 'forms', 'temp']
        for subdir in subdirs:
            subdir_path = os.path.join(self.upload_folder, subdir)
            if not os.path.exists(subdir_path):
                os.makedirs(subdir_path, exist_ok=True)
    
    def get_file_extension(self, filename: str) -> str:
        """Get file extension from filename"""
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    def is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        extension = self.get_file_extension(filename)
        return extension in self.ALLOWED_EXTENSIONS
    
    def validate_mime_type(self, file: FileStorage, filename: str) -> bool:
        """Validate MIME type matches file extension"""
        extension = self.get_file_extension(filename)
        if extension not in self.ALLOWED_EXTENSIONS:
            return False
        
        # Get MIME type from file content
        file_mime_type = file.mimetype
        allowed_mime_types = self.ALLOWED_EXTENSIONS[extension]
        
        return file_mime_type in allowed_mime_types
    
    def validate_file_size(self, file: FileStorage, filename: str) -> bool:
        """Validate file size is within limits"""
        extension = self.get_file_extension(filename)
        
        # Determine file category for size limits
        if extension == 'pdf':
            max_size = self.MAX_FILE_SIZES['pdf']
        elif extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'webp']:
            max_size = self.MAX_FILE_SIZES['image']
        else:
            max_size = self.MAX_FILE_SIZES['default']
        
        # Get file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        return file_size <= max_size
    
    def generate_secure_filename(self, original_filename: str) -> str:
        """Generate a secure, unique filename"""
        # Secure the original filename
        secure_name = secure_filename(original_filename)
        
        # Generate unique filename with UUID
        extension = self.get_file_extension(secure_name)
        unique_id = str(uuid.uuid4())
        
        return f"{unique_id}.{extension}"
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file for integrity verification"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def get_file_info(self, file_path: str, original_filename: str) -> Dict[str, Any]:
        """Get comprehensive file information"""
        file_size = os.path.getsize(file_path)
        file_hash = self.calculate_file_hash(file_path)
        extension = self.get_file_extension(original_filename)
        mime_type = mimetypes.guess_type(file_path)[0]
        
        return {
            'file_size': file_size,
            'file_hash': file_hash,
            'extension': extension,
            'mime_type': mime_type,
            'is_pdf': extension == 'pdf',
            'is_image': extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'webp']
        }
    
    def save_file(self, file: FileStorage, subfolder: str = 'evidence') -> Tuple[str, Dict[str, Any]]:
        """
        Save uploaded file securely
        
        Args:
            file: The uploaded file object
            subfolder: Subfolder within upload directory
            
        Returns:
            Tuple of (file_path, file_info)
            
        Raises:
            FileUploadError: If validation fails or save operation fails
        """
        if not file or not file.filename:
            raise FileUploadError("No file provided")
        
        original_filename = file.filename
        
        # Validate file extension
        if not self.is_allowed_file(original_filename):
            raise FileUploadError(f"File type not allowed. Allowed types: {', '.join(self.ALLOWED_EXTENSIONS.keys())}")
        
        # Validate MIME type
        if not self.validate_mime_type(file, original_filename):
            raise FileUploadError("File content doesn't match file extension")
        
        # Validate file size
        if not self.validate_file_size(file, original_filename):
            extension = self.get_file_extension(original_filename)
            max_size_mb = self.MAX_FILE_SIZES.get(extension, self.MAX_FILE_SIZES['default']) // (1024 * 1024)
            raise FileUploadError(f"File too large. Maximum size: {max_size_mb}MB")
        
        # Generate secure filename
        secure_name = self.generate_secure_filename(original_filename)
        
        # Create full file path
        subfolder_path = os.path.join(self.upload_folder, subfolder)
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path, exist_ok=True)
        
        file_path = os.path.join(subfolder_path, secure_name)
        
        try:
            # Save file
            file.save(file_path)
            
            # Get file information
            file_info = self.get_file_info(file_path, original_filename)
            file_info['original_filename'] = original_filename
            file_info['secure_filename'] = secure_name
            file_info['relative_path'] = os.path.join(subfolder, secure_name)
            
            return file_path, file_info
            
        except Exception as e:
            # Clean up file if save failed
            if os.path.exists(file_path):
                os.remove(file_path)
            raise FileUploadError(f"Failed to save file: {str(e)}")
    
    def delete_file(self, file_path: str) -> bool:
        """
        Safely delete a file
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
    
    def get_upload_url(self, relative_path: str) -> str:
        """Get URL for accessing uploaded file"""
        return f"/uploads/{relative_path}"
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.1f} {size_names[i]}"
    
    @staticmethod
    def get_file_type_description(extension: str) -> str:
        """Get human-readable file type description"""
        descriptions = {
            'pdf': 'PDF Document',
            'jpg': 'JPEG Image',
            'jpeg': 'JPEG Image',
            'png': 'PNG Image',
            'gif': 'GIF Image',
            'bmp': 'Bitmap Image',
            'tiff': 'TIFF Image',
            'tif': 'TIFF Image',
            'webp': 'WebP Image'
        }
        return descriptions.get(extension.lower(), 'Unknown File Type')


# Global instance for easy access
_file_upload_handler = None

def get_file_upload_handler():
    global _file_upload_handler
    if _file_upload_handler is None:
        with current_app.app_context():
            _file_upload_handler = FileUploadHandler()
    return _file_upload_handler


def save_evidence_file(file: FileStorage) -> Tuple[str, Dict[str, Any]]:
    """Convenience function for saving evidence files"""
    return file_upload_handler.save_file(file, 'evidence')


def save_form_file(file: FileStorage) -> Tuple[str, Dict[str, Any]]:
    """Convenience function for saving form-related files"""
    return file_upload_handler.save_file(file, 'forms')


def delete_evidence_file(file_path: str) -> bool:
    """Convenience function for deleting evidence files"""
    return file_upload_handler.delete_file(file_path)