"""
AVALIA Authentication Page
This page handles user authentication (sign in, sign up, password reset)
"""

import streamlit as st
import re
from utils.supabase_client import supabase_client, set_user_in_session, set_user_profile_in_session


def is_valid_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"

    return True, "Password is valid"


def sign_in_form():
    """Display sign in form"""
    st.subheader("Sign In")

    with st.form("sign_in_form"):
        email = st.text_input("Email", key="signin_email", type="default")
        password = st.text_input("Password", key="signin_password", type="password")

        submitted = st.form_submit_button("Sign In")

        if submitted:
            if not email or not password:
                st.error("Please fill in all fields")
                return

            if not is_valid_email(email):
                st.error("Please enter a valid email address")
                return

            with st.spinner("Signing in..."):
                result = supabase_client.sign_in(email, password)

                if result["success"]:
                    user_data = result["user"]
                    set_user_in_session({
                        "id": user_data.id,
                        "email": user_data.email,
                        "user_metadata": user_data.user_metadata
                    })

                    # Get user profile
                    profile = supabase_client.get_profile(user_data.id)
                    set_user_profile_in_session(profile)

                    st.success("Successfully signed in!")
                    st.rerun()
                else:
                    st.error(f"Sign in failed: {result.get('error', 'Unknown error')}")


def sign_up_form():
    """Display sign up form"""
    st.subheader("Sign Up")

    with st.form("sign_up_form"):
        email = st.text_input("Email", key="signup_email", type="default")
        password = st.text_input("Password", key="signup_password", type="password")
        confirm_password = st.text_input("Confirm Password", key="confirm_password", type="password")
        full_name = st.text_input("Full Name (Optional)", key="full_name")

        submitted = st.form_submit_button("Sign Up")

        if submitted:
            if not email or not password or not confirm_password:
                st.error("Please fill in all required fields")
                return

            if not is_valid_email(email):
                st.error("Please enter a valid email address")
                return

            valid_password, password_message = is_valid_password(password)
            if not valid_password:
                st.error(password_message)
                return

            if password != confirm_password:
                st.error("Passwords do not match")
                return

            with st.spinner("Creating account..."):
                user_data = {
                    "full_name": full_name
                }

                result = supabase_client.sign_up(email, password, user_data)

                if result["success"]:
                    st.success("Account created successfully! Please check your email to confirm your account.")
                else:
                    st.error(f"Sign up failed: {result.get('error', 'Unknown error')}")


def password_reset_form():
    """Display password reset form"""
    st.subheader("Reset Password")

    with st.form("password_reset_form"):
        email = st.text_input("Email", key="reset_email", type="default")

        submitted = st.form_submit_button("Send Reset Link")

        if submitted:
            if not email:
                st.error("Please enter your email address")
                return

            if not is_valid_email(email):
                st.error("Please enter a valid email address")
                return

            with st.spinner("Sending reset link..."):
                result = supabase_client.reset_password(email)

                if result["success"]:
                    st.success("Password reset link sent to your email!")
                else:
                    st.error(f"Failed to send reset link: {result.get('error', 'Unknown error')}")


def show_profile_info():
    """Display user profile information"""
    profile = supabase_client.get_profile(st.session_state.user["id"])

    if profile:
        st.success(f"Welcome back, {profile.get('full_name', profile.get('username', 'User'))}!")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Role", profile.get('role', 'Unknown'))

        with col2:
            st.metric("Email Verified", "✅" if profile.get('is_verified', False) else "❌")

        with col3:
            st.metric("Status", "Active" if profile.get('is_active', True) else "Inactive")
    else:
        st.success(f"Welcome back, {st.session_state.user['email']}!")


def main():
    """Main authentication page logic"""
    st.set_page_config(
        page_title="AVALIA - Authentication",
        page_icon="🔐",
        layout="centered"
    )

    # Check if already authenticated
    if supabase_client.get_current_user():
        st.title("🔐 AVALIA Authentication")

        user = supabase_client.get_current_user()
        profile = supabase_client.get_profile(user["id"])

        if profile:
            show_profile_info()

        if st.button("Continue to Dashboard"):
            st.switch_page("Home")

        if st.button("Sign Out"):
            result = supabase_client.sign_out()
            if result["success"]:
                set_user_in_session(None)
                set_user_profile_in_session(None)
                st.rerun()
            else:
                st.error("Failed to sign out")

        return

    st.title("🔐 AVALIA Authentication")
    st.markdown("Welcome to AVALIA - Your Code Quality Analysis Platform")

    # Create tabs for different auth actions
    tab1, tab2, tab3 = st.tabs(["Sign In", "Sign Up", "Reset Password"])

    with tab1:
        sign_in_form()

    with tab2:
        sign_up_form()

    with tab3:
        password_reset_form()

    # Add helpful information
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("""
    - **Sign In**: Use your existing AVALIA account credentials
    - **Sign Up**: Create a new account to start analyzing your code
    - **Reset Password**: Recover your account if you forgot your password

    **Password Requirements:**
    - At least 8 characters long
    - Contains uppercase and lowercase letters
    - Contains at least one number
    """)


if __name__ == "__main__":
    main()