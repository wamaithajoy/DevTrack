import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import urllib.parse
from utils import API_BASE_URL, make_authenticated_request, create_activity_chart, create_error_chart, format_datetime, get_auth_headers, get_github_username, get_commit_count, get_user_tracking_data
from utils import sync_project_commits

def show_dashboard():
    """
    Main dashboard interface that displays all user tracking data.
    This connects to your FastAPI endpoints to show real-time data.
    """
    
    # Dashboard header with user info
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"## Welcome back, {st.session_state.username}! 👋")
        st.markdown("Track your development productivity in real-time")
    
    with col2:
        # Streak counter (we'll calculate this from data)
        streak_count = get_user_streak()
        st.metric("🔥 Current Streak", f"{streak_count} day")

    sync_project_commits()

    
    with col3:
        # Logout button
        if st.button("🚪 Logout"):
            from auth import logout
            logout()
    
    st.divider()
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "➕ Add Data", "📈 Analytics", "🎯 Projects"])
    
    with tab1:
        show_overview_tab()
    
    with tab2:
        show_add_data_tab()
    
    with tab3:
        show_analytics_tab()
    
    with tab4:
        show_projects_tab()


def show_overview_tab():
    """
    Display the main overview with key metrics and recent activity.
    """
    st.markdown("### 📊 Activity Overview")
    
    # Fetch user's tracking data
    tracking_data = get_user_tracking_data()
    
    if not tracking_data:
        st.info("🎯 No tracking data yet. Add your first entry in the 'Add Data' tab!")
        return
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(tracking_data)
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_commits = df['commits'].sum()
        st.metric("🔄 Total Commits", total_commits)
    
    with col2:
        total_api_requests = df['api_requests'].sum()
        st.metric("🌐 API Requests", total_api_requests)
    
    with col3:
        total_errors = df['errors'].sum()
        st.metric("❌ Total Errors", total_errors)
    
    with col4:
        avg_response_time = df['response_time'].mean()
        st.metric("⚡ Avg Response Time", f"{avg_response_time:.2f}ms")
    
    st.divider()
    
    # Recent activity table
    st.markdown("### 📋 Recent Activity")
    
    # Format the data for display
    display_df = df.copy()
    display_df['last_updated'] = pd.to_datetime(display_df['last_updated']).dt.strftime('%Y-%m-%d %H:%M')
    
    # Select columns to display
    columns_to_show = ['project_name', 'commits', 'api_requests', 'errors', 'response_time', 'last_updated']
    display_df = display_df[columns_to_show]
    
    # Rename columns for better display
    display_df.columns = ['Project', 'Commits', 'API Requests', 'Errors', 'Response Time (ms)', 'Last Updated']
    
    st.dataframe(display_df, use_container_width=True)

