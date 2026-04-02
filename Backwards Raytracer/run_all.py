import subprocess
import glob
import sys
import os

def render_all_tests(target_directory="."):
    # Recursively find all .txt files starting with 'test' in the target directory AND any subfolders
    search_pattern = os.path.join(target_directory, '**', 'test*.txt')
    test_files = glob.glob(search_pattern, recursive=True)
    
    # Sort them alphabetically for a predictable rendering order
    test_files.sort()
    
    if not test_files:
        print(f"No test files found in '{target_directory}' or its subfolders.")
        return

    print(f"Found {len(test_files)} test files. Starting batch render...\n")

    # Make sure this matches the exact name of your main engine file!
    tracer_script = 'RayTracer2.py'

    for file_path in test_files:
        print(f"==================================================")
        print(f"Starting: {file_path}")
        print(f"==================================================")
        
        try:
            # sys.executable ensures it uses the exact same Python version running this script
            subprocess.run([sys.executable, tracer_script, file_path], check=True)
            print("\n")
            
        except subprocess.CalledProcessError as e:
            print(f">>> ERROR: Failed to render {file_path}.")
            print(f">>> {e}\n")
        except FileNotFoundError:
            print(f">>> ERROR: Could not find '{tracer_script}'. Make sure it is in the same directory as run_all.py.")
            break
            
    print("Batch rendering complete. Check the folder where your text files are for the output .ppm files!")

if __name__ == "__main__":
    # If you want to specify a specific folder from the command line, you can do: 
    # python run_all.py my_test_folder
    # Otherwise, it defaults to searching the current directory and all sub-directories.
    folder_to_search = sys.argv[1] if len(sys.argv) > 1 else "."
    render_all_tests(folder_to_search)