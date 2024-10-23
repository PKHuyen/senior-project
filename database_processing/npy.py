import numpy as np
import os


def read_npy_info(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return

    # Check if the file has a .npy extension
    if not file_path.endswith('.npy'):
        print(f"Error: The file '{file_path}' is not a .npy file.")
        return

    try:
        # Load the .npy file
        data = np.load(file_path, allow_pickle=True)

        # Get information about the array
        print(f"File: {file_path}")
        print(f"Data type: {data.dtype}")
        print(f"Shape: {data.shape}")
        print(f"Dimensions: {data.ndim}")
        print(f"Size: {data.size}")
        print(f"Total bytes: {data.nbytes}")

        # Print the first few elements (if it's a flat array)
        if data.ndim == 1:
            print("\nFirst few elements:")
            print(data[:min(5, len(data))])
        else:
            print("\nNote: This is a multi-dimensional array. Showing the first few elements may not be representative.")

    except Exception as e:
        print(f"An error occurred while reading the file: {str(e)}")


# Usage example
if __name__ == "__main__":
    file_path = input("Enter the path to your .npy file: ")
    read_npy_info(file_path)