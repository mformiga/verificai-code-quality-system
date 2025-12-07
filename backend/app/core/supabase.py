"""
Supabase integration for AVALIA Backend
This module provides utilities for integrating with Supabase services
"""

import os
from typing import Optional, Dict, Any
import supabase
from supabase import create_client, Client
from pydantic import Field

from app.core.config import settings


class SupabaseConfig:
    """Supabase configuration settings"""

    def __init__(self):
        self.supabase_url: str = os.getenv("SUPABASE_URL", "")
        self.supabase_key: str = os.getenv("SUPABASE_ANON_KEY", "")
        self.supabase_service_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        self.supabase_project_ref: str = os.getenv("SUPABASE_PROJECT_REF", "")

    @property
    def is_configured(self) -> bool:
        """Check if Supabase is properly configured"""
        return bool(self.supabase_url and self.supabase_key)


# Global Supabase configuration instance
supabase_config = SupabaseConfig()


def get_supabase_client(service_role: bool = False) -> Optional[Client]:
    """
    Get a Supabase client instance

    Args:
        service_role: If True, use service role key for admin operations

    Returns:
        Supabase client instance or None if not configured
    """
    if not supabase_config.is_configured:
        return None

    key = supabase_config.supabase_service_key if service_role else supabase_config.supabase_key

    try:
        return create_client(supabase_config.supabase_url, key)
    except Exception as e:
        print(f"Failed to create Supabase client: {e}")
        return None


def get_supabase_admin_client() -> Optional[Client]:
    """
    Get a Supabase client with service role key for admin operations

    Returns:
        Supabase admin client instance or None if not configured
    """
    return get_supabase_client(service_role=True)


