import os
import subprocess

# Set file paths and directories
def extraction(input_dir, output_base_dir):
    # Loop through each video in the input directory
    for idx, input_video in enumerate(os.listdir(input_dir), start=0):
        if input_video == ".DS_Store":
            continue
        
        input_video_path = os.path.join(input_dir, input_video)
        video_name = os.path.splitext(input_video)[0]
        
        # Create parent folder (Video1, Video2, etc.)
        parent_folder_name = f"Video{idx}"
        parent_folder_path = os.path.join(output_base_dir, parent_folder_name)
        
        # Create subdirectories for keyframes and reduced keyframes
        keyframe_dir = os.path.join(parent_folder_path, video_name)
        reduced_keyframe_dir = os.path.join(parent_folder_path, f"{video_name}_reduced")
        
        if not os.path.exists(keyframe_dir):
            os.makedirs(keyframe_dir)
        if not os.path.exists(reduced_keyframe_dir):
            os.makedirs(reduced_keyframe_dir)

        # Get the keyframe timestamps using ffprobe
        ffprobe_command = [
            "../senior-project/packages/ffprobe", "-loglevel", "error", 
            "-select_streams", "v:0", "-show_entries", "packet=pts_time,flags", 
            "-of", "csv=print_section=0", input_video_path
        ]

        # Run the ffprobe command and capture the output
        ffprobe_result = subprocess.run(ffprobe_command, stdout=subprocess.PIPE, text=True)

        # Filter the keyframes (lines containing ",K")
        keyframe_lines = [line.split(",")[0] for line in ffprobe_result.stdout.splitlines() if ",K" in line]

        # Extract keyframes using ffmpeg
        for index, timestamp in enumerate(keyframe_lines, start=1):
            output_image = os.path.join(keyframe_dir, f"keyframe_{index}_{timestamp}.jpg")
            
            ffmpeg_command = [
                "ffmpeg", "-loglevel", "error", 
                "-ss", timestamp, "-i", input_video_path, 
                "-frames:v", "1", output_image
            ]
            
            subprocess.run(ffmpeg_command)
            print(f"Keyframe extracted: {output_image}")

        # Reduce the extracted keyframes and save to reduced directory
        print(f"Keyframes and reduced keyframes saved for {input_video} in {parent_folder_name}")
