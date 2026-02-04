"""
Security module for file encryption, decryption, and access control.
Implements file encryption storage, hashing, and permission-based access control.
"""

import os
import hashlib
from datetime import datetime
from typing import Optional, Tuple
from cryptography.fernet import Fernet
from pathlib import Path


class FileEncryptionManager:
    """Manages file encryption and decryption operations."""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize the encryption manager.
        
        Args:
            encryption_key: Encryption key (base64 encoded). If None, generates a new one.
        """
        if encryption_key is None:
            self.encryption_key = Fernet.generate_key()
        else:
            self.encryption_key = encryption_key.encode() if isinstance(encryption_key, str) else encryption_key
        
        self.cipher = Fernet(self.encryption_key)
    
    def encrypt_file(self, file_path: str) -> bytes:
        """
        Encrypt a file and return encrypted content.
        
        Args:
            file_path: Path to the file to encrypt
            
        Returns:
            Encrypted file content as bytes
            
        Raises:
            FileNotFoundError: If file does not exist
            IOError: If file cannot be read
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            encrypted_content = self.cipher.encrypt(file_content)
            return encrypted_content
        except IOError as e:
            raise IOError(f"Failed to read file {file_path}: {str(e)}")
    
    def decrypt_file(self, encrypted_content: bytes) -> bytes:
        """
        Decrypt file content.
        
        Args:
            encrypted_content: Encrypted file content as bytes
            
        Returns:
            Decrypted file content as bytes
            
        Raises:
            ValueError: If decryption fails
        """
        try:
            decrypted_content = self.cipher.decrypt(encrypted_content)
            return decrypted_content
        except Exception as e:
            raise ValueError(f"Failed to decrypt file: {str(e)}")
    
    def save_encrypted_file(self, file_path: str, output_path: str) -> str:
        """
        Encrypt a file and save it to a new location.
        
        Args:
            file_path: Path to the original file
            output_path: Path where encrypted file will be saved
            
        Returns:
            Path to the encrypted file
            
        Raises:
            FileNotFoundError: If source file does not exist
            IOError: If file cannot be written
        """
        encrypted_content = self.encrypt_file(file_path)
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            with open(output_path, 'wb') as f:
                f.write(encrypted_content)
            return output_path
        except IOError as e:
            raise IOError(f"Failed to write encrypted file to {output_path}: {str(e)}")
    
    def load_and_decrypt_file(self, encrypted_file_path: str, output_path: str) -> str:
        """
        Load an encrypted file and decrypt it to a new location.
        
        Args:
            encrypted_file_path: Path to the encrypted file
            output_path: Path where decrypted file will be saved
            
        Returns:
            Path to the decrypted file
            
        Raises:
            FileNotFoundError: If encrypted file does not exist
            ValueError: If decryption fails
            IOError: If file cannot be written
        """
        if not os.path.exists(encrypted_file_path):
            raise FileNotFoundError(f"Encrypted file not found: {encrypted_file_path}")
        
        try:
            with open(encrypted_file_path, 'rb') as f:
                encrypted_content = f.read()
            
            decrypted_content = self.decrypt_file(encrypted_content)
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_content)
            
            return output_path
        except IOError as e:
            raise IOError(f"Failed to write decrypted file to {output_path}: {str(e)}")


class FileHashManager:
    """Manages file hashing for integrity verification."""
    
    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
        """
        Calculate hash of a file.
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm (sha256, sha512, md5)
            
        Returns:
            Hex digest of the file hash
            
        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If algorithm is not supported
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if algorithm not in ['sha256', 'sha512', 'md5']:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        hash_obj = hashlib.new(algorithm)
        
        try:
            with open(file_path, 'rb') as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
        except IOError as e:
            raise IOError(f"Failed to read file {file_path}: {str(e)}")
    
    @staticmethod
    def calculate_content_hash(content: bytes, algorithm: str = 'sha256') -> str:
        """
        Calculate hash of content.
        
        Args:
            content: Content as bytes
            algorithm: Hash algorithm (sha256, sha512, md5)
            
        Returns:
            Hex digest of the content hash
            
        Raises:
            ValueError: If algorithm is not supported
        """
        if algorithm not in ['sha256', 'sha512', 'md5']:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(content)
        return hash_obj.hexdigest()
    
    @staticmethod
    def verify_file_hash(file_path: str, expected_hash: str, algorithm: str = 'sha256') -> bool:
        """
        Verify file hash matches expected value.
        
        Args:
            file_path: Path to the file
            expected_hash: Expected hash value
            algorithm: Hash algorithm
            
        Returns:
            True if hash matches, False otherwise
        """
        try:
            actual_hash = FileHashManager.calculate_file_hash(file_path, algorithm)
            return actual_hash == expected_hash
        except (FileNotFoundError, IOError):
            return False


class FileMetadataManager:
    """Manages file metadata recording."""
    
    @staticmethod
    def create_file_metadata(
        file_path: str,
        uploader_id: int,
        uploader_name: str,
        file_type: str,
        original_filename: str
    ) -> dict:
        """
        Create file metadata record.
        
        Args:
            file_path: Path to the file
            uploader_id: ID of the user who uploaded the file
            uploader_name: Name of the user who uploaded the file
            file_type: Type of the file (教案, 教学反思, etc.)
            original_filename: Original filename
            
        Returns:
            Dictionary containing file metadata
            
        Raises:
            FileNotFoundError: If file does not exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_stat = os.stat(file_path)
        file_hash = FileHashManager.calculate_file_hash(file_path)
        
        metadata = {
            'uploader_id': uploader_id,
            'uploader_name': uploader_name,
            'upload_time': datetime.utcnow().isoformat(),
            'file_type': file_type,
            'original_filename': original_filename,
            'file_size': file_stat.st_size,
            'file_hash': file_hash,
            'encrypted_path': None,  # Will be set after encryption
            'is_encrypted': False,
            'encryption_algorithm': 'Fernet',
            'hash_algorithm': 'sha256'
        }
        
        return metadata
    
    @staticmethod
    def update_metadata_with_encryption(
        metadata: dict,
        encrypted_path: str
    ) -> dict:
        """
        Update metadata after file encryption.
        
        Args:
            metadata: Original metadata dictionary
            encrypted_path: Path to the encrypted file
            
        Returns:
            Updated metadata dictionary
        """
        metadata['encrypted_path'] = encrypted_path
        metadata['is_encrypted'] = True
        metadata['encryption_time'] = datetime.utcnow().isoformat()
        return metadata
