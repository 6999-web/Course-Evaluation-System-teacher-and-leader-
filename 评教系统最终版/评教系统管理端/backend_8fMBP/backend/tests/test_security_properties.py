"""
Property-based tests for security module.
Tests encryption, hashing, metadata, and access control functionality.
"""

import os
import tempfile
import pytest
from hypothesis import given, strategies as st, assume
from datetime import datetime

from app.security import (
    FileEncryptionManager,
    FileHashManager,
    FileMetadataManager
)
from app.access_control import (
    AccessControlManager,
    AuditLogManager,
    UserRole,
    FileAccessPermission
)


class TestFileEncryptionProperties:
    """Property-based tests for file encryption."""
    
    @given(st.binary(min_size=1, max_size=10000))
    def test_encryption_decryption_roundtrip(self, content: bytes):
        """
        **Property 29: 文件加密存储**
        
        For any file content, encrypting and then decrypting should return the original content.
        
        **Validates: Requirements 11.1**
        """
        # Create temporary file with content
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Create encryption manager
            manager = FileEncryptionManager()
            
            # Encrypt the file
            encrypted_content = manager.encrypt_file(tmp_path)
            
            # Verify encrypted content is different from original
            assert encrypted_content != content
            
            # Decrypt and verify
            decrypted_content = manager.decrypt_file(encrypted_content)
            assert decrypted_content == content
        finally:
            os.unlink(tmp_path)
    
    @given(st.binary(min_size=1, max_size=10000))
    def test_encrypted_content_is_different(self, content: bytes):
        """
        For any file content, encrypted content should be different from original.
        """
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            manager = FileEncryptionManager()
            encrypted_content = manager.encrypt_file(tmp_path)
            
            # Encrypted content should be different
            assert encrypted_content != content
            
            # Encrypted content should be non-empty
            assert len(encrypted_content) > 0
        finally:
            os.unlink(tmp_path)
    
    @given(st.binary(min_size=1, max_size=10000))
    def test_same_content_produces_different_encryption(self, content: bytes):
        """
        For the same content encrypted with different managers, results should be different
        (due to Fernet's use of random IV).
        """
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            manager1 = FileEncryptionManager()
            manager2 = FileEncryptionManager()
            
            encrypted1 = manager1.encrypt_file(tmp_path)
            encrypted2 = manager2.encrypt_file(tmp_path)
            
            # Different managers should produce different encrypted content
            # (because they have different keys)
            assert encrypted1 != encrypted2
        finally:
            os.unlink(tmp_path)


class TestFileHashProperties:
    """Property-based tests for file hashing."""
    
    @given(st.binary(min_size=1, max_size=10000))
    def test_file_hash_consistency(self, content: bytes):
        """
        **Property 30: 文件元数据记录**
        
        For any file, calculating hash multiple times should produce the same result.
        
        **Validates: Requirements 11.2**
        """
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            hash1 = FileHashManager.calculate_file_hash(tmp_path)
            hash2 = FileHashManager.calculate_file_hash(tmp_path)
            
            assert hash1 == hash2
        finally:
            os.unlink(tmp_path)
    
    @given(st.binary(min_size=1, max_size=10000))
    def test_different_content_produces_different_hash(self, content: bytes):
        """
        For different file contents, hashes should be different.
        """
        assume(len(content) > 0)
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp1:
            tmp1.write(content)
            tmp1_path = tmp1.name
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp2:
            # Create different content
            different_content = content + b'x'
            tmp2.write(different_content)
            tmp2_path = tmp2.name
        
        try:
            hash1 = FileHashManager.calculate_file_hash(tmp1_path)
            hash2 = FileHashManager.calculate_file_hash(tmp2_path)
            
            assert hash1 != hash2
        finally:
            os.unlink(tmp1_path)
            os.unlink(tmp2_path)
    
    @given(st.binary(min_size=1, max_size=10000))
    def test_hash_verification(self, content: bytes):
        """
        For any file, hash verification should work correctly.
        """
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            correct_hash = FileHashManager.calculate_file_hash(tmp_path)
            
            # Verify correct hash
            assert FileHashManager.verify_file_hash(tmp_path, correct_hash)
            
            # Verify incorrect hash
            incorrect_hash = correct_hash[:-1] + ('0' if correct_hash[-1] != '0' else '1')
            assert not FileHashManager.verify_file_hash(tmp_path, incorrect_hash)
        finally:
            os.unlink(tmp_path)


