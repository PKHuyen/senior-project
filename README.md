# How to Download for Metadata Retrieval
### Installing using PIP
`pip install -r requirements.txt`

### keyframe_extraction/extract_keyframes.ipynb
- Download ffmpeg (you will also need this) https://www.ffmpeg.org/download.html
- Follow this instruction: https://www.reddit.com/r/ffmpeg/comments/116alkt/how_do_i_use_ffprobe_without_installing_ffmpeg/
- Contact Harley Phung (hkp15@case.edu) if needed

### metadata_extraction/object_recognition.ipynb
- We used mediapipe and followed the instruction from this website https://ai.google.dev/edge/mediapipe/solutions/vision/object_detector/python
- Need to install the recommended version from this website https://ai.google.dev/edge/mediapipe/solutions/vision/object_detector/index#models

# Workflow for backend
### Keyframe extraction (in keyframe_extraction folder)
1. extract_keyframe.ipynb
- Input: Videos
- Process: 
    - Using `ffprobe` to get a list of keyframes -> get timestamp of keyframe
    - Using `ffmpeg` to get .jpg from the timestamp
    - Save those .jpg to `keyframe_information/keyframe/<video_name>`
    - Convert .jpg to .webp and stored in `keyframe_information/keyframe/<video_name>_reduced`
- Output:
    - `keyframe_information/keyframe/<video_name>` and `keyframe_information/keyframe/<video_name>_reduced` (.jpg and .webp)

2. get_metadata_json.ipynb
- Input: keyframe_information/keyframe/<video_name>
- Output: For each video, there will be one .json file stored in  keyframe_information/annotation/<video_name>.json that contained information of keyframes
    - Image path: This is keyframe path `keyframe_information/keyframe/<video_name>/<keyframe_name>`
    - Video ID: Video name
    - Timestamp: This is time in the video when keyframe is extracted

### Metadata Extraction (Color, Text, Object) in metadata_extraction folder
1. color_recognition.ipynb
- Input: keyframe_information/keyframe/<video_name>
- Process:
    - Using customizable color_palette and sklearn.cluster to find closest color and identify that color. 
- Output: `keyframe_information/color_metadata/<video_name>` 
    - Each file should contained x_coord, y_coord, color (maybe range or x,y coord?)

2. object_recognition.ipynb
- Input: keyframe_information/keyframe/<video_name>
- Process: 
    - Using `mediapipe` and Google's object detection guide (link in how to download)
- Output: `keyframe_information/object_metadata/<video_name>`
    - Object location: xmin, ymin, width, height
    - Score: Accuracy probability
    - Category_name

3. text_recognition.ipynb
- Input: keyframe_information/keyframe/<video_name>
- Process: 
    - Using `easyocr` and only read English (we can add more later)
- Output: `keyframe_information/object_metadata/<video_name>`
    - Words that is recognized and have high accuracy rate (> 0.5)

# Notes
- Must change ffprobe and ffmpeg command line so that it matched with your directory when you download these packages. For example, mine is stored in ~/Downloads/ffprobe so my command is actually 
```
ffprobe_command = [
    "/Users/huyenphung/Downloads/ffprobe", "-loglevel", "error", 
    "-select_streams", "v:0", "-show_entries", "packet=pts_time,flags", 
    "-of", "csv=print_section=0", input_video
]
``` 
- Also be mindful about paths (input, output). Need clean code for this but later

1. keyframe_extraction
`extract_keyframes.ipynb`
This contains extract_keyframes.ipynb that using ffprobe and ffmpeg to extract keyframes based on the following command line

`ffprobe -loglevel error -select_streams v:0 -show_entries packet=pts_time,flags -of csv=print_section=0 Desktop/backend/video/<video_name>.mp4 | grep ",K"` 

This allows user to get frame that have annotation "K" which is keyframe. The output of this command line is `timestamp,<annotation>` 

From this, we can get timestamp and use ffmpeg to retrieve image at that timestamp
`ffmpeg -ss "$ts" -i "$input_video" -frames:v 1 "$output_dir/keyframe_$index.jpg"`

The keyframe will be named `keyframe_<timestamp'>`. We should discuss about this naming

`get_metadata_json`
This is to get metadata of keyframe. Input is `keyframe_information/keyframe`. Output is `keyframe_infomation/annotation`


2. keyframe_infomation 
This is output of keyframe_extraction

3. metadata_extraction
- Need to work on color, optical, object

4. vector_database
- Make CLIP, vector_database (.bin), FAISS

5. video
List of video. Currently 1 but will abstract later.

# Contact
- hkp15@case.edu if need videos