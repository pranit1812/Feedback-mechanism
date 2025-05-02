# Feedback Dashboard

A Streamlit dashboard application that displays feedback data received from a front-end website.

## Features

- Displays feedback data with filtering options
- Receives data via POST requests
- Visualizes feedback sentiment

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the app locally:
   ```
   streamlit run app.py
   ```

## API Endpoint

The dashboard receives POST requests with the following fields:
- `id` - Unique identifier for the feedback
- `projectName` - Name of the project
- `query` - Question asked
- `answer` - Response provided
- `sentiment` - Must be "up", "down", or "comment"
- `user.id` - User identifier
- `user.email` - User email
- `searchMethod` - Method used for search
- `commentText` - Required if sentiment is "comment"

## Deployment

This app is configured for Vercel deployment with Streamlit. 