class TestAccessControlProperties:
    """Property-based tests for access control."""
    
    @given(st.integers(min_value=1, max_value=1000))
    def test_admin_can_access_all_files(self, user_id: int):
        """
        **Property 31: 基于角色的文件访问控制**
        
        For any user ID, admin role should always have access to files.
        
        **Validates: Requirements 11.3, 11.4, 11.5**
        """
        # Admin should be able to access any file
        assert AccessControlManager.check_file_access(
            user_id=user_id,
            user_role=UserRole.ADMIN,
            file_uploader_id=999
        )
    
    @given(
        st.integers(min_value=1, max_value=1000),
        st.integers(min_value=1, max_value=1000)
    )
    def test_teacher_can_only_access_own_files(self, user_id: int, uploader_id: int):
        """
        For any teacher user, they should only access files they uploaded.
        """
        can_access = AccessControlManager.check_file_access(
            user_id=user_id,
            user_role=UserRole.TEACHER,
            file_uploader_id=uploader_id
        )
        
        # Teacher can access only if they are the uploader
        assert can_access == (user_id == uploader_id)
    
    @given(st.integers(min_value=1, max_value=1000))
    def test_student_cannot_access_files(self, user_id: int):
        """
        For any student user, they should not have access to files.
        """
        assert not AccessControlManager.check_file_access(
            user_id=user_id,
            user_role=UserRole.STUDENT,
            file_uploader_id=999
        )
    
    @given(st.integers(min_value=1, max_value=1000))
    def test_only_admin_can_delete_files(self, user_id: int):
        """
        For any user, only admin role should be able to delete files.
        """
        # Admin can delete
        assert AccessControlManager.can_delete_file(
            user_id=user_id,
            user_role=UserRole.ADMIN,
            file_uploader_id=999
        )
        
        # Teacher cannot delete
        assert not AccessControlManager.can_delete_file(
            user_id=user_id,
            user_role=UserRole.TEACHER,
            file_uploader_id=user_id
        )
        
        # Student cannot delete
        assert not AccessControlManager.can_delete_file(
            user_id=user_id,
            user_role=UserRole.STUDENT,
            file_uploader_id=999
        )


class TestAuditLogProperties:
    """Property-based tests for audit logging."""
    
    @given(
        st.text(min_size=1, max_size=100),
        st.text(min_size=1, max_size=100),
        st.integers(min_value=1, max_value=1000),
        st.text(min_size=1, max_size=100)
    )
    def test_audit_log_recording(
        self,
        file_id: str,
        file_name: str,
        downloader_id: int,
        downloader_name: str
    ):
        """
        **Property 32: 文件下载审计日志**
        
        For any download operation, audit log should record all details correctly.
        
        **Validates: Requirements 11.6**
        """
        manager = AuditLogManager()
        
        # Log a download
        log_entry = manager.log_download(
            file_id=file_id,
            file_name=file_name,
            downloader_id=downloader_id,
            downloader_name=downloader_name,
            downloader_role=UserRole.ADMIN,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        # Verify log entry contains all information
        assert log_entry.file_id == file_id
        assert log_entry.file_name == file_name
        assert log_entry.downloader_id == downloader_id
        assert log_entry.downloader_name == downloader_name
        assert log_entry.downloader_role == UserRole.ADMIN
        assert log_entry.ip_address == "192.168.1.1"
        assert log_entry.user_agent == "Mozilla/5.0"
    
    @given(
        st.lists(
            st.tuples(
                st.text(min_size=1, max_size=50),
                st.text(min_size=1, max_size=50),
                st.integers(min_value=1, max_value=100)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_audit_log_retrieval_by_file(self, downloads):
        """
        For any set of downloads, retrieving logs by file_id should return only that file's logs.
        """
        manager = AuditLogManager()
        
        # Log multiple downloads
        for file_id, file_name, downloader_id in downloads:
            manager.log_download(
                file_id=file_id,
                file_name=file_name,
                downloader_id=downloader_id,
                downloader_name=f"User{downloader_id}",
                downloader_role=UserRole.ADMIN
            )
        
        # Get logs for first file
        first_file_id = downloads[0][0]
        file_logs = manager.get_file_download_logs(first_file_id)
        
        # All returned logs should be for the requested file
        for log in file_logs:
            assert log['file_id'] == first_file_id
    
    @given(
        st.lists(
            st.tuples(
                st.text(min_size=1, max_size=50),
                st.text(min_size=1, max_size=50),
                st.integers(min_value=1, max_value=100)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_audit_log_retrieval_by_user(self, downloads):
        """
        For any set of downloads, retrieving logs by user_id should return only that user's logs.
        """
        manager = AuditLogManager()
        
        # Log multiple downloads
        for file_id, file_name, downloader_id in downloads:
            manager.log_download(
                file_id=file_id,
                file_name=file_name,
                downloader_id=downloader_id,
                downloader_name=f"User{downloader_id}",
                downloader_role=UserRole.ADMIN
            )
        
        # Get logs for first user
        first_user_id = downloads[0][2]
        user_logs = manager.get_user_download_logs(first_user_id)
        
        # All returned logs should be for the requested user
        for log in user_logs:
            assert log['downloader_id'] == first_user_id
