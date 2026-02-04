"""
Unit tests for security module.
Tests file encryption, decryption, hashing, metadata, and access control.
"""

import os
import tempfile
import pytest
from cryptography.fernet import Fernet

from app.security import (
    FileEncryptionManager,
    FileHashManager,
    FileMetadataManager
)
from app.access_control import (
    AccessControlManager,
    AuditLogManager,
    UserRole,
    FileAccessPermission,
    DownloadAuditLog
)


class TestFileEncryptionManager:
    """Unit tests for FileEncryptionManager."""
    
    def test_initialization_with_generated_key(self):
        """Test initialization with auto-generated key."""
        manager = FileEncryptionManager()
        assert manager.encryption_key is not None
        assert manager.cipher is not None
    
    def test_initialization_with_provided_key(self):
        """Test initialization with provided key."""
        key = Fernet.generate_key()
        manager = FileEncryptionManager(key.decode())
        assert manager.encryption_key == key
    
    def test_encrypt_file_success(self):
        """Test successful file encryption."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = b"Test content for encryption"
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            manager = FileEncryptionManager()
            encrypted = manager.encrypt_file(tmp_path)
            
            assert encrypted != content
            assert len(encrypted) > 0
        finally:
            os.unlink(tmp_path)
    
    def test_encrypt_file_not_found(self):
        """Test encryption with non-existent file."""
        manager = FileEncryptionManager()
        
        with pytest.raises(FileNotFoundError):
            manager.encrypt_file("/nonexistent/path/file.txt")
    
    def test_decrypt_file_success(self):
        """Test successful file decryption."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = b"Test content for decryption"
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            manager = FileEncryptionManager()
            encrypted = manager.encrypt_file(tmp_path)
            decrypted = manager.decrypt_file(encrypted)
            
            assert decrypted == content
        finally:
            os.unlink(tmp_path)
    
    def test_decrypt_invalid_content(self):
        """Test decryption with invalid content."""
        manager = FileEncryptionManager()
        
        with pytest.raises(ValueError):
            manager.decrypt_file(b"invalid encrypted content")
    
    def test_save_encrypted_file(self):
        """Test saving encrypted file."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = b"Test content"
            tmp.write(content)
            tmp_path = tmp.name
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "encrypted.bin")
            
            try:
                manager = FileEncryptionManager()
                result = manager.save_encrypted_file(tmp_path, output_path)
                
                assert result == output_path
                assert os.path.exists(output_path)
                
                # Verify encrypted file can be decrypted
                with open(output_path, 'rb') as f:
                    encrypted_content = f.read()
                decrypted = manager.decrypt_file(encrypted_content)
                assert decrypted == content
            finally:
                os.unlink(tmp_path)
    
    def test_load_and_decrypt_file(self):
        """Test loading and decrypting file."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = b"Test content for load and decrypt"
            tmp.write(content)
            tmp_path = tmp.name
        
        with tempfile.TemporaryDirectory() as tmpdir:
            encrypted_path = os.path.join(tmpdir, "encrypted.bin")
            decrypted_path = os.path.join(tmpdir, "decrypted.txt")
            
            try:
                manager = FileEncryptionManager()
                
                # First encrypt the file
                manager.save_encrypted_file(tmp_path, encrypted_path)
                
                # Then decrypt it
                result = manager.load_and_decrypt_file(encrypted_path, decrypted_path)
                
                assert result == decrypted_path
                assert os.path.exists(decrypted_path)
                
                # Verify decrypted content
                with open(decrypted_path, 'rb') as f:
                    decrypted_content = f.read()
                assert decrypted_content == content
            finally:
                os.unlink(tmp_path)


