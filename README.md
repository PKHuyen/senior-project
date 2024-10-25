# Video Retrival Timeframe
## Videos:
https://drive.google.com/drive/folders/1txH1iI2nWMMkay2jYyHOQqyIfISkLytK?usp=sharing

## Project Overview
For our senior project, we are tackling the complex challenge of efficiently retrieving video frame data by developing a sophisticated infrastructure utilizing a vector database to store and manage video frames. This innovative system is designed to enable users to swiftly retrieve specific frames based on nuanced text queries or intuitive UI toggles, significantly improving both accessibility and precision in video content analysis.

## Project Struture
### Database_processing 
- clip.ipynb & clipv2.ipynb: \
    - Main Goal: 
        - Train the models based on the preexisting keyframe library generated from keyframe_extraction 
        - Have two files, each with different models to compare the accuracy and speed of each retrieval \

    - Input: keyframes extracted from the initial video \
    - Output:
        - CLIP_features
        - CLIPv2_features
        - These two folders contain a .npy file with metadata related to the keyframe such as color, shape, object… etc 

- Create_bin.ipynb
    - Main Goal: Creates bin for each of the CLIP_features and CLIPv2_features


### Keyframe_extraction: 
- Extract_keyframes.ipynb
    - Main Goal: Using ffprobe and ffmpeg to extract keyframes from videos. The keyframes extracted are unique. The extracted keyframes are named /Video{index}/keyframe_{index}_{timestamp}
    - Input: ./video
    - Output: ./keyframe_information/keyframe

- Get_metadata_json:
    - Main Goal: Create a .json file for each video that contains information of keyframes of that profile. The information included: frame_path, video_id, timestamp
    - Input: ./keyframe_information/keyframe
    - Output: ./keyframe_information/annotation

### Metadata_extraction:
    - Color_recognition.ipynb:
        - Main Goal: Recognize colors and extract metadata to json files using scikit-learn. The information included: bounding_box, color
        - Input: ./keyframe_information/keyframe
        - Output: ./keyframe_information/color_metadata
    - Object_recognition.ipynb:
        - Main Goal: Recognize objects and extract metadata to json files using MediaPipe. The information included bounding_box, score, category_name
        - Input: ./keyframe_information/keyframe
        - Output: ./keyframe_information/object_metadata
    - Text_recognition.ipynb:
        - Main Goal: Recognize text and extract metadata to .json file using EasyOCR. The information should include text
        - Input: ./keyframe_information/keyframe
        - Output: ./keyframe_information/text_metadata

### Packages: Tools for metadata_extraction
