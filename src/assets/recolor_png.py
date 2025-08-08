# base color = #000000
from PIL import Image
from vessel_colors import status_colors
import os

# --- Settings ---
original_folder = "src/assets/based_vessels_png"
output_folder = "src/assets/colored_vessels_png"
based_color = "#000000"

def hex_to_rgba(hex_color, alpha=255):
    """Convert hex color string to RGBA tuple."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 6:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (r, g, b, alpha)
    elif len(hex_color) == 8:
        r, g, b, a = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4, 6))
        return (r, g, b, a)
    else:
        raise ValueError("Hex color must be in #RRGGBB or #RRGGBBAA format.")


for filename in os.listdir(original_folder):
    for status, hex_color in status_colors.items():
        
        # Convert hex to RGBA
        old_color = hex_to_rgba(based_color)
        new_color = hex_to_rgba(hex_color)

        # --- Load image ---
        img = Image.open(os.path.join(original_folder, filename)).convert("RGBA")
        pixels = img.load()

        # --- Replace color ---
        for y in range(img.height):
            for x in range(img.width):
                if pixels[x, y] == old_color:
                    pixels[x, y] = new_color
                    
        new_filename = filename.replace(".png", "") + '_' + status + '.png'

        # --- Save result ---
        output_path = os.path.join(output_folder, new_filename)
        img.save(output_path)
        print(f"Recolored: {new_filename}")

