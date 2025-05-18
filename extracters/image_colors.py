from PIL import Image
from collections import Counter
from colorthief import ColorThief
import webcolors
import io

def resize_to_buffer(image_path, size=(100,100)):
    with Image.open(image_path) as img:
        img = img.resize(size)
        img_format = img.format if img.format else "JPEG"
        # Save the resized image into a bytes buffer
        buffer = io.BytesIO()
        img.save(buffer, format=img_format)  # Or "PNG" depending on your image
        buffer.seek(0)
        return buffer

def closest_color_name(requested_rgb):
    min_colors = {}
    names = webcolors.names(spec=webcolors.CSS21)
  
    for name in names:
        r_c, g_c, b_c = webcolors.name_to_rgb(name)
        rd = (r_c - requested_rgb[0]) ** 2
        gd = (g_c - requested_rgb[1]) ** 2
        bd = (b_c - requested_rgb[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]

def remove_dupes(response):
    colors = [response['dominant']['name']]
    deduped_other = []
    for other_color in response['other']:
        if other_color['name'] in colors:
            continue
        colors.append(other_color['name'])
        deduped_other.append(other_color)
    return {
        "dominant": response['dominant'],
        "other": deduped_other
    }
    
def image_colors(image_path, top_n=5):
    image_buffer = resize_to_buffer(image_path)
    color_thief = ColorThief(image_buffer)
    dominant = color_thief.get_color(quality=1)
    other_colors = color_thief.get_palette(color_count=top_n, quality=1)
    transform_rgb = lambda rgb: {"rgb":rgb, "name": closest_color_name(rgb) }
    response = remove_dupes({
        "dominant": transform_rgb(dominant),
        "other": list(map(transform_rgb, other_colors))
    })
    
    return response