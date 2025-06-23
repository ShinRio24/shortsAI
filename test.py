from PIL import Image
import os

file_path = 'media/img-0.png'
if os.path.exists(file_path):
    try:
        with Image.open(file_path) as img:
            img.show()
    except Exception as e:
        print(f"Error: {e}")
else:
    print("File does not exist")