def show_add_data_tab():
    """
    Form to add new tracking data, either manually or via GitHub integration.
    """
    st.markdown("### ➕ Add New Tracking Data")

    # Get existing projects for dropdown
    existing_projects = get_user_projects()

    # New radio selector for input type
    input_type = st.radio("Choose input method", ["Manual Input", "Connect GitHub"])

    if input_type == "Manual Input":
        with st.form("add_tracking_data_manual"):
            col1, col2 = st.columns(2)

            with col1:
                project_option = st.radio("Project Option:", ["Select Existing", "Create New"])

                if project_option == "Select Existing" and existing_projects:
                    project_name = st.selectbox("Select Project:", existing_projects)
                else:
                    project_name = st.text_input("Project Name:", placeholder="Enter project name")

                commits = st.number_input("Commits:", min_value=0, value=0)
                api_requests = st.number_input("API Requests:", min_value=0, value=0)

            with col2:
                errors = st.number_input("Errors:", min_value=0, value=0)
                response_time = st.number_input("Response Time (ms):", min_value=0.0, value=0.0, step=0.1)

            submitted = st.form_submit_button("📝 Add Tracking Data", use_container_width=True)

            if submitted:
                if not project_name:
                    st.error("❌ Please enter a project name")
                    return

                tracking_data = {
                    "project_name": project_name,
                    "commits": commits,
                    "api_requests": api_requests,
                    "errors": errors,
                    "response_time": response_time
                }

                success = add_tracking_data(tracking_data)

                if success:
                    st.success("✅ Tracking data added successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Failed to add tracking data. Please try again.")

    elif input_type == "Connect GitHub":
        st.markdown("### 🔗 Connect GitHub and Auto-Fetch Commits")

        github_token = st.text_input("🔑 GitHub Personal Access Token", type="password")
        st.session_state.github_token = github_token


        # 💡 Add GitHub token instruction here
        st.markdown(
            """
            💡 **To create a token:**  
            1. Go to [GitHub Tokens](https://github.com/settings/tokens)  
            2. Click "Generate new token" (classic or fine-grained)  
            3. Select `repo` and `user` scopes (read-only access is enough)  
            4. Paste the token above 👆  
            """
        )

        if github_token:
            username = get_github_username(github_token)
            st.session_state["github_token"] = github_token
            st.session_state["github_username"] = username

            if username:
                st.success(f"✅ Connected to GitHub as `{username}`")

                commits_today = get_commit_count(github_token, username)

                st.info(f"📦 You made **{commits_today} commit(s)** in the past 24 hours.")


                project_name = st.text_input("Project Name for GitHub Activity", value="GitHub Project")

                if st.button("📥 Save GitHub Activity"):
                    github_data = {
                        "project_name": project_name,
                        "commits": commits_today,
                        "api_requests": 0,
                        "errors": 0,
                        "response_time": 0.0
                    }

                    success = add_tracking_data(github_data)

                    if success:
                        st.success("✅ GitHub activity saved!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Failed to save GitHub data.")
            else:
                st.error("❌ Invalid token or failed to fetch GitHub user.")


def show_analytics_tab():
    """
    Display charts and analytics for tracking data.
    """
    st.markdown("### 📈 Analytics & Insights")
    
    # Fetch user's tracking data
    tracking_data = get_user_tracking_data()
    
    if not tracking_data:
        st.info("📊 No data available for analytics. Add some tracking data first!")
        return
    
    df = pd.DataFrame(tracking_data)
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Commits by project
        commits_by_project = df.groupby('project_name')['commits'].sum().reset_index()
        fig_commits = px.bar(
            commits_by_project, 
            x='project_name', 
            y='commits',
            title='Commits by Project',
            color='commits',
            color_continuous_scale='Blues'
        )
        fig_commits.update_layout(height=400)
        st.plotly_chart(fig_commits, use_container_width=True)
    
    with col2:
        # API requests by project
        api_by_project = df.groupby('project_name')['api_requests'].sum().reset_index()
        fig_api = px.pie(
            api_by_project, 
            values='api_requests', 
            names='project_name',
            title='API Requests Distribution'
        )
        fig_api.update_layout(height=400)
        st.plotly_chart(fig_api, use_container_width=True)
    
    # Error analysis
    if df['errors'].sum() > 0:
        st.markdown("#### ❌ Error Analysis")
        errors_by_project = df.groupby('project_name')['errors'].sum().reset_index()
        fig_errors = px.bar(
            errors_by_project, 
            x='project_name', 
            y='errors',
            title='Errors by Project',
            color='errors',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_errors, use_container_width=True)
    
    # Response time analysis
    st.markdown("#### ⚡ Response Time Analysis")
    response_time_by_project = df.groupby('project_name')['response_time'].mean().reset_index()
    fig_response = px.line(
        response_time_by_project, 
        x='project_name', 
        y='response_time',
        title='Average Response Time by Project',
        markers=True
    )
    st.plotly_chart(fig_response, use_container_width=True)

