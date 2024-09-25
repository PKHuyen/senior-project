1. keyframe_extraction
This contains extract_keyframes.ipynb that using ffprobe and ffmpeg to extract keyframes based on the following command line

`ffprobe -loglevel error -select_streams v:0 -show_entries packet=pts_time,flags -of csv=print_section=0 Desktop/backend/video/<video_name>.mp4 | grep ",K"` 

This allows user to get frame that have annotation "K" which is keyframe. The output of this command line is `timestamp,<annotation>` 

From this, we can get timestamp and use ffmpeg to retrieve image at that timestamp
`ffmpeg -ss "$ts" -i "$input_video" -frames:v 1 "$output_dir/keyframe_$index.jpg"`

2. keyframe_infomation 
This is output of keyframe_extraction

3. metadata_extraction
- Need to work on color, optical, object

4. vector_database
- Make CLIP, vector_database (.bin), FAISS

5. video
List of video. Currently 1 but will abstract later.