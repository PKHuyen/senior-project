import streamlit as st
from PIL import Image
import io
import os,sys
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import logging
from typing import List, Tuple
from database_processing.faiss_processing import MyFaiss
import tempfile, json
import traceback
from google.oauth2.credentials import Credentials
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

# Add the project root to Python path for imports
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

# Import the MyFaiss class and Translation from your backend
from database_processing.faiss_processing import MyFaiss

SCOPES = 'https://www.googleapis.com/auth/drive'
keyframes_dir_id = '1bqJG0CRIIuVIib3pBcA2k8iiRyWlwmq9'

class GoogleDriveKeyframeManager:
    def __init__(self, dictionary_id='1l5D8idS8nXKD_E5A0SlM5ok2bE1iMrF1'):
        self.dictionary_id = dictionary_id
        if "drive_service" not in st.session_state:
            st.session_state["drive_service"] = self.authenticate_google_drive()
        self.service = st.session_state["drive_service"]

    # def authenticate_google_drive(self):
    #     """Authenticate and create Google Drive service using Streamlit secrets"""
    #     try:
    #         # Check if we have stored credentials in session state
    #         if 'google_oauth_credentials' in st.session_state:
    #             credentials = Credentials.from_authorized_user_info(
    #                 st.session_state['google_oauth_credentials'],
    #                 SCOPES
    #             )
    #             return build('drive', 'v3', credentials=credentials)

    #         # Create a temporary credentials file from secrets
    #         with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
    #             credentials_dict = {
    #                 "web": {
    #                     "client_id": st.secrets["google_credentials"]["client_id"],
    #                     "project_id": st.secrets["google_credentials"]["project_id"],
    #                     "auth_uri": st.secrets["google_credentials"]["auth_uri"],
    #                     "token_uri": st.secrets["google_credentials"]["token_uri"],
    #                     "auth_provider_x509_cert_url": st.secrets["google_credentials"]["auth_provider_x509_cert_url"],
    #                     "client_secret": st.secrets["google_credentials"]["client_secret"],
    #                     "redirect_uris": st.secrets["google_credentials"]["redirect_uris"]
    #                 }
    #             }
    #             json.dump(credentials_dict, f)
    #             temp_credentials_path = f.name

    #         # Set up OAuth flow
    #         flow = InstalledAppFlow.from_client_secrets_file(
    #             temp_credentials_path,
    #             SCOPES,
    #             redirect_uri=st.secrets["google_credentials"]["redirect_uris"][0]
    #         )

    #         # Create authorization URL
    #         auth_url, _ = flow.authorization_url(prompt='consent')

    #         # Show the authorization URL to the user
    #         st.markdown("""
    #         ### Google Drive Authentication Required
    #         1. Click the link below to authorize this application
    #         2. After authorization, copy the entire URL from your browser
    #         3. Paste it back here and click 'Submit'
    #         """)
    #         st.markdown(f"[Click here to authorize]({auth_url})", unsafe_allow_html=True)
            
    #         auth_code = st.text_input('Paste the full URL here:')
            
    #         if st.button('Submit'):
    #             try:
    #                 # Extract the authorization code from the full URL
    #                 flow.fetch_token(authorization_response=auth_code)
    #                 credentials = flow.credentials
                    
    #                 # Store credentials in session state
    #                 st.session_state['google_oauth_credentials'] = {
    #                     'token': credentials.token,
    #                     'refresh_token': credentials.refresh_token,
    #                     'token_uri': credentials.token_uri,
    #                     'client_id': credentials.client_id,
    #                     'client_secret': credentials.client_secret,
    #                     'scopes': credentials.scopes
    #                 }
                    
    #                 # Clean up the temporary file
    #                 os.unlink(temp_credentials_path)
                    
    #                 service = build('drive', 'v3', credentials=credentials)
    #                 st.success('Successfully authenticated with Google Drive!')
    #                 st.experimental_rerun()
    #                 return service
    #             except Exception as e:
    #                 st.error(f'Authentication error: {str(e)}')
    #                 return None

    #         # If we haven't completed authentication, stop the app
    #         st.stop()

    #     except Exception as e:
    #         st.error(f"Authentication error: {str(e)}")
    #         return None
    def authenticate_google_drive(self):
        try:
            if 'google_oauth_credentials' in st.session_state:
                credentials = Credentials.from_authorized_user_info(
                    st.session_state['google_oauth_credentials'],
                    SCOPES
                )
                return build('drive', 'v3', credentials=credentials)

            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                credentials_dict = {
                    "web": {
                        "client_id": st.secrets["google_credentials"]["client_id"],
                        "project_id": st.secrets["google_credentials"]["project_id"],
                        "auth_uri": st.secrets["google_credentials"]["auth_uri"],
                        "token_uri": st.secrets["google_credentials"]["token_uri"],
                        "auth_provider_x509_cert_url": st.secrets["google_credentials"]["auth_provider_x509_cert_url"],
                        "client_secret": st.secrets["google_credentials"]["client_secret"],
                        "redirect_uris": st.secrets["google_credentials"]["redirect_uris"]
                    }
                }
                json.dump(credentials_dict, f)
                temp_credentials_path = f.name

            # Store flow in session state to maintain state
            if 'oauth_flow' not in st.session_state:
                flow = InstalledAppFlow.from_client_secrets_file(
                    temp_credentials_path,
                    SCOPES,
                    redirect_uri=st.secrets["google_credentials"]["redirect_uris"][0]
                )
                st.session_state['oauth_flow'] = flow
            
            flow = st.session_state['oauth_flow']
            auth_url, _ = flow.authorization_url(prompt='consent')

            st.markdown("""
            ### Google Drive Authentication Required
            1. Click the link below to authorize this application
            2. After authorization, copy the entire URL from your browser
            3. Paste it back here and click 'Submit'
            """)
            st.markdown(f"[Click here to authorize]({auth_url})", unsafe_allow_html=True)
            
            auth_code = st.text_input('Paste the full URL here:')
            
            if st.button('Submit'):
                try:
                    flow.fetch_token(authorization_response=auth_code)
                    credentials = flow.credentials
                    
                    st.session_state['google_oauth_credentials'] = {
                        'token': credentials.token,
                        'refresh_token': credentials.refresh_token,
                        'token_uri': credentials.token_uri,
                        'client_id': credentials.client_id,
                        'client_secret': credentials.client_secret,
                        'scopes': credentials.scopes
                    }
                    
                    os.unlink(temp_credentials_path)
                    
                    service = build('drive', 'v3', credentials=credentials)
                    st.success('Successfully authenticated with Google Drive!')
                    st.experimental_rerun()
                    return service
                except Exception as e:
                    st.error(f'Authentication error: {str(e)}')
                    return None

            st.stop()

        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            return None
    def list_files(self):
        try:
            results = self.service.files().list(
                q=f"'{self.dictionary_id}' in parents", 
                spaces='drive',
                fields="files(id, name, mimeType, parents)"
            ).execute()

            files = results.get('files', [])
            json_files = [file for file in files if file['name'].endswith('.json') and 'annotation' in [parent['id'] for parent in file.get('parents', [])]]

            return files, json_files
        except HttpError as error:
            st.error(f'An error occurred: {error}')
            return [], []

    def download_file_from_drive(self, file_id):
        try:
            request = self.service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            file.seek(0)
            return Image.open(file)
        except HttpError as error:
            st.error(f'An error occurred: {error}')
            return None