class TestFileHashManager:
    """Unit tests for FileHashManager."""
    
    def test_calculate_file_hash_sha256(self):
        """Test SHA256 hash calculation."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = b"Test content for hashing"
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            hash_value = FileHashManager.calculate_file_hash(tmp_path, 'sha256')
            
            assert isinstance(hash_value, str)
            assert len(hash_value) == 64  # SHA256 produces 64 hex characters
        finally:
            os.unlink(tmp_path)
    
    def test_calculate_file_hash_sha512(self):
        """Test SHA512 hash calculation."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = b"Test content"
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            hash_value = FileHashManager.calculate_file_hash(tmp_path, 'sha512')
            
            assert isinstance(hash_value, str)
            assert len(hash_value) == 128  # SHA512 produces 128 hex characters
        finally:
            os.unlink(tmp_path)
    
    def test_calculate_file_hash_md5(self):
        """Test MD5 hash calculation."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = b"Test content"
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            hash_value = FileHashManager.calculate_file_hash(tmp_path, 'md5')
            
            assert isinstance(hash_value, str)
            assert len(hash_value) == 32  # MD5 produces 32 hex characters
        finally:
            os.unlink(tmp_path)
    
    def test_calculate_file_hash_not_found(self):
        """Test hash calculation with non-existent file."""
        with pytest.raises(FileNotFoundError):
            FileHashManager.calculate_file_hash("/nonexistent/file.txt")
    
    def test_calculate_file_hash_invalid_algorithm(self):
        """Test hash calculation with invalid algorithm."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"content")
            tmp_path = tmp.name
        
        try:
            with pytest.raises(ValueError):
                FileHashManager.calculate_file_hash(tmp_path, 'invalid_algo')
        finally:
            os.unlink(tmp_path)
    
    def test_calculate_content_hash(self):
        """Test content hash calculation."""
        content = b"Test content"
        hash_value = FileHashManager.calculate_content_hash(content)
        
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # SHA256 default
    
    def test_verify_file_hash_success(self):
        """Test successful hash verification."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = b"Test content"
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            correct_hash = FileHashManager.calculate_file_hash(tmp_path)
            assert FileHashManager.verify_file_hash(tmp_path, correct_hash)
        finally:
            os.unlink(tmp_path)
    
    def test_verify_file_hash_failure(self):
        """Test hash verification with incorrect hash."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = b"Test content"
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            incorrect_hash = "0" * 64
            assert not FileHashManager.verify_file_hash(tmp_path, incorrect_hash)
        finally:
            os.unlink(tmp_path)


class TestFileMetadataManager:
    """Unit tests for FileMetadataManager."""
    
    def test_create_file_metadata(self):
        """Test file metadata creation."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = b"Test content"
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            metadata = FileMetadataManager.create_file_metadata(
                file_path=tmp_path,
                uploader_id=1,
                uploader_name="Test User",
                file_type="教案",
                original_filename="test.docx"
            )
            
            assert metadata['uploader_id'] == 1
            assert metadata['uploader_name'] == "Test User"
            assert metadata['file_type'] == "教案"
            assert metadata['original_filename'] == "test.docx"
            assert metadata['file_size'] == len(content)
            assert metadata['file_hash'] is not None
            assert metadata['is_encrypted'] is False
        finally:
            os.unlink(tmp_path)
    
    def test_create_file_metadata_not_found(self):
        """Test metadata creation with non-existent file."""
        with pytest.raises(FileNotFoundError):
            FileMetadataManager.create_file_metadata(
                file_path="/nonexistent/file.txt",
                uploader_id=1,
                uploader_name="Test User",
                file_type="教案",
                original_filename="test.docx"
            )
    
    def test_update_metadata_with_encryption(self):
        """Test updating metadata after encryption."""
        metadata = {
            'uploader_id': 1,
            'uploader_name': "Test User",
            'file_type': "教案",
            'original_filename': "test.docx",
            'file_size': 1024,
            'file_hash': "abc123",
            'is_encrypted': False
        }
        
        updated = FileMetadataManager.update_metadata_with_encryption(
            metadata,
            "/path/to/encrypted/file.bin"
        )
        
        assert updated['encrypted_path'] == "/path/to/encrypted/file.bin"
        assert updated['is_encrypted'] is True
        assert 'encryption_time' in updated


class TestAccessControlManager:
    """Unit tests for AccessControlManager."""
    
    def test_admin_access_all_files(self):
        """Test admin can access all files."""
        assert AccessControlManager.check_file_access(
            user_id=1,
            user_role=UserRole.ADMIN,
            file_uploader_id=999
        )
    
    def test_teacher_access_own_files(self):
        """Test teacher can access own files."""
        assert AccessControlManager.check_file_access(
            user_id=1,
            user_role=UserRole.TEACHER,
            file_uploader_id=1
        )
    
    def test_teacher_cannot_access_others_files(self):
        """Test teacher cannot access other's files."""
        assert not AccessControlManager.check_file_access(
            user_id=1,
            user_role=UserRole.TEACHER,
            file_uploader_id=2
        )
    
    def test_student_cannot_access_files(self):
        """Test student cannot access files."""
        assert not AccessControlManager.check_file_access(
            user_id=1,
            user_role=UserRole.STUDENT,
            file_uploader_id=1
        )
    
    def test_can_download_file_admin(self):
        """Test admin can download files."""
        assert AccessControlManager.can_download_file(
            user_id=1,
            user_role=UserRole.ADMIN,
            file_uploader_id=999
        )
    
    def test_can_download_file_teacher_own(self):
        """Test teacher can download own files."""
        assert AccessControlManager.can_download_file(
            user_id=1,
            user_role=UserRole.TEACHER,
            file_uploader_id=1
        )
    
    def test_can_delete_file_admin(self):
        """Test only admin can delete files."""
        assert AccessControlManager.can_delete_file(
            user_id=1,
            user_role=UserRole.ADMIN,
            file_uploader_id=999
        )
    
    def test_cannot_delete_file_teacher(self):
        """Test teacher cannot delete files."""
        assert not AccessControlManager.can_delete_file(
            user_id=1,
            user_role=UserRole.TEACHER,
            file_uploader_id=1
        )
    
    def test_can_modify_permissions_admin(self):
        """Test only admin can modify permissions."""
        assert AccessControlManager.can_modify_permissions(
            user_id=1,
            user_role=UserRole.ADMIN
        )
    
    def test_cannot_modify_permissions_teacher(self):
        """Test teacher cannot modify permissions."""
        assert not AccessControlManager.can_modify_permissions(
            user_id=1,
            user_role=UserRole.TEACHER
        )


