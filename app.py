# from flask import Flask, request, jsonify, make_response
# from flask_cors import CORS
# import logging
# import os
# import json
# from database_processing.faiss_processing import MyFaiss

# # Configure logging
# logging.basicConfig(level=logging.INFO,
#                    format='%(asctime)s - %(levelname)s - %(message)s')

# # Get the absolute path of the current directory
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# # Initialize MyFaiss with absolute paths
# cosine_faiss = MyFaiss(
#     bin_clip_file=None,
#     bin_clipv2_file=os.path.join(BASE_DIR, 'database_processing', 'faiss_clipv2_cosine.bin'),
#     json_path=os.path.join(BASE_DIR, 'keyframe_information', 'annotation', 'L00.json'),
#     audio_json_path=None,
#     img2audio_json_path=None
# )

# app = Flask(__name__)
# CORS(app)

# scores, _, infos_query, image_paths = cosine_faiss.text_search("yellow umbrella", None, 3, 'clip_v2')

# # Create a dictionary to store the results
# search_results = {
#     'success': True,
#     'results': []
# }

# # Format and store the results
# for score, path in zip(scores, image_paths):
#     search_results['results'].append({
#         'score': float(score),
#         'path': path,
#         'timestamp': '00:00:00'
#     })

# # Print the results
# print("Search Results:")
# print(json.dumps(search_results, indent=2))

# # Optionally, save the results to a file
# with open('search_results.json', 'w') as f:
#     json.dump(search_results, f, indent=2)

# if __name__ == '__main__':
#     app.run(debug=False, port=5000)


from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import logging
import os
import json
from database_processing.faiss_processing import MyFaiss

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

# Get the absolute path of the current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize MyFaiss with absolute paths
cosine_faiss = MyFaiss(
    bin_clip_file=None,
    bin_clipv2_file=os.path.join(BASE_DIR, 'database_processing', 'faiss_clipv2_cosine.bin'),
    json_path=os.path.join(BASE_DIR, 'keyframe_information', 'annotation', 'L00.json'),
    audio_json_path=None,
    img2audio_json_path=None
)

app = Flask(__name__)
CORS(app, resources={r"/search": {"origins": "http://localhost:3000"}})

@app.route('/search', methods=['POST'])
def perform_search(query_text):
    scores, _, infos_query, image_paths = cosine_faiss.text_search(query_text, None, 3, 'clip_v2')
    
    # Create a dictionary to store the results
    search_results = {
        'success': True,
        'results': []
    }
    
    # Format and store the results
    for score, path in zip(scores, image_paths):
        search_results['results'].append({
            'score': float(score),
            'path': path,
            'timestamp': '00:00:00'
        })
    
    return jsonify(search_results)

if __name__ == '__main__':
    # while True:
    #     # Get user input
    #     user_query = input("Enter your search query (or 'quit' to exit): ")
        
    #     # Check if user wants to quit
    #     if user_query.lower() == 'quit':
    #         print("Exiting search program...")
    #         break
            
    #     # Perform the search with user's query
    #     results = perform_search(user_query)
        
    #     # Print the results
    #     print("\nSearch Results:")
    #     print(json.dumps(results, indent=2))
        
    #     # Save the results to a file
    #     with open('search_results.json', 'w') as f:
    #         json.dump(results, f, indent=2)
    #     print("\nResults have been saved to 'search_results.json'\n")
    app.run(debug=True)