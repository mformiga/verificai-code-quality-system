"""
Supabase client for AVALIA Streamlit Frontend
This module provides utilities for integrating with Supabase services
"""

import os
from typing import Optional, Dict, Any, List
import streamlit as st
from supabase import create_client, Client


class SupabaseClient:
    """Supabase client wrapper for Streamlit"""

    def __init__(self):
        self._client: Optional[Client] = None

    @property
    def client(self) -> Client:
        """Get or create Supabase client"""
        if self._client is None:
            self._initialize_client()
        return self._client

    def _initialize_client(self):
        """Initialize Supabase client from secrets or environment variables"""
        try:
            # Try to get from Streamlit secrets first
            if hasattr(st, 'secrets') and 'supabase' in st.secrets:
                supabase_config = st.secrets['supabase']
                url = supabase_config['url']
                key = supabase_config['anon_key']
            else:
                # Fallback to environment variables
                url = os.getenv("SUPABASE_URL")
                key = os.getenv("SUPABASE_ANON_KEY")

            if not url or not key:
                raise ValueError("Supabase URL and Anon Key are required")

            self._client = create_client(url, key)

        except Exception as e:
            st.error(f"Failed to initialize Supabase client: {str(e)}")
            raise e

    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in user"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {
                "success": True,
                "user": response.user,
                "session": response.session
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def sign_up(self, email: str, password: str, user_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Sign up new user"""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_data or {}
                }
            })
            return {
                "success": True,
                "user": response.user,
                "session": response.session
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def sign_out(self) -> Dict[str, Any]:
        """Sign out current user"""
        try:
            self.client.auth.sign_out()
            return {"success": True}
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""
        try:
            user_response = self.client.auth.get_user()
            if user_response.user is not None:
                return {
                    "id": user_response.user.id,
                    "email": user_response.user.email,
                    "user_metadata": user_response.user.user_metadata
                }
            return None
        except Exception:
            return None

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

    # Profile Management
    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        try:
            response = self.client.table("profiles").select("*").eq("id", user_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception:
            return None

    def update_profile(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        try:
            response = self.client.table("profiles").update(data).eq("id", user_id).execute()
            return {
                "success": True,
                "data": response.data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # Analyses
    def get_analyses(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user analyses"""
        try:
            response = self.client.table("analyses")\
                .select("*, analyses(*), prompts(*)")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            return response.data
        except Exception:
            return []

    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get specific analysis"""
        try:
            response = self.client.table("analyses")\
                .select("*, analysis_results(*), prompts(*)")\
                .eq("id", analysis_id)\
                .execute()
            if response.data:
                return response.data[0]
            return None
        except Exception:
            return None

    def create_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new analysis"""
        try:
            response = self.client.table("analyses").insert(analysis_data).execute()
            return {
                "success": True,
                "data": response.data[0] if response.data else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # Prompts
    def get_prompts(self) -> List[Dict[str, Any]]:
        """Get all available prompts"""
        try:
            response = self.client.table("prompts")\
                .select("*")\
                .eq("status", "active")\
                .execute()
            return response.data
        except Exception:
            return []

    def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Get specific prompt"""
        try:
            response = self.client.table("prompts").select("*").eq("id", prompt_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception:
            return None

    # General Criteria
    def get_general_criteria(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's general analysis criteria"""
        try:
            response = self.client.table("general_criteria")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("is_active", True)\
                .order("order")\
                .execute()
            return response.data
        except Exception:
            return []

    def create_general_criteria(self, criteria_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new general criteria"""
        try:
            response = self.client.table("general_criteria").insert(criteria_data).execute()
            return {
                "success": True,
                "data": response.data[0] if response.data else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def update_general_criteria(self, criteria_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update general criteria"""
        try:
            response = self.client.table("general_criteria").update(data).eq("id", criteria_id).execute()
            return {
                "success": True,
                "data": response.data[0] if response.data else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def delete_general_criteria(self, criteria_id: str) -> Dict[str, Any]:
        """Delete general criteria"""
        try:
            response = self.client.table("general_criteria").delete().eq("id", criteria_id).execute()
            return {
                "success": True,
                "data": response.data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # Files
    def upload_file(self, bucket: str, path: str, file_content: bytes, content_type: str) -> Dict[str, Any]:
        """Upload file to Supabase storage"""
        try:
            file_options = {"content-type": content_type}
            response = self.client.storage.from_(bucket).upload(path, file_content, file_options)
            return {
                "success": True,
                "data": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_file_url(self, bucket: str, path: str) -> str:
        """Get public URL for file"""
        try:
            return self.client.storage.from_(bucket).get_public_url(path)
        except Exception:
            return ""

    def delete_file(self, bucket: str, path: str) -> Dict[str, Any]:
        """Delete file from storage"""
        try:
            response = self.client.storage.from_(bucket).remove([path])
            return {
                "success": True,
                "data": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def list_files(self, bucket: str, prefix: str = "") -> List[Dict[str, Any]]:
        """List files in storage"""
        try:
            response = self.client.storage.from_(bucket).list(prefix)
            return response
        except Exception:
            return []


# Global instance
supabase_client = SupabaseClient()


# Streamlit session state utilities
def get_current_user_from_session() -> Optional[Dict[str, Any]]:
    """Get current user from Streamlit session state"""
    if "user" in st.session_state and st.session_state.user:
        return st.session_state.user
    return None


def set_user_in_session(user_data: Optional[Dict[str, Any]]):
    """Set user data in Streamlit session state"""
    st.session_state.user = user_data


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return get_current_user_from_session() is not None


def require_auth():
    """Require authentication - redirect to login if not authenticated"""
    if not is_authenticated():
        st.switch_page("pages/auth.py")


def get_user_profile_from_session() -> Optional[Dict[str, Any]]:
    """Get user profile from session state"""
    if "user_profile" in st.session_state and st.session_state.user_profile:
        return st.session_state.user_profile
    return None


def set_user_profile_in_session(profile_data: Optional[Dict[str, Any]]):
    """Set user profile in session state"""
    st.session_state.user_profile = profile_data


# Utility functions
def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 Bytes"

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def get_status_color(status: str) -> str:
    """Get color for analysis status"""
    status_colors = {
        "pending": "🟡",
        "processing": "🔄",
        "completed": "✅",
        "failed": "❌",
        "cancelled": "⏹️"
    }
    return status_colors.get(status, "❓")


def get_role_display_name(role: str) -> str:
    """Get display name for user role"""
    role_names = {
        "ADMIN": "Administrator",
        "QA_ENGINEER": "QA Engineer",
        "DEVELOPER": "Developer",
        "VIEWER": "Viewer"
    }
    return role_names.get(role, "Unknown")