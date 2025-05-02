import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime
import os

# Set page config
st.set_page_config(
    page_title="Feedback Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize session state for storing feedback data
if 'feedback_data' not in st.session_state:
    st.session_state.feedback_data = []

# Function to save data to a JSON file
def save_data_to_file():
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    with open(f"{data_dir}/feedback_data.json", "w") as f:
        json.dump(st.session_state.feedback_data, f)

# Function to load data from a JSON file
def load_data_from_file():
    data_dir = "data"
    file_path = f"{data_dir}/feedback_data.json"
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                st.session_state.feedback_data = json.load(f)
        except json.JSONDecodeError:
            st.error("Error loading data file. It might be corrupted.")

# Load data on app start
load_data_from_file()

# Streamlit UI
st.title("Feedback Dashboard")

# Sidebar for filtering
st.sidebar.header("Filters")

# Convert to DataFrame for easier manipulation
if st.session_state.feedback_data:
    df = pd.DataFrame(st.session_state.feedback_data)
    
    # Add timestamp if not present
    if 'timestamp' not in df.columns:
        df['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Filter options
    project_names = ["All"] + sorted(df['projectName'].unique().tolist())
    selected_project = st.sidebar.selectbox("Project", project_names)
    
    sentiment_options = ["All", "up", "down", "comment"]
    selected_sentiment = st.sidebar.selectbox("Sentiment", sentiment_options)
    
    search_methods = ["All"] + sorted(df['searchMethod'].unique().tolist())
    selected_search_method = st.sidebar.selectbox("Search Method", search_methods)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_project != "All":
        filtered_df = filtered_df[filtered_df['projectName'] == selected_project]
    
    if selected_sentiment != "All":
        filtered_df = filtered_df[filtered_df['sentiment'] == selected_sentiment]
    
    if selected_search_method != "All":
        filtered_df = filtered_df[filtered_df['searchMethod'] == selected_search_method]
    
    # Display summary metrics
    st.header("Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Feedback", len(df))
    
    with col2:
        sentiment_counts = df['sentiment'].value_counts()
        positive_count = sentiment_counts.get('up', 0)
        negative_count = sentiment_counts.get('down', 0)
        total = positive_count + negative_count
        satisfaction_rate = (positive_count / total * 100) if total > 0 else 0
        st.metric("Satisfaction Rate", f"{satisfaction_rate:.1f}%")
    
    with col3:
        st.metric("Comments", df[df['sentiment'] == 'comment'].shape[0])
    
    # Display sentiment distribution
    st.header("Sentiment Distribution")
    sentiment_counts = filtered_df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    
    fig = px.pie(
        sentiment_counts, 
        values='Count', 
        names='Sentiment',
        color='Sentiment',
        color_discrete_map={'up': 'green', 'down': 'red', 'comment': 'blue'},
        hole=0.4
    )
    st.plotly_chart(fig)
    
    # Display detailed feedback
    st.header("Detailed Feedback")
    
    # Sort by most recent first
    if 'timestamp' in filtered_df.columns:
        filtered_df = filtered_df.sort_values(by='timestamp', ascending=False)
    
    # Display comments section
    if 'comment' in filtered_df['sentiment'].values:
        st.subheader("Comments")
        comments_df = filtered_df[filtered_df['sentiment'] == 'comment']
        for i, row in comments_df.iterrows():
            with st.expander(f"Comment from {row.get('user.email', 'Anonymous')} on {row.get('projectName', 'Unknown Project')}"):
                st.write(f"**Query:** {row.get('query', 'N/A')}")
                st.write(f"**Comment:** {row.get('commentText', 'No comment text')}")
    
    # Display all feedback data
    st.subheader("All Feedback")
    display_cols = ['id', 'projectName', 'query', 'sentiment', 'searchMethod', 'timestamp']
    if not filtered_df.empty:
        st.dataframe(filtered_df[display_cols])
else:
    st.info("No feedback data available yet. Send POST requests to populate the dashboard.")

# API endpoint for receiving POST requests
# For Streamlit, we need to handle this differently since it's not a traditional web server
# We'll create a section to manually add test data or simulate POST requests

st.header("API Integration")
st.write("This dashboard is designed to receive data via POST requests. In a production environment, use the Streamlit API to handle incoming requests.")

# For testing/simulation purposes
with st.expander("Test Data Entry"):
    st.subheader("Add Test Feedback Data")
    
    with st.form("feedback_form"):
        test_id = st.text_input("ID", value=f"test-{len(st.session_state.feedback_data) + 1}")
        test_project = st.text_input("Project Name", value="Test Project")
        test_query = st.text_area("Query Asked")
        test_answer = st.text_area("Answer")
        test_sentiment = st.selectbox("Sentiment", ["up", "down", "comment"])
        test_user_id = st.text_input("User ID", value="test-user-1")
        test_user_email = st.text_input("User Email", value="test@example.com")
        test_search_method = st.text_input("Search Method", value="direct")
        
        test_comment_text = st.text_area("Comment Text (required if sentiment is 'comment')")
        
        submit_button = st.form_submit_button("Add Test Data")
        
        if submit_button:
            # Validate required fields
            if test_sentiment == "comment" and not test_comment_text:
                st.error("Comment text is required when sentiment is 'comment'")
            else:
                # Create test data entry
                test_data = {
                    "id": test_id,
                    "projectName": test_project,
                    "query": test_query,
                    "answer": test_answer,
                    "sentiment": test_sentiment,
                    "user.id": test_user_id,
                    "user.email": test_user_email,
                    "searchMethod": test_search_method,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                if test_sentiment == "comment":
                    test_data["commentText"] = test_comment_text
                
                # Add to session state
                st.session_state.feedback_data.append(test_data)
                save_data_to_file()
                st.success("Test data added successfully!")
                st.experimental_rerun()

# Clear data button (for testing)
if st.sidebar.button("Clear All Data"):
    st.session_state.feedback_data = []
    save_data_to_file()
    st.experimental_rerun() 