from utils import API_BASE_URL
import streamlit as st
from auth import show_login, show_register
from dashboard import show_dashboard

st.set_page_config(
    page_title="DevTrack Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    text-align: center;
}

.main-header h1 {
    color: white;
    margin: 0;
    font-size: 2.5rem;
}

.auth-container {
    max-width: 400px;
    margin: 2rem auto;
    padding: 2rem;
    background: #f8f9fa;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.success-message {
    background: #d4edda;
    color: #155724;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}

.error-message {
    background: #f8d7da;
    color: #721c24;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

def main():
    """
    Main function that controls the entire Streamlit app flow.
    This is like the traffic controller - it decides what page to show.
    """
    
    # Initialize session state variables
    # Session state keeps data persistent across page reloads
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'page' not in st.session_state:
        st.session_state.page = 'login'

    # App header
    st.markdown("""
    <div class="main-header">
        <h1>DevTrack Dashboard</h1>
        <p style="color: #e0e0e0; margin: 0;">Track your development productivity in real-time</p>
    </div>
    """, unsafe_allow_html=True)

    # Check authentication status
    if not st.session_state.authenticated:
        # Show authentication pages
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Navigation tabs for login/register
            tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
            
            with tab1:
                show_login()
            
            with tab2:
                show_register()
    else:
        # User is authenticated, show the main dashboard
        show_dashboard()

if __name__ == "__main__":
    main()