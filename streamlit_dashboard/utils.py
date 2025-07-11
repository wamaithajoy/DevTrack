import streamlit as st
import requests
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"

def get_auth_headers():
    """
    Get authorization headers with JWT token.
    This is needed for all authenticated API calls.
    """
    if st.session_state.get('access_token'):
        return {
            "Authorization": f"Bearer {st.session_state.access_token}",
            "Content-Type": "application/json"
        }
    return {"Content-Type": "application/json"}

def make_authenticated_request(method, url, json=None, params=None):
    """
    Make authenticated API requests to your FastAPI backend.
    This function handles all API calls with proper error handling.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        url: Full URL for the API endpoint
        json: JSON data for POST/PUT requests
        params: Query parameters for GET requests
    
    Returns:
        Response object or None if error
    """
    try:
        headers = get_auth_headers()
        
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=json)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=json)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            st.error(f"❌ Unsupported HTTP method: {method}")
            return None
        
        # Check if token is expired
        if response.status_code == 401:
            st.error("❌ Session expired. Please login again.")
            # Clear session state
            st.session_state.authenticated = False
            st.session_state.access_token = None
            st.rerun()
            return None
        
        return response
        
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server. Make sure your FastAPI backend is running on http://127.0.0.1:8000")
        return None
    except requests.exceptions.Timeout:
        st.error("❌ Request timeout. Please try again.")
        return None
    except Exception as e:
        st.error(f"❌ Request failed: {str(e)}")
        return None

