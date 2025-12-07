"""
Supabase Client for AVALIA Code Analysis Application
Integrates Streamlit with Supabase for authentication, database, and storage
"""

import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client
import json
from datetime import datetime
from typing import Optional, Dict, List, Any

# Load environment variables
# Try to load from .env.supabase first (local development), then use Streamlit secrets
try:
    load_dotenv('.env.supabase')
except:
    pass  # dotenv not available, will use Streamlit secrets

class SupabaseClient:
    """Supabase client wrapper for Streamlit integration"""

    def __init__(self):
        """Initialize Supabase client"""
        # Try environment variables first, then Streamlit secrets
        self.url = os.getenv("SUPABASE_URL") or st.secrets.get("supabase", {}).get("SUPABASE_URL", "")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY") or st.secrets.get("supabase", {}).get("SUPABASE_ANON_KEY", "")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or st.secrets.get("supabase", {}).get("SUPABASE_SERVICE_ROLE_KEY", "")

        if not self.url or not self.anon_key:
            st.error("⚠️ Configuração do Supabase não encontrada. Configure as variáveis SUPABASE_URL e SUPABASE_ANON_KEY.")
            self.client = None
        else:
            try:
                self.client: Client = create_client(self.url, self.anon_key)
                st.success("✅ Conectado ao Supabase com sucesso!")
            except Exception as e:
                st.error(f"❌ Erro ao conectar ao Supabase: {str(e)}")
                self.client = None

    def sign_up(self, email: str, password: str, username: str = None) -> Dict[str, Any]:
        """Register new user"""
        if not self.client:
            return {"error": "Cliente Supabase não inicializado"}

        try:
            # Sign up user
            auth_response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "username": username or email.split('@')[0]
                    }
                }
            })

            if auth_response.user:
                return {"success": True, "user": auth_response.user}
            else:
                return {"error": "Falha no registro"}

        except Exception as e:
            return {"error": f"Erro no registro: {str(e)}"}

    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in user"""
        if not self.client:
            return {"error": "Cliente Supabase não inicializado"}

        try:
            auth_response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if auth_response.user:
                # Store session in Streamlit session state
                st.session_state.supabase_session = auth_response.session
                st.session_state.user = auth_response.user
                return {"success": True, "user": auth_response.user, "session": auth_response.session}
            else:
                return {"error": "Falha no login"}

        except Exception as e:
            return {"error": f"Erro no login: {str(e)}"}

    def sign_out(self) -> Dict[str, Any]:
        """Sign out user"""
        if not self.client:
            return {"error": "Cliente Supabase não inicializado"}

        try:
            self.client.auth.sign_out()
            # Clear session state
            if 'supabase_session' in st.session_state:
                del st.session_state.supabase_session
            if 'user' in st.session_state:
                del st.session_state.user
            return {"success": True}
        except Exception as e:
            return {"error": f"Erro no logout: {str(e)}"}

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""
        if 'user' in st.session_state:
            return st.session_state.user
        return None

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return 'user' in st.session_state and st.session_state.user is not None

    def upload_file(self, file_content: bytes, file_name: str, bucket: str = "code-files") -> Dict[str, Any]:
        """Upload file to Supabase Storage"""
        if not self.client:
            return {"error": "Cliente Supabase não inicializado"}

        if not self.is_authenticated():
            return {"error": "Usuário não autenticado"}

        try:
            user_id = self.get_current_user()['id']
            file_path = f"{user_id}/{file_name}"

            # Upload file
            storage_response = self.client.storage.from_(bucket).upload(file_path, file_content)

            if storage_response:
                # Get public URL
                public_url = self.client.storage.from_(bucket).get_public_url(file_path)

                # Save file metadata to database
                file_data = {
                    "user_id": user_id,
                    "file_name": file_name,
                    "file_path": file_path,
                    "bucket": bucket,
                    "file_size": len(file_content),
                    "mime_type": self._get_mime_type(file_name)
                }

                db_response = self.client.table("uploaded_files").insert(file_data).execute()

                return {
                    "success": True,
                    "file_path": file_path,
                    "public_url": public_url,
                    "metadata": db_response.data[0] if db_response.data else None
                }
            else:
                return {"error": "Falha no upload do arquivo"}

        except Exception as e:
            return {"error": f"Erro no upload: {str(e)}"}

    def save_analysis_result(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save analysis result to database"""
        if not self.client:
            return {"error": "Cliente Supabase não inicializado"}

        if not self.is_authenticated():
            return {"error": "Usuário não autenticado"}

        try:
            user_id = self.get_current_user()['id']

            # Prepare analysis data
            analysis_record = {
                "user_id": user_id,
                "file_path": analysis_data.get("file_path", ""),
                "analysis_type": analysis_data.get("analysis_type", "local"),
                "criteria_count": len(analysis_data.get("criteria_results", [])),
                "violation_count": sum(len(cr.get("violations", [])) for cr in analysis_data.get("criteria_results", [])),
                "analysis_data": analysis_data,
                "created_at": datetime.now().isoformat()
            }

            # Insert analysis record
            response = self.client.table("analyses").insert(analysis_record).execute()

            if response.data:
                analysis_id = response.data[0]["id"]

                # Save detailed criteria results
                for criterion_result in analysis_data.get("criteria_results", []):
                    criterion_record = {
                        "analysis_id": analysis_id,
                        "criterion_id": criterion_result.get("criterion_id", ""),
                        "analysis_text": criterion_result.get("analysis_text", ""),
                        "violations": criterion_result.get("violations", []),
                        "violation_count": len(criterion_result.get("violations", []))
                    }
                    self.client.table("analysis_results").insert(criterion_record).execute()

                return {"success": True, "analysis_id": analysis_id}
            else:
                return {"error": "Falha ao salvar análise"}

        except Exception as e:
            return {"error": f"Erro ao salvar análise: {str(e)}"}

    def get_user_analyses(self) -> List[Dict[str, Any]]:
        """Get user's analysis history"""
        if not self.client or not self.is_authenticated():
            return []

        try:
            user_id = self.get_current_user()['id']
            response = self.client.table("analyses").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Erro ao carregar análises: {str(e)}")
            return []

    def get_analysis_details(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed analysis results"""
        if not self.client or not self.is_authenticated():
            return None

        try:
            # Get main analysis record
            main_response = self.client.table("analyses").select("*").eq("id", analysis_id).single().execute()

            if main_response.data:
                # Get detailed criteria results
                criteria_response = self.client.table("analysis_results").select("*").eq("analysis_id", analysis_id).execute()

                analysis_data = main_response.data
                analysis_data["detailed_results"] = criteria_response.data if criteria_response.data else []

                return analysis_data
            return None
        except Exception as e:
            st.error(f"Erro ao carregar detalhes da análise: {str(e)}")
            return None

    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type based on file extension"""
        extension = filename.lower().split('.')[-1]
        mime_types = {
            'py': 'text/x-python',
            'js': 'text/javascript',
            'ts': 'text/typescript',
            'java': 'text/x-java-source',
            'cpp': 'text/x-c++src',
            'c': 'text/x-csrc',
            'h': 'text/x-csrc',
            'php': 'text/x-php',
            'rb': 'text/x-ruby',
            'go': 'text/x-go',
            'html': 'text/html',
            'css': 'text/css',
            'json': 'application/json',
            'xml': 'text/xml',
            'sql': 'text/x-sql'
        }
        return mime_types.get(extension, 'text/plain')

# Global Supabase client instance
@st.cache_resource
def get_supabase_client():
    """Get or create Supabase client instance"""
    return SupabaseClient()

# Authentication helpers
def require_auth():
    """Decorator to require authentication"""
    if not get_supabase_client().is_authenticated():
        st.error("⚠️ Você precisa estar autenticado para acessar esta página.")
        st.stop()
        return False
    return True

def get_current_user_display():
    """Get current user display name"""
    try:
        user = get_supabase_client().get_current_user()
        if user:
            # Tenta obter do Pydantic model
            if hasattr(user, 'user_metadata'):
                username = user.user_metadata.get('username') if user.user_metadata else None
            else:
                username = user.get('user_metadata', {}).get('username') if hasattr(user, 'get') else None

            if hasattr(user, 'email'):
                email = user.email
            else:
                email = user.get('email', '') if hasattr(user, 'get') else ''

            return username or (email.split('@')[0] if email else "Usuário")
        return "Usuário"
    except Exception as e:
        # Se der erro, tenta fallback básico
        return "Usuário"