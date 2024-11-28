import streamlit as st
from PIL import Image
import io
import os, sys
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import logging
from typing import List, Tuple
import json

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

# Import the MyFaiss class and Translation from your backend
from database_processing.faiss_processing import MyFaiss

SCOPES = 'https://www.googleapis.com/auth/drive'
keyframes_dir_id = '1bqJG0CRIIuVIib3pBcA2k8iiRyWlwmq9'

class GoogleDriveKeyframeManager:
    def __init__(self, dictionary_id='1l5D8idS8nXKD_E5A0SlM5ok2bE1iMrF1'):
        self.dictionary_id = dictionary_id
        self.service = self.authenticate_google_drive()

    def authenticate_google_drive(self):
        """Authenticate Google Drive using Streamlit secrets service account"""
        try:
            # Use Streamlit secrets for service account credentials
            credentials_dict = st.secrets["google_service_account"]
            
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                credentials_dict,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["google_service_account"], 
                scopes=[SCOPES],
                cache_discovery=False
            )
            service = build('drive', 'v3', credentials=credentials)
            return service
            
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

def initialize_search_engine(drive_service):
    try:
        search_engine = MyFaiss(
            bin_clip_file = '1XsdUu-NTVbgXt-ch_OdohsNQyHLdtwHN',
            bin_clipv2_file = '1RPKwzzgWqT68rWFEO2xSwLOuAaboVEJu',
            json_path = '1ZM-q1El6oV18hpzBIJjwNCDrEhvOx6s2',
            drive_service=drive_service
        )
        return search_engine
    except Exception as e:
        st.error(f"Error initializing search engine: {str(e)}")
        return None