class TestDownloadAuditLog:
    """Unit tests for DownloadAuditLog."""
    
    def test_create_audit_log(self):
        """Test creating audit log entry."""
        log = DownloadAuditLog(
            file_id="file_123",
            file_name="test.pdf",
            downloader_id=1,
            downloader_name="Test User",
            downloader_role=UserRole.ADMIN,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        assert log.file_id == "file_123"
        assert log.file_name == "test.pdf"
        assert log.downloader_id == 1
        assert log.downloader_name == "Test User"
        assert log.downloader_role == UserRole.ADMIN
        assert log.ip_address == "192.168.1.1"
        assert log.user_agent == "Mozilla/5.0"
    
    def test_audit_log_to_dict(self):
        """Test converting audit log to dictionary."""
        log = DownloadAuditLog(
            file_id="file_123",
            file_name="test.pdf",
            downloader_id=1,
            downloader_name="Test User",
            downloader_role=UserRole.ADMIN
        )
        
        log_dict = log.to_dict()
        
        assert log_dict['file_id'] == "file_123"
        assert log_dict['file_name'] == "test.pdf"
        assert log_dict['downloader_id'] == 1
        assert log_dict['downloader_name'] == "Test User"
        assert log_dict['downloader_role'] == "admin"


class TestAuditLogManager:
    """Unit tests for AuditLogManager."""
    
    def test_log_download(self):
        """Test logging a download."""
        manager = AuditLogManager()
        
        log = manager.log_download(
            file_id="file_123",
            file_name="test.pdf",
            downloader_id=1,
            downloader_name="Test User",
            downloader_role=UserRole.ADMIN,
            ip_address="192.168.1.1"
        )
        
        assert log.file_id == "file_123"
        assert log.downloader_id == 1
    
    def test_get_file_download_logs(self):
        """Test retrieving logs by file ID."""
        manager = AuditLogManager()
        
        # Log multiple downloads
        manager.log_download("file_1", "test1.pdf", 1, "User1", UserRole.ADMIN)
        manager.log_download("file_1", "test1.pdf", 2, "User2", UserRole.ADMIN)
        manager.log_download("file_2", "test2.pdf", 1, "User1", UserRole.ADMIN)
        
        # Get logs for file_1
        logs = manager.get_file_download_logs("file_1")
        
        assert len(logs) == 2
        assert all(log['file_id'] == "file_1" for log in logs)
    
    def test_get_user_download_logs(self):
        """Test retrieving logs by user ID."""
        manager = AuditLogManager()
        
        # Log multiple downloads
        manager.log_download("file_1", "test1.pdf", 1, "User1", UserRole.ADMIN)
        manager.log_download("file_2", "test2.pdf", 1, "User1", UserRole.ADMIN)
        manager.log_download("file_3", "test3.pdf", 2, "User2", UserRole.ADMIN)
        
        # Get logs for user 1
        logs = manager.get_user_download_logs(1)
        
        assert len(logs) == 2
        assert all(log['downloader_id'] == 1 for log in logs)
    
    def test_get_all_logs(self):
        """Test retrieving all logs."""
        manager = AuditLogManager()
        
        # Log multiple downloads
        manager.log_download("file_1", "test1.pdf", 1, "User1", UserRole.ADMIN)
        manager.log_download("file_2", "test2.pdf", 2, "User2", UserRole.ADMIN)
        
        logs = manager.get_all_logs()
        
        assert len(logs) == 2
    
    def test_clear_logs(self):
        """Test clearing all logs."""
        manager = AuditLogManager()
        
        # Log downloads
        manager.log_download("file_1", "test1.pdf", 1, "User1", UserRole.ADMIN)
        manager.log_download("file_2", "test2.pdf", 2, "User2", UserRole.ADMIN)
        
        assert len(manager.get_all_logs()) == 2
        
        # Clear logs
        manager.clear_logs()
        
        assert len(manager.get_all_logs()) == 0
