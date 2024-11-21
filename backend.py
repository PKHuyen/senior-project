############# Run Notebook ###############
import os
<<<<<<< Updated upstream
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
def run_notebook(notebook_path, output_dir=None):
    print (f"Run {notebook_path}")
=======
import logging
import streamlit as st
import google.auth
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET = 'credentials.json'
# Define the Google Drive folder ID
GOOGLE_DRIVE_FOLDER_ID = '1l5D8idS8nXKD_E5A0SlM5ok2bE1iMrF1'
def get_files_from_drive(folder_id):
    
>>>>>>> Stashed changes
    try:
        notebook_dir = os.path.dirname(os.path.abspath(notebook_path))
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
        exec_processor = ExecutePreprocessor(
            timeout=600,  # 10 minute timeout
            kernel_name='python3'
        )
        
        exec_processor.preprocess(notebook, {'metadata': {'path': notebook_dir}})
        print (f"Finish {notebook_path}")  
        return True

    except Exception as e:
        return False

############# Keyframe Extraction ###############
run_notebook("keyframe_extraction/extract_keyframes.ipynb")

############# Annotation ###############
run_notebook("keyframe_extraction/get_metadata_json.ipynb")

############# CLIP ###############
run_notebook("database_processing/clip.ipynb")

############# CLIPv2 ###############
run_notebook("database_processing/clipv2.ipynb")

############# create_bin ###############
run_notebook("database_processing/create_bin.ipynb")