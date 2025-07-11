import streamlit as st
import requests
from utils import API_BASE_URL

def show_login():
    """
    Display the login form and handle user authentication.
    This connects to your FastAPI /auth/login endpoint.
    """
    st.markdown("### Login to DevTrack")
    
    # Create the login form
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if not username or not password:
                st.error("❌ Please fill in both username and password")
                return
            
            # Prepare data for API call
            login_data = {
                "username": username,
                "password": password
            }
            
            try:
                # Make API call to your FastAPI backend
                response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data)
                
                if response.status_code == 200:
                    # Login successful
                    data = response.json()
                    
                    # Store authentication data in session state
                    st.session_state.authenticated = True
                    st.session_state.access_token = data["access_token"]
                    st.session_state.username = username
                    
                    st.success("✅ Login successful! Redirecting to dashboard...")
                    st.rerun()  # Refresh the page to show dashboard
                    
                else:
                    # Login failed
                    error_data = response.json()
                    st.error(f"❌ Login failed: {error_data.get('detail', 'Unknown error')}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to server. Make sure your FastAPI backend is running on http://127.0.0.1:8000")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

def show_register():
    """
    Display the registration form and handle user registration.
    This connects to your FastAPI /auth/register endpoint.
    """
    st.markdown("### 📝 Create New Account")
    

    with st.form("register_form"):
        username = st.text_input("Username", placeholder="Choose a username")
        password = st.text_input("Password", type="password", placeholder="Create a password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        submit_button = st.form_submit_button("Register")
        
        if submit_button:
            # Validation
            if not username or not password or not confirm_password:
                st.error("❌ Please fill in all fields")
                return
            
            if password != confirm_password:
                st.error("❌ Passwords do not match")
                return
            
            if len(password) < 6:
                st.error("❌ Password must be at least 6 characters long")
                return
            
            # Prepare data for API call
            register_data = {
                "username": username,
                "password": password
            }
            
            try:
                # Make API call to your FastAPI backend
                response = requests.post(f"{API_BASE_URL}/auth/register", json=register_data)
                
                if response.status_code == 201:
                    # Registration successful
                    st.success("✅ Account created successfully! Please login with your credentials.")
                    
                else:
                    # Registration failed
                    error_data = response.json()
                    st.error(f"❌ Registration failed: {error_data.get('detail', 'Unknown error')}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to server. Make sure your FastAPI backend is running on http://127.0.0.1:8000")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

def logout():
    """
    Handle user logout by clearing session state.
    """
    st.session_state.authenticated = False
    st.session_state.access_token = None
    st.session_state.username = None
    st.rerun()