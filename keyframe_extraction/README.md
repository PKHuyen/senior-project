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

# Notes
- Change ffmpeg command line (if needed) so that it matched with your directory when you download these packages. 
```
ffmpeg_command = [
            "ffmpeg", "-loglevel", "error", 
            "-ss", timestamp, "-i", input_video_path, 
            "-frames:v", "1", output_image
        ]
```
To do so, you can ```which ffmpeg``` in terminal, and update to the ```ffmpeg``` part of previous code
- Also be mindful about paths (input, output). Need clean code for this but later

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
