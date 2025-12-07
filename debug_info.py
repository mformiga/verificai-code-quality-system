"""
Debug utility for AVALIA application
Use this to troubleshoot Supabase connection issues
"""

import os
import streamlit as st
from supabase_client import get_supabase_client

def show_debug_info():
    """Display debug information for troubleshooting"""
    st.subheader("🔍 Debug Information")

    # Show environment info
    st.write("**Environment Variables:**")
    env_vars = {
        "SUPABASE_URL": os.getenv("SUPABASE_URL", "Not found"),
        "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY", "Not found")[:20] + "..." if os.getenv("SUPABASE_ANON_KEY") else "Not found",
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "Not set"),
    }

    for key, value in env_vars.items():
        st.write(f"- {key}: {value}")

    # Show Streamlit secrets
    st.write("**Streamlit Secrets:**")
    try:
        secrets = st.secrets
        if "supabase" in secrets:
            for key, value in secrets["supabase"].items():
                if key == "SUPABASE_ANON_KEY" or key == "SUPABASE_SERVICE_ROLE_KEY":
                    value = str(value)[:20] + "..." if value else "Not found"
                st.write(f"- supabase.{key}: {value}")
        else:
            st.write("No Supabase secrets found")
    except Exception as e:
        st.write(f"Error accessing secrets: {e}")

    # Test Supabase connection
    st.write("**Supabase Connection Test:**")
    try:
        supabase = get_supabase_client()
        if supabase.client:
            st.success("✅ Supabase client initialized successfully")
            st.write(f"- URL: {supabase.url[:20]}...")
            st.write(f"- Authenticated: {supabase.is_authenticated()}")
        else:
            st.error("❌ Supabase client failed to initialize")
    except Exception as e:
        st.error(f"❌ Connection test failed: {e}")

# Usage in app.py:
# if st.checkbox("🔍 Show Debug Info"):
#     from debug_info import show_debug_info
#     show_debug_info()