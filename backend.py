import os
import logging
import streamlit as st
import google.auth
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET = 'credentials.json'
# Define the Google Drive folder ID
GOOGLE_DRIVE_FOLDER_ID = 'your-google-drive-folder-id'
PROJECT_ROOT = ''
def get_files_from_drive(folder_id):
    
    try:
        if os.path.exists('token.json'):
            creds = google.auth.load_credentials_from_file('token.json')[0]
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=8502)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        # Initialize the Drive service with credentials
        service = build('drive', 'v3', credentials=creds)
        
        # Query to fetch files in the specified folder
        query = f"'{folder_id}' in parents"
        response = service.files().list(q=query, fields="files(id, name)").execute()
        
        # Return the list of files
        return response.get('files', [])
    
    except Exception as e:
        logging.error(f"Error fetching files from Google Drive: {e}")
        st.error("Failed to fetch files from the specified Google Drive folder.")
        return []