class StreamlitImageSearch:
    def __init__(self):
        st.set_page_config(
            page_title="Image Search Engine",
            page_icon="🔍",
            layout="wide"
        )
        
        self.drive_manager = GoogleDriveKeyframeManager()
        self.search_engine = initialize_search_engine(self.drive_manager.service)
        
        if not self.search_engine:
            st.stop()

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
            if query and self.search_engine:
                try:
                    with st.spinner(f"Searching with {model_type.upper()} for: '{query}'"):
                        scores, _, infos_query, image_paths = self.search_engine.text_search(
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

def main():
    app = StreamlitImageSearch()
    app.run()

if __name__ == "__main__":
    main()
# import streamlit as st
# from PIL import Image
# import io
# import os, sys
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# from googleapiclient.http import MediaIoBaseDownload
# import logging
# from typing import List, Tuple
# import json
# import psutil
# import time
# import plotly.graph_objects as go
# from datetime import datetime, timedelta
# import pandas as pd
# import numpy as np

# # Configure logging
# logging.basicConfig(level=logging.INFO,
#                    format='%(asctime)s - %(levelname)s - %(message)s')

# # Import the MyFaiss class from your backend
# from database_processing.faiss_processing import MyFaiss

# SCOPES = 'https://www.googleapis.com/auth/drive'
# keyframes_dir_id = '1bqJG0CRIIuVIib3pBcA2k8iiRyWlwmq9'

# class MemoryMonitor:
#     def __init__(self):
#         self.memory_history = []
#         self.timestamp_history = []
#         self.process = psutil.Process()
        
#     def get_memory_usage(self):
#         """Get current memory usage stats"""
#         memory = psutil.virtual_memory()
#         process_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
#         return {
#             'total': memory.total / 1024 / 1024 / 1024,  # GB
#             'available': memory.available / 1024 / 1024 / 1024,  # GB
#             'used': memory.used / 1024 / 1024 / 1024,  # GB
#             'process': process_memory,  # MB
#             'percent': memory.percent
#         }
    
#     def update_history(self):
#         """Update memory usage history"""
#         usage = self.get_memory_usage()
#         self.memory_history.append(usage)
#         self.timestamp_history.append(datetime.now())
        
#         # Keep only last 100 points
#         if len(self.memory_history) > 100:
#             self.memory_history.pop(0)
#             self.timestamp_history.pop(0)
    
#     def plot_memory_usage(self):
#         """Create memory usage plots"""
#         # Memory Usage Gauge
#         current_usage = self.get_memory_usage()
        
#         fig_gauge = go.Figure(go.Indicator(
#             mode="gauge+number+delta",
#             value=current_usage['percent'],
#             domain={'x': [0, 1], 'y': [0, 1]},
#             gauge={
#                 'axis': {'range': [None, 100]},
#                 'bar': {'color': "darkblue"},
#                 'steps': [
#                     {'range': [0, 50], 'color': "lightgray"},
#                     {'range': [50, 80], 'color': "gray"},
#                     {'range': [80, 100], 'color': "red"}
#                 ],
#                 'threshold': {
#                     'line': {'color': "red", 'width': 4},
#                     'thickness': 0.75,
#                     'value': 90
#                 }
#             },
#             title={'text': "Memory Usage %"}
#         ))
        
#         # Memory History Line Chart
#         if self.memory_history:
#             df = pd.DataFrame({
#                 'timestamp': self.timestamp_history,
#                 'Used (GB)': [m['used'] for m in self.memory_history],
#                 'Available (GB)': [m['available'] for m in self.memory_history],
#                 'Process (MB)': [m['process'] for m in self.memory_history]
#             })
            
#             fig_history = go.Figure()
#             fig_history.add_trace(go.Scatter(
#                 x=df['timestamp'],
#                 y=df['Used (GB)'],
#                 name='Used Memory (GB)',
#                 line=dict(color='blue')
#             ))
#             fig_history.add_trace(go.Scatter(
#                 x=df['timestamp'],
#                 y=df['Available (GB)'],
#                 name='Available Memory (GB)',
#                 line=dict(color='green')
#             ))
#             fig_history.add_trace(go.Scatter(
#                 x=df['timestamp'],
#                 y=df['Process (MB)'],
#                 name='Process Memory (MB)',
#                 line=dict(color='red'),
#                 yaxis='y2'
#             ))
            
#             fig_history.update_layout(
#                 title='Memory Usage Over Time',
#                 yaxis=dict(title='System Memory (GB)'),
#                 yaxis2=dict(title='Process Memory (MB)', overlaying='y', side='right'),
#                 height=400
#             )
            
#             return fig_gauge, fig_history
        
#         return fig_gauge, None

# class GoogleDriveKeyframeManager:
#     def __init__(self, dictionary_id='1l5D8idS8nXKD_E5A0SlM5ok2bE1iMrF1'):
#         self.dictionary_id = dictionary_id
#         self.service = self.authenticate_google_drive()

#     def authenticate_google_drive(self):
#         """Authenticate Google Drive using Streamlit secrets service account"""
#         try:
#             credentials = service_account.Credentials.from_service_account_info(
#                 st.secrets["google_service_account"], 
#                 scopes=[SCOPES]
#             )
#             service = build('drive', 'v3', credentials=credentials)
#             return service
            
#         except Exception as e:
#             st.error(f"Authentication error: {str(e)}")
#             return None

#     def list_files(self):
#         try:
#             results = self.service.files().list(
#                 q=f"'{self.dictionary_id}' in parents", 
#                 spaces='drive',
#                 fields="files(id, name, mimeType, parents)"
#             ).execute()

#             files = results.get('files', [])
#             json_files = [file for file in files if file['name'].endswith('.json') and 'annotation' in [parent['id'] for parent in file.get('parents', [])]]

#             return files, json_files
#         except HttpError as error:
#             st.error(f'An error occurred: {error}')
#             return [], []

#     def download_file_from_drive(self, file_id):
#         try:
#             request = self.service.files().get_media(fileId=file_id)
#             file = io.BytesIO()
#             downloader = MediaIoBaseDownload(file, request)
#             done = False
#             while done is False:
#                 status, done = downloader.next_chunk()
            
#             file.seek(0)
#             return Image.open(file)
#         except HttpError as error:
#             st.error(f'An error occurred: {error}')
#             return None

# def initialize_search_engine(drive_service):
#     try:
#         search_engine = MyFaiss(
#             bin_clip_file = '1XsdUu-NTVbgXt-ch_OdohsNQyHLdtwHN',
#             bin_clipv2_file = '1RPKwzzgWqT68rWFEO2xSwLOuAaboVEJu',
#             json_path = '1ZM-q1El6oV18hpzBIJjwNCDrEhvOx6s2',
#             drive_service=drive_service
#         )
#         return search_engine
#     except Exception as e:
#         st.error(f"Error initializing search engine: {str(e)}")
#         return None

# class StreamlitImageSearch:
#     def __init__(self):
#         st.set_page_config(
#             page_title="Image Search Engine",
#             page_icon="🔍",
#             layout="wide"
#         )
        
#         self.drive_manager = GoogleDriveKeyframeManager()
#         self.search_engine = initialize_search_engine(self.drive_manager.service)
#         self.memory_monitor = MemoryMonitor()
        
#         if not self.search_engine:
#             st.stop()

#     def load_and_display_images(self, file_ids: List[str], scores: List[float]):
#         cols = st.columns(3)  # Create 3 columns for grid layout

#         for idx, (file_id, score) in enumerate(zip(file_ids, scores)):
#             try:
#                 col_idx = idx % 3
#                 with cols[col_idx]:
#                     image = self.drive_manager.download_file_from_drive(file_id)
                    
#                     if image:
#                         st.image(image, caption=f"Score: {score:.4f}")
#                         with st.expander("Image Details"):
#                             st.text(f"Google Drive File ID: {file_id}")
#                             st.text(f"Share URL: https://drive.google.com/uc?id={file_id}")
#                     else:
#                         st.warning(f"Could not load image with ID: {file_id}")
#             except Exception as e:
#                 st.error(f"Error loading image {file_id}: {str(e)}")

#     def display_memory_metrics(self):
#         """Display memory usage metrics"""
#         st.sidebar.markdown("### Memory Usage Metrics")
        
#         # Update memory history
#         self.memory_monitor.update_history()
        
#         # Get current memory stats
#         memory_stats = self.memory_monitor.get_memory_usage()
        
#         # Display current stats
#         col1, col2 = st.sidebar.columns(2)
#         col1.metric("Total Memory (GB)", f"{memory_stats['total']:.1f}")
#         col2.metric("Used Memory (GB)", f"{memory_stats['used']:.1f}")
        
#         col3, col4 = st.sidebar.columns(2)
#         col3.metric("Available (GB)", f"{memory_stats['available']:.1f}")
#         col4.metric("Process (MB)", f"{memory_stats['process']:.1f}")
        
#         # Plot memory usage
#         gauge_fig, history_fig = self.memory_monitor.plot_memory_usage()
        
#         st.sidebar.plotly_chart(gauge_fig, use_container_width=True)
#         if history_fig:
#             st.sidebar.plotly_chart(history_fig, use_container_width=True)

#     def run(self):
#         """Run the Streamlit application"""
#         st.title("🔍 Multi-Modal Image Search Engine")
#         st.markdown("""
#         This application uses CLIP and CLIPv2 models to search for images based on text descriptions.
#         Enter your query below to find matching images.
#         """)

#         # Display memory metrics in sidebar
#         self.display_memory_metrics()

#         st.sidebar.header("Search Settings")
#         k_results = st.sidebar.slider("Number of results", 1, 20, 9)
#         model_type = st.sidebar.selectbox("Model Type", ["clip", "clip_v2"])

#         example_queries = {
#             "Scene Description": "Two news anchors in a television studio with a cityscape background",
#             "Object Query": "yellow umbrella",
#             "Action Query": "people walking on the street",
#         }
        
#         # Query input with example selection
#         selected_example = st.selectbox(
#             "Try an example query:", 
#             ["Custom Query"] + list(example_queries.keys())
#         )
        
#         st.markdown("### Enter your search query")

#         if selected_example == "Custom Query":
#             query = st.text_area(
#                 "Describe what you're looking for:",
#                 height=100,
#                 placeholder="Enter your search query here..."
#             )
#         else:
#             query = example_queries[selected_example]
#             st.text_area("Current query:", value=query, height=100, disabled=True)

#         search_col1, search_col2 = st.columns([3, 1])
#         with search_col1:
#             search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)
#         with search_col2:
#             st.info(f"Using {model_type.upper()} model")

#         if search_clicked:
#             if query and self.search_engine:
#                 try:
#                     with st.spinner(f"Searching with {model_type.upper()} for: '{query}'"):
#                         scores, _, infos_query, image_paths = self.search_engine.text_search(
#                             text=query,
#                             k=k_results,
#                             index=None,
#                             model_type=model_type
#                         )

#                         if not image_paths:
#                             st.warning("No images found matching your query.")
#                         else:
#                             st.markdown(f"### Found {len(image_paths)} results")
#                             st.info(f"""
#                             🔍 Search Summary:
#                             - Query: "{query}"
#                             - Model: {model_type.upper()}
#                             - Results found: {len(image_paths)}
#                             - Top score: {scores[0]:.4f}
#                             """)
#                             self.load_and_display_images(image_paths, scores)

#                 except Exception as e:
#                     st.error(f"Search error: {str(e)}")
#                     logging.error(f"Search error: {str(e)}")
#                     import traceback
#                     st.code(traceback.format_exc())
#             else:
#                 st.warning("Please enter a search query")

# def main():
#     app = StreamlitImageSearch()
#     app.run()

# if __name__ == "__main__":
#     main()