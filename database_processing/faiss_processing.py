import os
import dropbox
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import logging
import clip
import open_clip
import torch
import json
import faiss
import numpy as np
from keyframe_extraction.extract_keyframes import extraction
from keyframe_extraction.get_metadata_json import process_keyframe_folders

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

os.environ['KMP_DUPLICATE_LIB_OK']='True'

class MyFaiss:
    def __init__(self, bin_clip_file: str, bin_clipv2_file: str, json_path: str):
        logging.info("Initializing MyFaiss")
        self.index_clip = self.load_bin_file(bin_clip_file)
        self.index_clipv2 = self.load_bin_file(bin_clipv2_file)
        self.id2img_fps = self.load_json_file(json_path)
        self.__device = "cuda" if torch.cuda.is_available() else "cpu"
        logging.info(f"Using device: {self.__device}")
        self.clip_model, _ = clip.load("ViT-B/16", device=self.__device)
        self.clipv2_model, _, _ = open_clip.create_model_and_transforms(
            'ViT-L-14', device=self.__device, pretrained='datacomp_xl_s13b_b90k')
        self.clipv2_tokenizer = open_clip.get_tokenizer('ViT-L-14')
        logging.info("MyFaiss initialization complete")

    def load_json_file(self, json_path: str):
        logging.info(f"Loading JSON file: {json_path}")
        with open(json_path, 'r') as f:
            js = json.load(f)
        return {int(k): v for k, v in js.items()}

    def load_bin_file(self, bin_file: str):
        logging.info(f"Loading bin file: {bin_file}")
        return faiss.read_index(bin_file)

    def text_search(self, text, index, k, model_type):
        logging.info(
            f"Performing text search with query: '{text}', model: {model_type}, k: {k}")
        
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

        infos_query = [self.id2img_fps.get(idx) for idx in list(idx_image)]
        infos_query = [info for info in infos_query if info is not None]
        image_paths = [info['frame_path'] for info in infos_query if info and 'frame_path' in info]
        
        logging.info(f"Text search complete. Found {len(image_paths)} results.")
        return scores.flatten(), idx_image, infos_query, image_paths

def main():
    logging.info("Starting video processing pipeline")
    
    # Set paths
    base_dir = "../senior-project"
    dropbox_folder_path = "/video"
    local_folder_path = os.path.join(base_dir, "video")
    keyframe_output_path = os.path.join(base_dir, "keyframe_information/keyframe/")
    annotation_output_path = os.path.join(base_dir, "keyframe_information/annotation/")

    try:
        faiss_instance = MyFaiss(
            bin_clip_file=os.path.join(base_dir, "database_processing/clip.bin"),
            bin_clipv2_file=os.path.join(base_dir, "database_processing/clipv2.bin"),
            json_path=os.path.join(base_dir, "keyframe_information/annotation/all_frames.json")
        )
        logging.info("FAISS initialization successful")
    except Exception as e:
        logging.error(f"Failed to initialize FAISS: {str(e)}")
        return
    
    logging.info("Pipeline completed successfully")
    return faiss_instance

if __name__ == "__main__":
    faiss_instance = main()