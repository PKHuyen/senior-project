import os
import dropbox

def get_access_token():
    properties_file = os.path.expanduser("../dropbox.properties")
    with open(properties_file) as f:
        for line in f:
            if line.startswith("ACCESS_TOKEN="):
                return line.split("=")[1].strip()
    raise ValueError("ACCESS_TOKEN not found in properties file.")

# Initialize Dropbox client with the token
access_token = get_access_token()
dbx = dropbox.Dropbox(access_token)

def clean_dropbox_path(path):
    """
    Clean and normalize a Dropbox path:
    - Replace backslashes with forward slashes
    - Remove './' or '.\' patterns
    - Ensure the path starts with a forward slash
    - Remove any double slashes
    """
    # Replace backslashes with forward slashes
    path = path.replace("\\", "/")
    
    # Remove './' or '.\' patterns
    path = path.replace("./", "").replace(".\\", "")
    
    # Ensure path starts with forward slash
    if not path.startswith("/"):
        path = "/" + path
        
    # Remove any double slashes
    while "//" in path:
        path = path.replace("//", "/")
        
    return path

def upload_large_file(local_file_path, dropbox_file_path):
    dropbox_file_path = clean_dropbox_path(dropbox_file_path)
    file_size = os.path.getsize(local_file_path)
    CHUNK_SIZE = 4 * 1024 * 1024  # 4MB chunks
    
    with open(local_file_path, "rb") as f:
        if file_size <= 150 * 1024 * 1024:  # 150 MB
            print(f"Uploading {local_file_path} to {dropbox_file_path}")
            dbx.files_upload(f.read(), dropbox_file_path, mode=dropbox.files.WriteMode("overwrite"))
            print(f"Uploaded {local_file_path} to {dropbox_file_path}")
        else:
            print(f"Starting chunked upload for {local_file_path} ({file_size / (1024*1024):.2f} MB)")
            
            try:
                # Upload first chunk and start session
                chunk = f.read(CHUNK_SIZE)
                session_start_result = dbx.files_upload_session_start(chunk)
                cursor = dropbox.files.UploadSessionCursor(
                    session_id=session_start_result.session_id,
                    offset=f.tell()
                )
                
                # Upload intermediate chunks
                while f.tell() < file_size:
                    if (file_size - f.tell()) <= CHUNK_SIZE:
                        # Last chunk
                        print(f"Uploading final chunk...")
                        commit = dropbox.files.CommitInfo(
                            path=dropbox_file_path,
                            mode=dropbox.files.WriteMode("overwrite")
                        )
                        dbx.files_upload_session_finish(
                            f.read(CHUNK_SIZE),
                            cursor,
                            commit
                        )
                        print(f"Successfully uploaded {local_file_path} to {dropbox_file_path}")
                        break
                    else:
                        # Intermediate chunks
                        chunk = f.read(CHUNK_SIZE)
                        dbx.files_upload_session_append_v2(chunk, cursor)
                        cursor.offset = f.tell()
                        print(f"Uploaded chunk: {cursor.offset / (1024*1024):.2f} MB / {file_size / (1024*1024):.2f} MB")
                        
            except Exception as e:
                print(f"Error during chunked upload: {str(e)}")
                raise

def upload_folder(local_folder, dropbox_folder):
    """
    Recursively upload a local folder to Dropbox, ignoring .DS_Store files.
    """
    # Clean the base dropbox folder path
    dropbox_folder = clean_dropbox_path(dropbox_folder)
    
    for root, dirs, files in os.walk(local_folder):
        # Get the relative path in Dropbox
        relative_path = os.path.relpath(root, local_folder)
        
        # Handle the case where relative_path is '.'
        if relative_path == '.':
            current_dropbox_path = dropbox_folder
        else:
            current_dropbox_path = clean_dropbox_path(os.path.join(dropbox_folder, relative_path))

        # Create folders in Dropbox as needed
        for directory in dirs:
            dir_path = clean_dropbox_path(f"{current_dropbox_path}/{directory}")
            try:
                dbx.files_create_folder_v2(dir_path)
                print(f"Folder created: {dir_path}")
            except dropbox.exceptions.ApiError as e:
                if e.error.is_path() and e.error.get_path().is_conflict():
                    print(f"Folder already exists: {dir_path}")

        # Upload each file, ignoring .DS_Store files
        for file in files:
            if file == ".DS_Store":
                continue
            
            local_file_path = os.path.join(root, file)
            dropbox_file_path = clean_dropbox_path(f"{current_dropbox_path}/{file}")
            
            try:
                upload_large_file(local_file_path, dropbox_file_path)
            except dropbox.exceptions.ApiError as e:
                print(f"Failed to upload {local_file_path}: {e}")

# Set the paths for the upload
video_folder_path = "../video/"  # Local folder to upload
dropbox_video_folder_path = "/video"  # Dropbox folder path

# Start the upload process
upload_folder(video_folder_path, dropbox_video_folder_path)