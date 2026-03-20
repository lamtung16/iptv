import os
from PIL import Image

# Folder containing PNG files (change if needed)
folder_path = "logos"

for filename in os.listdir(folder_path):
    if filename.lower().endswith(".png"):
        file_path = os.path.join(folder_path, filename)
        
        with Image.open(file_path) as img:
            width, height = img.size
            
            # Determine scaling factor so smaller side becomes 50 px
            if width < height:
                scale = 50 / width
            else:
                scale = 50 / height
            
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Overwrite original image
            resized_img.save(file_path)