class SupabaseAuth:
    """Supabase authentication utilities"""

    def __init__(self, client: Client):
        self.client = client

    def sign_up(self, email: str, password: str, user_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Sign up a new user"""
        try:
            auth_response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_data or {}
                }
            })
            return {
                "success": True,
                "user": auth_response.user,
                "session": auth_response.session
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in a user"""
        try:
            auth_response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {
                "success": True,
                "user": auth_response.user,
                "session": auth_response.session
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def sign_in_with_token(self, token: str) -> Dict[str, Any]:
        """Sign in with a token"""
        try:
            auth_response = self.client.auth.sign_in_with_token({
                "access_token": token
            })
            return {
                "success": True,
                "user": auth_response.user,
                "session": auth_response.session
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def sign_out(self, token: str) -> Dict[str, Any]:
        """Sign out a user"""
        try:
            self.client.auth.sign_out(token)
            return {"success": True}
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_user(self, token: str) -> Dict[str, Any]:
        """Get user information from token"""
        try:
            user_response = self.client.auth.get_user(token)
            return {
                "success": True,
                "user": user_response.user
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def reset_password(self, email: str) -> Dict[str, Any]:
        """Send password reset email"""
        try:
            self.client.auth.reset_password_for_email(email)
            return {"success": True}
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def update_user(self, token: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user information"""
        try:
            user_response = self.client.auth.update_user(token, user_data)
            return {
                "success": True,
                "user": user_response.user
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class SupabaseStorage:
    """Supabase storage utilities"""

    def __init__(self, client: Client):
        self.client = client

    def upload_file(self, bucket: str, path: str, file_content: bytes, file_options: Optional[Dict] = None) -> Dict[str, Any]:
        """Upload a file to Supabase storage"""
        try:
            storage_response = self.client.storage.from_(bucket).upload(
                path, file_content, file_options or {}
            )
            return {
                "success": True,
                "data": storage_response
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def download_file(self, bucket: str, path: str) -> Dict[str, Any]:
        """Download a file from Supabase storage"""
        try:
            file_content = self.client.storage.from_(bucket).download(path)
            return {
                "success": True,
                "data": file_content
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def delete_file(self, bucket: str, path: str) -> Dict[str, Any]:
        """Delete a file from Supabase storage"""
        try:
            storage_response = self.client.storage.from_(bucket).remove([path])
            return {
                "success": True,
                "data": storage_response
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_public_url(self, bucket: str, path: str) -> str:
        """Get public URL for a file"""
        try:
            return self.client.storage.from_(bucket).get_public_url(path)
        except Exception:
            return ""

    def list_files(self, bucket: str, prefix: str = "") -> Dict[str, Any]:
        """List files in a bucket with optional prefix"""
        try:
            files = self.client.storage.from_(bucket).list(prefix)
            return {
                "success": True,
                "data": files
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class SupabaseDatabase:
    """Supabase database utilities"""

    def __init__(self, client: Client):
        self.client = client

    def select(self, table: str, columns: str = "*", filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Select records from a table"""
        try:
            query = self.client.table(table).select(columns)

            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.in_(key, value)
                    else:
                        query = query.eq(key, value)

            response = query.execute()
            return {
                "success": True,
                "data": response.data,
                "count": len(response.data)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def insert(self, table: str, data: Dict[str, Any] or list) -> Dict[str, Any]:
        """Insert record(s) into a table"""
        try:
            response = self.client.table(table).insert(data).execute()
            return {
                "success": True,
                "data": response.data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def update(self, table: str, data: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Update records in a table"""
        try:
            query = self.client.table(table).update(data)

            for key, value in filters.items():
                query = query.eq(key, value)

            response = query.execute()
            return {
                "success": True,
                "data": response.data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def delete(self, table: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Delete records from a table"""
        try:
            query = self.client.table(table).delete()

            for key, value in filters.items():
                query = query.eq(key, value)

            response = query.execute()
            return {
                "success": True,
                "data": response.data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def rpc(self, function_name: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Call a PostgreSQL function"""
        try:
            response = self.client.rpc(function_name, params or {}).execute()
            return {
                "success": True,
                "data": response.data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def get_supabase_services(service_role: bool = False):
    """
    Get all Supabase service instances

    Args:
        service_role: If True, use service role key for admin operations

    Returns:
        Dictionary with Supabase service instances or None if not configured
    """
    client = get_supabase_client(service_role)
    if not client:
        return None

    return {
        "client": client,
        "auth": SupabaseAuth(client),
        "storage": SupabaseStorage(client),
        "database": SupabaseDatabase(client)
    }


# Helper functions for specific operations
def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user profile by ID"""
    services = get_supabase_services()
    if not services:
        return None

    result = services["database"].select("profiles", "*", {"id": user_id})
    if result["success"] and result["data"]:
        return result["data"][0]
    return None


def update_user_profile(user_id: str, profile_data: Dict[str, Any]) -> bool:
    """Update user profile"""
    services = get_supabase_services()
    if not services:
        return False

    result = services["database"].update("profiles", profile_data, {"id": user_id})
    return result["success"]


def upload_user_file(user_id: str, file_name: str, file_content: bytes, bucket: str = "code-files") -> Dict[str, Any]:
    """Upload a file for a user"""
    services = get_supabase_services()
    if not services:
        return {"success": False, "error": "Supabase not configured"}

    # Create user-specific path
    file_path = f"{user_id}/{file_name}"

    return services["storage"].upload_file(bucket, file_path, file_content)


def delete_user_file(user_id: str, file_name: str, bucket: str = "code-files") -> Dict[str, Any]:
    """Delete a file for a user"""
    services = get_supabase_services()
    if not services:
        return {"success": False, "error": "Supabase not configured"}

    file_path = f"{user_id}/{file_name}"
    return services["storage"].delete_file(bucket, file_path)


def get_user_files(user_id: str, bucket: str = "code-files") -> Dict[str, Any]:
    """Get all files for a user"""
    services = get_supabase_services()
    if not services:
        return {"success": False, "error": "Supabase not configured"}

    return services["storage"].list_files(bucket, f"{user_id}/")


def verify_supabase_connection() -> Dict[str, Any]:
    """Verify Supabase connection and configuration"""
    try:
        services = get_supabase_services()
        if not services:
            return {
                "connected": False,
                "error": "Supabase not configured"
            }

        # Test database connection
        test_result = services["database"].select("profiles", "count", limit=1)

        return {
            "connected": test_result["success"],
            "project_ref": supabase_config.supabase_project_ref,
            "url": supabase_config.supabase_url,
            "error": test_result.get("error") if not test_result["success"] else None
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }