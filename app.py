# import streamlit as st
# import os
# import sys
# from PIL import Image
# import logging
# from typing import List, Tuple

# # Configure logging
# logging.basicConfig(level=logging.INFO,
#                    format='%(asctime)s - %(levelname)s - %(message)s')

# # Add the project root to Python path for imports
# PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(PROJECT_ROOT)

# # Import the MyFaiss class and Translation from your backend
# from database_processing.faiss_processing import MyFaiss

# # Define the keyframe directory
# KEYFRAME_DIR = os.path.join(PROJECT_ROOT, 'keyframe_information/keyframe/Video4/L05')

# DEFAULT_PATHS = {
#     'bin_clip_file': os.path.join(PROJECT_ROOT, 'database_processing/faiss_clip.bin'),
#     'bin_clipv2_file': os.path.join(PROJECT_ROOT, 'database_processing/faiss_clipv2_cosine.bin'),
#     'json_path': os.path.join(PROJECT_ROOT, 'keyframe_information/annotation/L05.json')
# }

# def resolve_image_path(relative_path: str) -> str:
#     """Convert relative path to absolute path"""
#     if relative_path.startswith('..'):
#         clean_path = relative_path.replace('../', '')
#         return os.path.join(PROJECT_ROOT, clean_path)
#     return relative_path

# class StreamlitImageSearch:
#     def __init__(self):
#         st.set_page_config(
#             page_title="Image Search Engine",
#             page_icon="🔍",
#             layout="wide"
#         )
        
#         # Initialize MyFaiss
#         self.setup_faiss()

#     def setup_faiss(self):
#         """Initialize the FAISS search engine"""
#         try:
#             # Display current paths in sidebar
#             st.sidebar.header("Current Configuration")
#             st.sidebar.markdown("**Project Root:**")
#             st.sidebar.code(PROJECT_ROOT)

#             # Display keyframe directory
#             st.sidebar.markdown("**Keyframe Directory:**")
#             st.sidebar.code(KEYFRAME_DIR)

#             # Path inputs in sidebar with default values
#             bin_clip_file = st.sidebar.text_input(
#                 "CLIP Binary File Path", 
#                 value=DEFAULT_PATHS['bin_clip_file'])
#             bin_clipv2_file = st.sidebar.text_input(
#                 "CLIPv2 Binary File Path", 
#                 value=DEFAULT_PATHS['bin_clipv2_file'])
#             json_path = st.sidebar.text_input(
#                 "JSON File Path", 
#                 value=DEFAULT_PATHS['json_path'])

#             # Path validation with more detailed feedback
#             for path, name in [(bin_clip_file, "CLIP Binary"), 
#                              (bin_clipv2_file, "CLIPv2 Binary"), 
#                              (json_path, "JSON"),
#                              (KEYFRAME_DIR, "Keyframe Directory")]:
#                 if not os.path.exists(path):
#                     st.sidebar.warning(f"{name} not found at: {path}")
#                 else:
#                     st.sidebar.success(f"{name} found at: {path}")

#             self.search_engine = MyFaiss(
#                 bin_clip_file=bin_clip_file,
#                 bin_clipv2_file=bin_clipv2_file,
#                 json_path=json_path,
#             )
#             logging.info("FAISS search engine initialized successfully")
#             st.sidebar.success("Search engine initialized successfully!")
#         except Exception as e:
#             st.error(f"Error initializing FAISS search engine: {str(e)}")
#             logging.error(f"FAISS initialization error: {str(e)}")
#             import traceback
#             st.code(traceback.format_exc())

#     def load_and_display_images(self, image_paths: List[str], scores: List[float]):
#         """Load and display images in a grid layout"""
#         cols = st.columns(3)  # Create 3 columns for grid layout

#         for idx, (image_path, score) in enumerate(zip(image_paths, scores)):
#             try:
#                 col_idx = idx % 3
#                 with cols[col_idx]:
#                     # Resolve the full image path
#                     full_path = resolve_image_path(image_path)
                    
#                     if os.path.exists(full_path):
#                         image = Image.open(full_path)
#                         st.image(image, caption=f"Score: {score:.4f}")
#                         with st.expander("Image Details"):
#                             st.text(f"Original Path: {image_path}")
#                             st.text(f"Full Path: {full_path}")
#                             # Add frame time from filename
#                             frame_time = os.path.splitext(os.path.basename(full_path))[0].split('_')[-1]
#                             st.text(f"Frame Time: {frame_time} seconds")
#                     else:
#                         st.warning(f"Image not found at: {full_path}")
#                         st.text(f"Original path: {image_path}")
#             except Exception as e:
#                 st.error(f"Error loading image {image_path}: {str(e)}")
#                 logging.error(f"Image loading error: {str(e)}")

#     def run(self):
#         """Run the Streamlit application"""
#         st.title("🔍 Multi-Modal Image Search Engine")
#         st.markdown("""
#         This application uses CLIP and CLIPv2 models to search for images based on text descriptions.
#         Enter your query below to find matching images.
#         """)

#         # Sidebar configurations
#         st.sidebar.header("Search Settings")
#         k_results = st.sidebar.slider("Number of results", 1, 20, 9)
#         model_type = st.sidebar.selectbox("Model Type", ["clip", "clip_v2"])