def create_activity_chart(data, title="Activity Over Time"):
    """
    Create a line chart showing activity over time.
    
    Args:
        data: List of tracking data
        title: Chart title
    
    Returns:
        Plotly figure object
    """
    if not data:
        return None
    
    df = pd.DataFrame(data)
    
    # Convert timestamp to datetime
    df['last_updated'] = pd.to_datetime(df['last_updated'])
    
    # Create line chart
    fig = px.line(
        df, 
        x='last_updated', 
        y='commits',
        color='project_name',
        title=title,
        labels={'last_updated': 'Date', 'commits': 'Commits'}
    )
    
    fig.update_layout(
        height=400,
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def create_error_chart(data, title="Error Distribution"):
    """
    Create a pie chart showing error distribution by project.
    
    Args:
        data: List of tracking data
        title: Chart title
    
    Returns:
        Plotly figure object
    """
    if not data:
        return None
    
    df = pd.DataFrame(data)
    
    # Group by project and sum errors
    error_data = df.groupby('project_name')['errors'].sum().reset_index()
    
    # Only show projects with errors
    error_data = error_data[error_data['errors'] > 0]
    
    if error_data.empty:
        return None
    
    # Create pie chart
    fig = px.pie(
        error_data, 
        values='errors', 
        names='project_name',
        title=title,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_layout(height=400)
    
    return fig

def create_response_time_chart(data, title="Response Time Analysis"):
    """
    Create a bar chart showing average response time by project.
    
    Args:
        data: List of tracking data
        title: Chart title
    
    Returns:
        Plotly figure object
    """
    if not data:
        return None
    
    df = pd.DataFrame(data)
    
    # Group by project and calculate average response time
    response_data = df.groupby('project_name')['response_time'].mean().reset_index()
    
    # Create bar chart
    fig = px.bar(
        response_data, 
        x='project_name', 
        y='response_time',
        title=title,
        labels={'project_name': 'Project', 'response_time': 'Avg Response Time (ms)'},
        color='response_time',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(height=400)
    
    return fig

def format_datetime(datetime_str):
    """
    Format datetime string for display.
    
    Args:
        datetime_str: ISO datetime string
    
    Returns:
        Formatted datetime string
    """
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return datetime_str

def calculate_total_activity(data):
    """
    Calculate total activity metrics from tracking data.
    
    Args:
        data: List of tracking data
    
    Returns:
        Dictionary with total metrics
    """
    if not data:
        return {
            'total_commits': 0,
            'total_api_requests': 0,
            'total_errors': 0,
            'avg_response_time': 0,
            'total_projects': 0
        }
    
    df = pd.DataFrame(data)
    
    return {
        'total_commits': df['commits'].sum(),
        'total_api_requests': df['api_requests'].sum(),
        'total_errors': df['errors'].sum(),
        'avg_response_time': df['response_time'].mean(),
        'total_projects': df['project_name'].nunique()
    }

def get_project_summary(data):
    """
    Get summary statistics for each project.
    
    Args:
        data: List of tracking data
    
    Returns:
        DataFrame with project summaries
    """
    if not data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    
    # Group by project and calculate totals
    summary = df.groupby('project_name').agg({
        'commits': 'sum',
        'api_requests': 'sum',
        'errors': 'sum',
        'response_time': 'mean',
        'last_updated': 'max'
    }).reset_index()
    
    # Round response time
    summary['response_time'] = summary['response_time'].round(2)
    
    return summary

def validate_tracking_data(data):
    """
    Validate tracking data before sending to API.
    
    Args:
        data: Dictionary with tracking data
    
    Returns:
        Tuple (is_valid, error_message)
    """
    if not data.get('project_name'):
        return False, "Project name is required"
    
    if not isinstance(data.get('commits', 0), int) or data.get('commits', 0) < 0:
        return False, "Commits must be a non-negative integer"
    
    if not isinstance(data.get('api_requests', 0), int) or data.get('api_requests', 0) < 0:
        return False, "API requests must be a non-negative integer"
    
    if not isinstance(data.get('errors', 0), int) or data.get('errors', 0) < 0:
        return False, "Errors must be a non-negative integer"
    
    if not isinstance(data.get('response_time', 0), (int, float)) or data.get('response_time', 0) < 0:
        return False, "Response time must be a non-negative number"
    
    return True, None

def show_success_message(message):
    """
    Display a success message with styling.
    
    Args:
        message: Success message to display
    """
    st.success(f"✅ {message}")

def show_error_message(message):
    """
    Display an error message with styling.
    
    Args:
        message: Error message to display
    """
    st.error(f"❌ {message}")

def show_info_message(message):
    """
    Display an info message with styling.
    
    Args:
        message: Info message to display
    """
    st.info(f"ℹ️ {message}")

def check_api_health():
    """
    Check if the FastAPI backend is running and healthy.
    
    Returns:
        Boolean indicating if API is healthy
    """
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_api_status():
    """
    Get API status for display in the dashboard.
    
    Returns:
        Dictionary with API status information
    """
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=5)
        if response.status_code == 200:
            return {
                'status': 'healthy',
                'message': 'API is running normally',
                'icon': '✅'
            }
        else:
            return {
                'status': 'warning',
                'message': f'API returned status code {response.status_code}',
                'icon': '⚠️'
            }
    except requests.exceptions.ConnectionError:
        return {
            'status': 'error',
            'message': 'Cannot connect to API. Make sure FastAPI is running.',
            'icon': '❌'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'API check failed: {str(e)}',
            'icon': '❌'
        }

def create_metric_card(title, value, delta=None, delta_color="normal"):
    """
    Create a styled metric card for the dashboard.
    
    Args:
        title: Metric title
        value: Metric value
        delta: Optional delta value
        delta_color: Color for delta (normal, inverse, off)
    """
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color
    )
    
def get_github_username(token):
    headers = {"Authorization": f"token {token}"}
    r = requests.get("https://api.github.com/user", headers=headers)
    if r.status_code == 200:
        return r.json()["login"]
    return None

def get_commit_count(token, username, since_days=1):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.cloak-preview"  # Needed for commit search API
    }
    since_date = (datetime.utcnow() - timedelta(days=since_days)).isoformat() + "Z"
    url = f"https://api.github.com/search/commits?q=author:{username}+committer-date:>{since_date}"

    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json().get("total_count", 0)
    return 0
    