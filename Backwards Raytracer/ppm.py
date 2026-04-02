# ppm.py
import numpy as np

def write_ppm(file_path, image_data):
    """
    Writes a 2D array of RGB pixels to a PPM (P3) file.
    
    Parameters:
    - file_path: String representing the output file name (e.g., 'output.ppm')
    - image_data: A 3D NumPy array or list of lists of shape (height, width, 3)
                  containing RGB values in the range [0, 255].
    """
    height = len(image_data)
    width = len(image_data[0])
    max_color = 255

    with open(file_path, 'w') as f:
        # 1. Write the PPM Header
        # P3 means ASCII RGB, followed by width, height, and max color value
        f.write(f"P3\n{width} {height}\n{max_color}\n")
        
        # 2. Write the pixel data
        # PPM writes from top-to-bottom, left-to-right
        for row in image_data:
            for pixel in row:
                # Ensure values are clamped to 0-255 and cast to integers
                r = max(0, min(max_color, int(pixel[0])))
                g = max(0, min(max_color, int(pixel[1])))
                b = max(0, min(max_color, int(pixel[2])))
                f.write(f"{r} {g} {b} ")
            f.write("\n")