def show_projects_tab():
    """
    Display and manage projects.
    """
    st.markdown("### 🎯 Project Management")
    
    # Fetch user's tracking data
    tracking_data = get_user_tracking_data()
    
    if not tracking_data:
        st.info("🎯 No projects yet. Add tracking data to create your first project!")
        return
    
    df = pd.DataFrame(tracking_data)
    
    # Group by project and calculate totals
    project_summary = df.groupby('project_name').agg({
        'commits': 'sum',
        'api_requests': 'sum',
        'errors': 'sum',
        'response_time': 'mean',
        'last_updated': 'max'
    }).reset_index()
    
    # Format for display
    project_summary['response_time'] = project_summary['response_time'].round(2)
    project_summary['last_updated'] = pd.to_datetime(project_summary['last_updated']).dt.strftime('%Y-%m-%d %H:%M')
    
    # Rename columns
    project_summary.columns = ['Project', 'Total Commits', 'Total API Requests', 'Total Errors', 'Avg Response Time (ms)', 'Last Updated']
    
    st.dataframe(project_summary, use_container_width=True)
    
    # Update existing project data
    st.markdown("#### 🔄 Update Project Data")
    
    with st.form("update_tracking_data"):
        col1, col2 = st.columns(2)
        
        with col1:
            project_to_update = st.selectbox("Select Project to Update:", df['project_name'].unique())
            new_commits = st.number_input("New Commits:", min_value=0, value=0)
            new_api_requests = st.number_input("New API Requests:", min_value=0, value=0)
        
        with col2:
            new_errors = st.number_input("New Errors:", min_value=0, value=0)
            new_response_time = st.number_input("New Response Time (ms):", min_value=0.0, value=0.0, step=0.1)
        
        update_submitted = st.form_submit_button("🔄 Update Project Data", use_container_width=True)
        
        if update_submitted:
            # Prepare data for API call
            update_data = {
                "project_name": project_to_update,
                "commits": new_commits,
                "api_requests": new_api_requests,
                "errors": new_errors,
                "response_time": new_response_time
            }
            
            # Make API call to update tracking data
            success = update_tracking_data(update_data)
            
            if success:
                st.success("✅ Project data updated successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to update project data. Please try again.")
    
    # Delete existing project
    st.markdown("#### 🗑️ Delete Project")

    with st.form("delete_project_form"):
        project_to_delete = st.selectbox("Select Project to Delete:", df['project_name'].unique())
        confirm = st.checkbox("Yes, I'm sure I want to delete this project. This cannot be undone.")

        delete_submitted = st.form_submit_button("🗑️ Delete Project", use_container_width=True)

        if delete_submitted:
            if not confirm:
                st.warning("⚠️ Please confirm deletion by checking the box.")
            else:
                success = delete_project(project_to_delete)
                if success:
                    st.success(f"✅ Project '{project_to_delete}' deleted successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to delete project. Please try again.")

def delete_project(project_name):
    try:
        # Encode the project name for safe URL usage
        encoded_name = urllib.parse.quote(project_name, safe='')
        response = make_authenticated_request("DELETE", f"{API_BASE_URL}/tracking/{encoded_name}")
        
        if response and response.status_code == 200:
            return True
        else:
            print("Delete failed:", response.status_code, response.text)
            return False
    except Exception as e:
        print("Delete error:", str(e))
        return False

def add_tracking_data(tracking_data):
    """
    Add new tracking data via API.
    """
    try:
        response = make_authenticated_request("POST", f"{API_BASE_URL}/tracking/", json=tracking_data)
        return response and response.status_code == 200
    except Exception as e:
        st.error(f"❌ Error adding tracking data: {str(e)}")
        return False

def update_tracking_data(tracking_data):
    """
    Update existing tracking data via API.
    """
    try:
        response = make_authenticated_request("PUT", f"{API_BASE_URL}/tracking/", json=tracking_data)
        return response and response.status_code == 200
    except Exception as e:
        st.error(f"❌ Error updating tracking data: {str(e)}")
        return False

def get_user_projects():
    """
    Get list of user's existing projects.
    """
    tracking_data = get_user_tracking_data()
    if tracking_data:
        df = pd.DataFrame(tracking_data)
        return df['project_name'].unique().tolist()
    return []

def get_user_streak():
    """
    Calculate the user's current streak based on actual commit activity.

    Returns:
        Integer streak count (consecutive days with at least one commit)
    """
    tracking_data = get_user_tracking_data()
    if not tracking_data:
        return 0

    df = pd.DataFrame(tracking_data)

    df['last_updated'] = pd.to_datetime(df['last_updated']).dt.date

    commits_by_date = df.groupby('last_updated')['commits'].sum()

    today = datetime.utcnow().date()
    days = [today - timedelta(days=i) for i in range(0, 30)]

    streak = 0
    for day in days:
        if commits_by_date.get(day, 0) > 0:
            streak += 1
        else:
            break

    return streak


