"""
Access control module for role-based file access and audit logging.
Implements permission verification and download audit logging.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum


class UserRole(str, Enum):
    """User roles in the system."""
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class FileAccessPermission(str, Enum):
    """File access permission levels."""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    DELETE = "delete"


class AccessControlManager:
    """Manages role-based file access control."""
    
    # Define role-based access rules
    ACCESS_RULES = {
        UserRole.ADMIN: {
            'can_access_all_files': True,
            'can_download': True,
            'can_delete': True,
            'can_modify_permissions': True
        },
        UserRole.TEACHER: {
            'can_access_all_files': False,
            'can_download': True,
            'can_delete': False,
            'can_modify_permissions': False
        },
        UserRole.STUDENT: {
            'can_access_all_files': False,
            'can_download': False,
            'can_delete': False,
            'can_modify_permissions': False
        }
    }
    
    @staticmethod
    def check_file_access(
        user_id: int,
        user_role: UserRole,
        file_uploader_id: int,
        permission_type: FileAccessPermission = FileAccessPermission.READ
    ) -> bool:
        """
        Check if user has permission to access a file.
        
        Args:
            user_id: ID of the user requesting access
            user_role: Role of the user
            file_uploader_id: ID of the user who uploaded the file
            permission_type: Type of permission being requested
            
        Returns:
            True if user has permission, False otherwise
        """
        # Admin can access all files
        if user_role == UserRole.ADMIN:
            return AccessControlManager.ACCESS_RULES[UserRole.ADMIN]['can_download']
        
        # Teacher can only access their own files
        if user_role == UserRole.TEACHER:
            if user_id == file_uploader_id:
                return AccessControlManager.ACCESS_RULES[UserRole.TEACHER]['can_download']
            return False
        
        # Student cannot access files
        if user_role == UserRole.STUDENT:
            return False
        
        return False
    
    @staticmethod
    def can_download_file(user_id: int, user_role: UserRole, file_uploader_id: int) -> bool:
        """
        Check if user can download a file.
        
        Args:
            user_id: ID of the user
            user_role: Role of the user
            file_uploader_id: ID of the file uploader
            
        Returns:
            True if user can download, False otherwise
        """
        return AccessControlManager.check_file_access(
            user_id,
            user_role,
            file_uploader_id,
            FileAccessPermission.READ
        )
    
    @staticmethod
    def can_delete_file(user_id: int, user_role: UserRole, file_uploader_id: int) -> bool:
        """
        Check if user can delete a file.
        
        Args:
            user_id: ID of the user
            user_role: Role of the user
            file_uploader_id: ID of the file uploader
            
        Returns:
            True if user can delete, False otherwise
        """
        # Only admin can delete files
        if user_role == UserRole.ADMIN:
            return AccessControlManager.ACCESS_RULES[UserRole.ADMIN]['can_delete']
        return False
    
    @staticmethod
    def can_modify_permissions(user_id: int, user_role: UserRole) -> bool:
        """
        Check if user can modify file permissions.
        
        Args:
            user_id: ID of the user
            user_role: Role of the user
            
        Returns:
            True if user can modify permissions, False otherwise
        """
        if user_role == UserRole.ADMIN:
            return AccessControlManager.ACCESS_RULES[UserRole.ADMIN]['can_modify_permissions']
        return False


class DownloadAuditLog:
    """Represents a download audit log entry."""
    
    def __init__(
        self,
        file_id: str,
        file_name: str,
        downloader_id: int,
        downloader_name: str,
        downloader_role: UserRole,
        download_time: Optional[datetime] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """
        Initialize download audit log.
        
        Args:
            file_id: ID of the downloaded file
            file_name: Name of the downloaded file
            downloader_id: ID of the user who downloaded
            downloader_name: Name of the user who downloaded
            downloader_role: Role of the user who downloaded
            download_time: Time of download (defaults to now)
            ip_address: IP address of the downloader
            user_agent: User agent of the downloader
        """
        self.file_id = file_id
        self.file_name = file_name
        self.downloader_id = downloader_id
        self.downloader_name = downloader_name
        self.downloader_role = downloader_role
        self.download_time = download_time or datetime.utcnow()
        self.ip_address = ip_address
        self.user_agent = user_agent
    
    def to_dict(self) -> dict:
        """Convert audit log to dictionary."""
        return {
            'file_id': self.file_id,
            'file_name': self.file_name,
            'downloader_id': self.downloader_id,
            'downloader_name': self.downloader_name,
            'downloader_role': self.downloader_role.value,
            'download_time': self.download_time.isoformat(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }


class AuditLogManager:
    """Manages audit logging for file operations."""
    
    def __init__(self):
        """Initialize audit log manager."""
        self.logs: List[DownloadAuditLog] = []
    
    def log_download(
        self,
        file_id: str,
        file_name: str,
        downloader_id: int,
        downloader_name: str,
        downloader_role: UserRole,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> DownloadAuditLog:
        """
        Log a file download operation.
        
        Args:
            file_id: ID of the downloaded file
            file_name: Name of the downloaded file
            downloader_id: ID of the user who downloaded
            downloader_name: Name of the user who downloaded
            downloader_role: Role of the user who downloaded
            ip_address: IP address of the downloader
            user_agent: User agent of the downloader
            
        Returns:
            The created audit log entry
        """
        log_entry = DownloadAuditLog(
            file_id=file_id,
            file_name=file_name,
            downloader_id=downloader_id,
            downloader_name=downloader_name,
            downloader_role=downloader_role,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.logs.append(log_entry)
        return log_entry
    
    def get_file_download_logs(self, file_id: str) -> List[dict]:
        """
        Get all download logs for a specific file.
        
        Args:
            file_id: ID of the file
            
        Returns:
            List of download log dictionaries
        """
        file_logs = [log for log in self.logs if log.file_id == file_id]
        return [log.to_dict() for log in file_logs]
    
    def get_user_download_logs(self, user_id: int) -> List[dict]:
        """
        Get all download logs for a specific user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of download log dictionaries
        """
        user_logs = [log for log in self.logs if log.downloader_id == user_id]
        return [log.to_dict() for log in user_logs]
    
    def get_all_logs(self) -> List[dict]:
        """
        Get all audit logs.
        
        Returns:
            List of all audit log dictionaries
        """
        return [log.to_dict() for log in self.logs]
    
    def clear_logs(self):
        """Clear all audit logs."""
        self.logs.clear()
