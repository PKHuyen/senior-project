# import clip
# import open_clip
# import torch
# import json
# import faiss
# import numpy as np
# import logging
# import tempfile
# import os
# from io import BytesIO

# os.environ['KMP_DUPLICATE_LIB_OK']='True'

# # Configure logging
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(message)s')


# class MyFaiss:
#     def __init__(self, bin_clip_file: str, bin_clipv2_file: str, json_path: str):
#         logging.info("Initializing MyFaiss")
#         self.index_clip = self.load_bin_file(bin_clip_file)
#         self.index_clipv2 = self.load_bin_file(bin_clipv2_file)
#         self.id2img_fps = self.load_json_file(json_path)
#         self.__device = "cuda" if torch.cuda.is_available() else "cpu"
#         logging.info(f"Using device: {self.__device}")
#         self.clip_model, _ = clip.load("ViT-B/16", device=self.__device)
#         self.clipv2_model, _, _ = open_clip.create_model_and_transforms(
#             'ViT-L-14', device=self.__device, pretrained='datacomp_xl_s13b_b90k')
#         self.clipv2_tokenizer = open_clip.get_tokenizer('ViT-L-14')
#         logging.info("MyFaiss initialization complete")

#     # def load_json_file(self, json_path: str):
#     #     logging.info(f"Loading JSON file: {json_path}")
#     #     with open(json_path, 'r') as f:
#     #         js = json.load(f)
#     #     return {int(k): v for k, v in js.items()}
#     def load_json_file(self, json_path):
#         if isinstance(json_path, BytesIO):
#             # Read directly from the BytesIO object
#             json_path.seek(0)  # Ensure we're at the start of the file
#             return json.load(json_path)
#         else:
#             # Handle case when json_path is a file path string
#             with open(json_path, 'r') as f:
#                 return json.load(f)

#     # def load_bin_file(self, bin_file: str):
#     #     logging.info(f"Loading bin file: {bin_file}")
#     #     return faiss.read_index(bin_file)


#     def load_bin_file(self, bin_file):
#         if isinstance(bin_file, BytesIO):
#             # Create a temporary file to hold the BytesIO data
#             with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#                 temp_file.write(bin_file.read())
#                 temp_file_path = temp_file.name
#             return faiss.read_index(temp_file_path)
#         else:
#             return faiss.read_index(bin_file)


#     def text_search(self, text, index, k, model_type):
#         logging.info(
#             f"Performing text search with query: '{text}', model: {model_type}, k: {k}")
#         # text = self.translater(text)
#         logging.info(f"Translated text: '{text}'")

#         if model_type == 'clip':
#             text = clip.tokenize([text]).to(self.__device)
#             text_features = self.clip_model.encode_text(text)
#         else:
#             text = self.clipv2_tokenizer([text]).to(self.__device)
#             text_features = self.clipv2_model.encode_text(text)

#         text_features /= text_features.norm(dim=-1, keepdim=True)
#         text_features = text_features.cpu().detach().numpy().astype(np.float32)

#         index_choosed = self.index_clip if model_type == 'clip' else self.index_clipv2

#         if index is None:
#             scores, idx_image = index_choosed.search(text_features, k=k)
#         else:
#             logging.info(f"Using custom index with {len(index)} items")
#             id_selector = faiss.IDSelectorArray(index)
#             scores, idx_image = index_choosed.search(text_features, k=k,
#                                                     params=faiss.SearchParametersIVF(sel=id_selector))
#         idx_image = idx_image.flatten()

#         # Get query info and filter out None values
#         infos_query = [self.id2img_fps.get(idx) for idx in list(idx_image)]
#         infos_query = [info for info in infos_query if info is not None]

#         # Check if 'frame_path' key exists and is not None
#         image_paths = [info['frame_path'] for info in infos_query if info and 'frame_path' in info]
        
#         logging.info(f"Text search complete. Found {len(image_paths)} results.")
#         return scores.flatten(), idx_image, infos_query, image_paths
    



import clip
import open_clip
import torch
import json
import faiss
import numpy as np
import logging
<<<<<<< Updated upstream

import os
=======
import tempfile
import os
from io import BytesIO
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
>>>>>>> Stashed changes
os.environ['KMP_DUPLICATE_LIB_OK']='True'

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class MyFaiss:
    def __init__(self, bin_clip_file, bin_clipv2_file, json_path, drive_service=None):
        logging.info("Initializing MyFaiss")
        self.drive_service = drive_service
        
        # Load binary files 
        self.index_clip = self.load_bin_file(bin_clip_file)
        self.index_clipv2 = self.load_bin_file(bin_clipv2_file)
        
        # Load JSON mapping
        self.id2img_fps = self.load_json_file(json_path)
        
        # Model and device setup
        self.__device = "cuda" if torch.cuda.is_available() else "cpu"
        logging.info(f"Using device: {self.__device}")
        self.clip_model, _ = clip.load("ViT-B/16", device=self.__device)
        self.clipv2_model, _, _ = open_clip.create_model_and_transforms(
            'ViT-L-14', device=self.__device, pretrained='datacomp_xl_s13b_b90k')
        self.clipv2_tokenizer = open_clip.get_tokenizer('ViT-L-14')
        logging.info("MyFaiss initialization complete")

