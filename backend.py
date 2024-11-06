############# Run Notebook ###############
import os
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
run_notebook("keyframe_extraction/extract_keyframes.ipynb")

############# Annotation ###############
run_notebook("keyframe_extraction/get_metadata_json.ipynb")

############# CLIP ###############
run_notebook("database_processing/clip.ipynb")

############# CLIPv2 ###############
run_notebook("database_processing/clipv2.ipynb")

############# create_bin ###############
run_notebook("database_processing/create_bin.ipynb")