#         # Example queries
#         example_queries = {
#             "Scene Description": "Two news anchors in a television studio with a cityscape background",
#             "Object Query": "yellow umbrella",
#             "Action Query": "people walking on the street",
#         }

#         # Main search interface
#         st.markdown("### Enter your search query")
        
#         # Query input with example selection
#         selected_example = st.selectbox(
#             "Try an example query:", 
#             ["Custom Query"] + list(example_queries.keys())
#         )
        
#         if selected_example == "Custom Query":
#             query = st.text_area(
#                 "Describe what you're looking for:",
#                 height=100,
#                 placeholder="Enter your search query here..."
#             )
#         else:
#             query = example_queries[selected_example]
#             st.text_area("Current query:", value=query, height=100, disabled=True)

#         # Search button with model selection feedback
#         search_col1, search_col2 = st.columns([3, 1])
#         with search_col1:
#             search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)
#         with search_col2:
#             st.info(f"Using {model_type.upper()} model")

#         if search_clicked:
#             if query:
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
#                             # Display search summary
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


import boto3
import streamlit as st
from PIL import Image
import os
import sys
import logging
from typing import List, Tuple
from io import BytesIO
from database_processing.faiss_processing import MyFaiss
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Now you can access the AWS credentials from environment variables
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)


# Set up S3 client
s3 = boto3.client('s3')

# Define S3 bucket details
S3_BUCKET_NAME = 'shots-spot'
KEYFRAME_DIR = 'keyframe_information/keyframe/Video4/L05'

DEFAULT_PATHS = {
    'bin_clip_file': 's3://shots-spot/faiss_clip.bin',
    'bin_clipv2_file': 's3://shots-spot/faiss_clipv2_cosine.bin',
    'json_path': 's3://shots-spot/keyframe_information/annotation/L05.json'
}


def download_s3_file(s3_path: str) -> BytesIO:
    """Downloads a file from S3 and returns it as a BytesIO object."""
    bucket_name, key = s3_path.replace('s3://', '').split('/', 1)
    file_obj = BytesIO()
    s3.download_fileobj(bucket_name, key, file_obj)
    file_obj.seek(0)
    return file_obj

def resolve_s3_image_path(s3_path: str) -> Image:
    """Load image from S3 and return as PIL Image."""
    file_obj = download_s3_file(s3_path)
    return Image.open(file_obj)

class StreamlitImageSearch:
    def __init__(self):
        st.set_page_config(
            page_title="Image Search Engine",
            page_icon="🔍",
            layout="wide"
        )
        self.setup_faiss()

    def setup_faiss(self):
        """Initialize the FAISS search engine with paths from S3."""
        st.sidebar.header("Current Configuration")
        st.sidebar.markdown("**S3 Bucket:**")
        st.sidebar.code(S3_BUCKET_NAME)

        # Input paths in sidebar with S3 paths
        bin_clip_file = st.sidebar.text_input("CLIP Binary File Path", value=DEFAULT_PATHS['bin_clip_file'])
        bin_clipv2_file = st.sidebar.text_input("CLIPv2 Binary File Path", value=DEFAULT_PATHS['bin_clipv2_file'])
        json_path = st.sidebar.text_input("JSON File Path", value=DEFAULT_PATHS['json_path'])

        self.search_engine = MyFaiss(
            bin_clip_file=download_s3_file(bin_clip_file),
            bin_clipv2_file=download_s3_file(bin_clipv2_file),
            json_path=download_s3_file(json_path),
        )
        logging.info("FAISS search engine initialized with S3 paths")

    def load_and_display_images(self, image_paths: List[str], scores: List[float]):
        """Load and display images in a grid layout from S3."""
        cols = st.columns(3)
        for idx, (image_path, score) in enumerate(zip(image_paths, scores)):
            col_idx = idx % 3
            with cols[col_idx]:
                try:
                    image = resolve_s3_image_path(image_path)
                    st.image(image, caption=f"Score: {score:.4f}")
                except Exception as e:
                    st.error(f"Error loading image {image_path}: {str(e)}")

    def run(self):
        """Run the Streamlit application"""
        st.title("🔍 Multi-Modal Image Search Engine")
        st.markdown("""
        This application uses CLIP and CLIPv2 models to search for images based on text descriptions.
        Enter your query below to find matching images.
        """)

        # Sidebar configurations
        st.sidebar.header("Search Settings")
        k_results = st.sidebar.slider("Number of results", 1, 20, 9)
        model_type = st.sidebar.selectbox("Model Type", ["clip", "clip_v2"])

        # Example queries
        example_queries = {
            "Scene Description": "Two news anchors in a television studio with a cityscape background",
            "Object Query": "yellow umbrella",
            "Action Query": "people walking on the street",
        }

        # Main search interface
        st.markdown("### Enter your search query")
        
        # Query input with example selection
        selected_example = st.selectbox(
            "Try an example query:", 
            ["Custom Query"] + list(example_queries.keys())
        )
        
        if selected_example == "Custom Query":
            query = st.text_area(
                "Describe what you're looking for:",
                height=100,
                placeholder="Enter your search query here..."
            )
        else:
            query = example_queries[selected_example]
            st.text_area("Current query:", value=query, height=100, disabled=True)

        # Search button with model selection feedback
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)
        with search_col2:
            st.info(f"Using {model_type.upper()} model")

        if search_clicked:
            if query:
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
                            # Display search summary
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
