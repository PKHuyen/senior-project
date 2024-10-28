def read_bin_file(file_path, num_bytes=64):
    """
    Reads the content of a .bin file and displays it in hexadecimal format.

    Parameters:
    - file_path (str): The path to the .bin file.
    - num_bytes (int): Number of bytes to read from the file (default is 64).

    Returns:
    - hex_content (str): A string representation of the file content in hexadecimal format.
    """
    try:
        with open(file_path, "rb") as file:
            content = file.read(num_bytes)
            hex_content = content.hex()
            print(f"Hexadecimal content of the first {num_bytes} bytes:")
            print(hex_content)
            return hex_content
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
file_path = "/Users/huyenphung/Desktop/senior-project/database_processing/faiss_clipv2_cosine.bin"
read_bin_file(file_path)