# def initialize_search_engine(drive_service):
#     if 'search_engine' not in st.session_state:
#         try:
#             st.session_state.search_engine = MyFaiss(
#                 bin_clip_file = '1XsdUu-NTVbgXt-ch_OdohsNQyHLdtwHN',
#                 bin_clipv2_file = '1RPKwzzgWqT68rWFEO2xSwLOuAaboVEJu',
#                 json_path = '1ZM-q1El6oV18hpzBIJjwNCDrEhvOx6s2',
#                 drive_service=drive_service
#             )
#             return True
#         except Exception as e:
#             # st.error(f"Error initializing search engine: {str(e)}")
#             # logging.error(f"Search engine initialization error: {str(e)}")
#             return False
#     return True

def initialize_search_engine(drive_service):
    if 'search_engine' not in st.session_state:
        try:
            logging.info("Starting search engine initialization...")
            st.session_state.search_engine = MyFaiss(
                bin_clip_file = '1XsdUu-NTVbgXt-ch_OdohsNQyHLdtwHN',
                bin_clipv2_file = '1RPKwzzgWqT68rWFEO2xSwLOuAaboVEJu',
                json_path = '1ZM-q1El6oV18hpzBIJjwNCDrEhvOx6s2',
                drive_service=drive_service
            )
            logging.info("Search engine initialization complete")
            return True
        except Exception as e:
            logging.error(f"Search engine initialization error: {str(e)}")
            return False
    return True

