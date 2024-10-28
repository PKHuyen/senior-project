############## Download videos ##################
import os
import dropbox

def get_access_token():
    # Read the access token from the properties file
    properties_file = os.path.expanduser("dropbox.properties")
    with open(properties_file) as f:
        for line in f:
            if line.startswith("ACCESS_TOKEN="):
                return line.split("=")[1].strip()
    raise ValueError("ACCESS_TOKEN not found in properties file.")

# Initialize Dropbox client with the token
access_token = get_access_token()
dbx = dropbox.Dropbox(access_token)

def download_file(dropbox_path, local_path):
    try:
        dbx.files_download_to_file(local_path, dropbox_path)
        print(f"Downloaded {dropbox_path} to {local_path}")
    except dropbox.exceptions.ApiError as e:
        print(f"API error: {e}")

def download_all_files_in_folder(dropbox_folder_path, local_folder_path):
    os.makedirs(local_folder_path, exist_ok=True)
    
    result = dbx.files_list_folder(dropbox_folder_path)
    for entry in result.entries:
        if isinstance(entry, dropbox.files.FileMetadata):
            local_file_path = os.path.join(local_folder_path, entry.name)
            download_file(entry.path_lower, local_file_path)

dropbox_folder_path = "/video"
local_folder_path = "../senior-project/video"
# download_all_files_in_folder(dropbox_folder_path, local_folder_path)

############# Run Notebook ###############
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
def run_notebook(notebook_path, output_dir=None):
    print (f"Run {notebook_path}")
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
from keyframe_extraction.extract_keyframes import extraction
# extraction("../senior-project/video", "../senior-project/keyframe_information/keyframe/")

############# Annotation ###############
from keyframe_extraction.get_metadata_json import process_keyframe_folders
# process_keyframe_folders("../senior-project/keyframe_information/keyframe/", "../senior-project/keyframe_information/annotation/")

############# CLIP ###############
# run_notebook("../senior-project/database_processing/clip.ipynb")

############# CLIPv2 ###############
# run_notebook("../senior-project/database_processing/clipv2.ipynb")

############# create_bin ###############
run_notebook("../senior-project/database_processing/create_bin.ipynb")

############# faiss_processing ###############
from database_processing.faiss_processing import MyFaiss
MyFaiss