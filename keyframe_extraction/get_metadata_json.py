import os
import json

os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
def get_image_paths(single_key_frame_folder, video_ID):
    image_video_dict = {}
    idx = 0
    for img_name in sorted(os.listdir(single_key_frame_folder)):
        img_path = os.path.join(single_key_frame_folder, img_name)
        frame_timestamp = img_name.replace('.jpg','')
        image_video_dict[idx] = {'frame_path': f'.{img_path}', 'video_ID': video_ID, 'timestamp': frame_timestamp}
        idx += 1
    return image_video_dict

def save_json(data, output_folder, filename):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    file_path = os.path.join(output_folder, filename)
    
    with open(file_path, 'w') as outfile:
        json.dump(data, outfile, indent=4)

def process_keyframe_folders(multiple_key_frame_folder, output_folder):
    for video_folder in sorted(os.listdir(multiple_key_frame_folder)):
        video_folder_path = os.path.join(multiple_key_frame_folder, video_folder)

        # Check if it's a directory (e.g., Video1, Video2)
        if os.path.isdir(video_folder_path):
            for video in sorted(os.listdir(video_folder_path)):
                if '_reduced' in video:
                    continue
                
                video_ID = video_folder  # Use the outer folder (e.g., Video1) as the video ID
                single_key_frame_folder = os.path.join(video_folder_path, video)
                
                image_info_dict = get_image_paths(single_key_frame_folder, video_ID)
                
                filename = f'{video}.json'
                save_json(image_info_dict, output_folder, filename)