class StreamlitImageSearch:
    # def __init__(self):
    #     st.set_page_config(
    #         page_title="Image Search Engine",
    #         page_icon="🔍",
    #         layout="wide"
    #     )
        
    #     self.drive_manager = GoogleDriveKeyframeManager()
    #     if not initialize_search_engine(self.drive_manager.service):
    #         st.stop()
        
    #     self.setup_faiss()
    def __init__(self):
        st.set_page_config(
            page_title="Image Search Engine",
            page_icon="🔍",
            layout="wide"
        )
        
        try:
            self.drive_manager = GoogleDriveKeyframeManager()
            if not initialize_search_engine(self.drive_manager.service):
                st.error("Failed to initialize search engine")
                st.stop()
            
            self.setup_faiss()
        except Exception as e:
            st.error(f"Initialization error: {str(e)}")
            logging.error(traceback.format_exc())
            st.stop()

    # def setup_faiss(self):
    #     try:
    #         st.sidebar.header("Google Drive Configuration")

    #         bin_clip_file = '1XsdUu-NTVbgXt-ch_OdohsNQyHLdtwHN'
    #         bin_clipv2_file = '1RPKwzzgWqT68rWFEO2xSwLOuAaboVEJu'
    #         json_path = '1ZM-q1El6oV18hpzBIJjwNCDrEhvOx6s2'

    #         files, json_files = self.drive_manager.list_files()
    #         file_ids = [file['id'] for file in files]
        
    #         self.search_engine = MyFaiss(
    #             bin_clip_file=bin_clip_file,
    #             bin_clipv2_file=bin_clipv2_file,
    #             json_path=json_path,
    #             drive_service=self.drive_manager.service
    #         )
            
    #         st.sidebar.success("Search engine initialized successfully!")
            
    #     except Exception as e:
    #         # st.error(f"Error initializing FAISS search engine: {str(e)}")
    #         import traceback
    #         traceback.format_exc()
    def setup_faiss(self):
        try:
            st.sidebar.header("Google Drive Configuration")
            
            files, json_files = self.drive_manager.list_files()
            file_ids = [file['id'] for file in files]
            
            # Remove duplicate initialization since we already have it in initialize_search_engine
            self.search_engine = st.session_state.search_engine
            
            st.sidebar.success("Search engine initialized successfully!")
            
        except Exception as e:
            logging.error(f"Error in setup_faiss: {str(e)}")
            logging.error(traceback.format_exc())

    def load_and_display_images(self, file_ids: List[str], scores: List[float]):
        cols = st.columns(3)  # Create 3 columns for grid layout

        for idx, (file_id, score) in enumerate(zip(file_ids, scores)):
            try:
                col_idx = idx % 3
                with cols[col_idx]:
                    # Download image from Google Drive
                    image = self.drive_manager.download_file_from_drive(file_id)
                    
                    if image:
                        st.image(image, caption=f"Score: {score:.4f}")
                        with st.expander("Image Details"):
                            st.text(f"Google Drive File ID: {file_id}")
                            st.text(f"Share URL: https://drive.google.com/uc?id={file_id}")
                    else:
                        st.warning(f"Could not load image with ID: {file_id}")
            except Exception as e:
                st.error(f"Error loading image {file_id}: {str(e)}")

    def run(self):
        """Run the Streamlit application"""
        st.title("🔍 Multi-Modal Image Search Engine")
        st.markdown("""
        This application uses CLIP and CLIPv2 models to search for images based on text descriptions.
        Enter your query below to find matching images.
        """)

        st.sidebar.header("Search Settings")
        k_results = st.sidebar.slider("Number of results", 1, 20, 9)
        model_type = st.sidebar.selectbox("Model Type", ["clip", "clip_v2"])

        example_queries = {
            "Scene Description": "Two news anchors in a television studio with a cityscape background",
            "Object Query": "yellow umbrella",
            "Action Query": "people walking on the street",
        }
        
        # Query input with example selection
        selected_example = st.selectbox(
            "Try an example query:", 
            ["Custom Query"] + list(example_queries.keys())
        )
        
        st.markdown("### Enter your search query")

        if selected_example == "Custom Query":
            query = st.text_area(
                "Describe what you're looking for:",
                height=100,
                placeholder="Enter your search query here..."
            )
        else:
            query = example_queries[selected_example]
            st.text_area("Current query:", value=query, height=100, disabled=True)

        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)
        with search_col2:
            st.info(f"Using {model_type.upper()} model")

        if search_clicked:
            if query and 'search_engine' in st.session_state:
                try:
                    with st.spinner(f"Searching with {model_type.upper()} for: '{query}'"):
                        scores, _, infos_query, image_paths = st.session_state.search_engine.text_search(
                            text=query,
                            k=k_results,
                            index=None,
                            model_type=model_type
                        )

                        if not image_paths:
                            st.warning("No images found matching your query.")
                        else:
                            st.markdown(f"### Found {len(image_paths)} results")
                            st.info(f"""
                            🔍 Search Summary:
                            - Query: "{query}"
                            - Model: {model_type.upper()}
                            - Results found: {len(image_paths)}
                            - Top score: {scores[0]:.4f}
                            """)
                            self.load_and_display_images(image_paths, scores)

                except Exception as e:
                    st.error(f"Search error: {str(e)}")
                    logging.error(f"Search error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
            else:
                st.warning("Please enter a search query")

# def main():
#     app = StreamlitImageSearch()
#     app.run()
def main():
    try:
        app = StreamlitImageSearch()
        app.run()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logging.error(traceback.format_exc())
    finally:
        # Cleanup any resources if needed
        if 'search_engine' in st.session_state:
            del st.session_state['search_engine']

if __name__ == "__main__":
    main()