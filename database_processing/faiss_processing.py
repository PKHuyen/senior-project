# from nlp_processing import Translation
import clip
import open_clip
import torch
import json
import faiss
import numpy as np
import logging

import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
# from utils.object_retrieval_engine.object_retrieval import object_retrieval
# from utils.semantic_embed.speech_retrieval import speech_retrieval
# from utils.ocr_retrieval_engine.ocr_retrieval import ocr_retrieval
# from utils.combine_utils import merge_searching_results_by_addition

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class MyFaiss:
    def __init__(self, bin_clip_file: str, bin_clipv2_file: str, json_path: str, audio_json_path: str, img2audio_json_path: str):
        logging.info("Initializing MyFaiss")
        # self.index_clip = self.load_bin_file(bin_clip_file)
        self.index_clipv2 = self.load_bin_file(bin_clipv2_file)
        # self.object_retrieval = object_retrieval()
        # self.ocr_retrieval = ocr_retrieval()
        # self.asr_retrieval = speech_retrieval()

        self.id2img_fps = self.load_json_file(json_path)
        # self.audio_id2img_id = self.load_json_file(audio_json_path)
        # self.img_id2audio_id = self.load_json_file(img2audio_json_path)
        # self.translater = Translation()
        self.__device = "cuda" if torch.cuda.is_available() else "cpu"
        logging.info(f"Using device: {self.__device}")
        # self.clip_model, _ = clip.load("ViT-B/16", device=self.__device)
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

        # Check if 'frame_path' key exists and is not None
        image_paths = [info['frame_path'] for info in infos_query if info and 'frame_path' in info]
        
        logging.info(f"Text search complete. Found {len(image_paths)} results.")
        return scores.flatten(), idx_image, infos_query, image_paths




def main():
    logging.info("Starting MyFaiss main process")
    bin_file = '../database_processing/faiss_clipv2_cosine.bin'
    # bin_file = '/Users/huyenphung/Desktop/senior-project/database_processing/faiss_clip.bin'
    json_path = '../keyframe_information/annotation/L00.json'

    # Clip
    # cosine_faiss = MyFaiss(
    #     bin_clip_file=bin_file,
    #     bin_clipv2_file=None,
    #     json_path=json_path,
    #     audio_json_path=None,
    #     img2audio_json_path=None)
    
    #Clip_V2
    cosine_faiss = MyFaiss(
        bin_clip_file=None,
        bin_clipv2_file=bin_file,
        json_path=json_path,
        audio_json_path=None,
        img2audio_json_path=None)

    # # Image search
    # logging.info("Performing image search")
    # i_scores, _, infos_query, i_image_paths = cosine_faiss.image_search(
    #     id_query=0, k=9)
    # logging.info(f"Image search complete. Found {len(i_image_paths)} results.")

    # Text search
    logging.info("Performing text search")
    # 0012
    text = 'yellow umbrella'

    scores, _, infos_query, image_paths = cosine_faiss.text_search(
        text, k=3, index=None, model_type='clip_v2')
    logging.info(f"Text search complete. Found {len(image_paths)} results.")

    # Print out all image paths with their scores
    logging.info("Retrieved image paths and scores:")
    for i, (score, path) in enumerate(zip(scores, image_paths), 1):
        logging.info(f"{i}. Score: {score:.4f}, Path: {path}")

    logging.info("MyFaiss main process completed")


if __name__ == "__main__":
    main()