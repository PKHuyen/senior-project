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