<<<<<<< Updated upstream
    def load_json_file(self, json_path: str):
        logging.info(f"Loading JSON file: {json_path}")
        with open(json_path, 'r') as f:
            js = json.load(f)
        return {int(k): v for k, v in js.items()}

    def load_bin_file(self, bin_file: str):
        logging.info(f"Loading bin file: {bin_file}")
        return faiss.read_index(bin_file)
=======
    def load_bin_file(self, bin_file):
        # If it's a BytesIO object, use it directly
        if isinstance(bin_file, BytesIO):
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(bin_file.read())
                temp_file_path = temp_file.name
            return faiss.read_index(temp_file_path)
        
        # If it's a file path, use it directly
        if os.path.exists(bin_file):
            return faiss.read_index(bin_file)
        
        # If it's a Google Drive file ID
        if self.drive_service:
            return self.load_bin_file_from_drive(bin_file)
        
        raise ValueError(f"Cannot load binary file: {bin_file}")

    # def load_bin_file_from_drive(self, file_id):
    #     try:
    #         # First, get the file metadata
    #         file_metadata = self.drive_service.files().get(fileId=file_id).execute()
            
    #         # Check if the file needs export
    #         if file_metadata.get('mimeType') != 'application/octet-stream':
    #             # Request to export as binary
    #             request = self.drive_service.files().get_media(fileId=file_id)
    #         else:
    #             # Directly download if it's already a binary file
    #             request = self.drive_service.files().get_media(fileId=file_id)
            
    #         file = BytesIO()
    #         downloader = MediaIoBaseDownload(file, request)
    #         done = False
    #         while done is False:
    #             status, done = downloader.next_chunk()
            
    #         file.seek(0)
    #         with tempfile.NamedTemporaryFile(delete=False) as temp_file:
    #             temp_file.write(file.read())
    #             temp_file_path = temp_file.name
            
    #         return faiss.read_index(temp_file_path)
    #     except HttpError as error:
    #         logging.error(f"Error loading bin file from Drive: {error}")
    #         raise

    def load_bin_file_from_drive(self, file_id):
        try:
            # First, get the file metadata
            file_metadata = self.drive_service.files().get(fileId=file_id).execute()
            
            # If the file is a Google Docs file (or other editable file like Sheets/Slides), export it
            mime_type = file_metadata.get('mimeType')
            
            if mime_type in ['application/vnd.google-apps.document', 
                            'application/vnd.google-apps.spreadsheet', 
                            'application/vnd.google-apps.presentation']:
                # Export the file to binary (e.g., PDF or any other suitable format)
                export_mime_type = 'application/pdf'  # You can change this to another format if needed
                request = self.drive_service.files().export_media(fileId=file_id, mimeType=export_mime_type)
            else:
                # If the file is already in binary format, simply get the media
                request = self.drive_service.files().get_media(fileId=file_id)

            # Download the file to a BytesIO object
            file = BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()

            file.seek(0)
            
            # Save to a temporary file and read it using FAISS
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file.read())
                temp_file_path = temp_file.name
            
            return faiss.read_index(temp_file_path)
            
        except HttpError as error:
            logging.error(f"Error loading bin file from Drive: {error}")
            raise

    def load_json_file(self, json_path):
        # If it's a BytesIO object, use it directly
        if isinstance(json_path, BytesIO):
            json_path.seek(0)
            return json.load(json_path)
        
        # If it's a file path, use it directly
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                return json.load(f)
        
        # If it's a Google Drive file ID
        if self.drive_service:
            return self.load_json_file_from_drive(json_path)
        
        raise ValueError(f"Cannot load JSON file: {json_path}")

    def load_json_file_from_drive(self, file_id):
        try:
            request = self.drive_service.files().get_media(fileId=file_id)
            file = BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            file.seek(0)
            return json.load(file)
        except Exception as e:
            logging.error(f"Error loading JSON file from Drive: {e}")
            raise
>>>>>>> Stashed changes

    def text_search(self, text, index, k, model_type):
        logging.info(
            f"Performing text search with query: '{text}', model: {model_type}, k: {k}")
        # text = self.translater(text)
        logging.info(f"Translated text: '{text}'")

        if model_type == 'clip':
            text = clip.tokenize([text]).to(self.__device)
            text_features = self.clip_model.encode_text(text)
        else:
            text = self.clipv2_tokenizer([text]).to(self.__device)
            text_features = self.clipv2_model.encode_text(text)

        text_features /= text_features.norm(dim=-1, keepdim=True)
        text_features = text_features.cpu().detach().numpy().astype(np.float32)

        index_choosed = self.index_clip if model_type == 'clip' else self.index_clipv2

        if index is None:
            scores, idx_image = index_choosed.search(text_features, k=k)
        else:
            logging.info(f"Using custom index with {len(index)} items")
            id_selector = faiss.IDSelectorArray(index)
            scores, idx_image = index_choosed.search(text_features, k=k,
                                                    params=faiss.SearchParametersIVF(sel=id_selector))
        idx_image = idx_image.flatten()

        # Get query info and filter out None values
        infos_query = [self.id2img_fps.get(idx) for idx in list(idx_image)]
        infos_query = [info for info in infos_query if info is not None]

        # Instead of returning local paths, return Google Drive file IDs
        image_file_ids = [info['frame_path'] for info in infos_query if info and 'frame_path' in info]
        
        return scores.flatten(), idx_image, infos_query, image_file_ids