from singleton_decorator import singleton
from datetime import datetime
from libs.ImageExif import ImageExif
from libs.ImageObjects import ImageObjects
from libs.util import human_date, human_time
from PIL import Image
from collections import Counter
from colorthief import ColorThief
import webcolors
import io

@singleton
class ImageParser:
    def __init__(self, exif_parser=ImageExif(), object_parser=ImageObjects()):
        self.exif_parser = exif_parser
        self.image_objects = object_parser
    
    
    def resize_to_buffer(self, image_path: str, size=(100, 100)):
        with Image.open(image_path) as img:
            img = img.resize(size)
            img_format = img.format if img.format else "JPEG"
            # Save the resized image into a bytes buffer
            buffer = io.BytesIO()
            img.save(buffer, format=img_format)  # Or "PNG" depending on your image
            buffer.seek(0)
            return buffer
    
    def remove_dupe_colors(self,response):
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
    
    def colors(self, file_path: str, top_n=5) -> dict:
        image_buffer = self.resize_to_buffer(file_path)
        color_thief = ColorThief(image_buffer)
        dominant = color_thief.get_color(quality=1)
        other_colors = color_thief.get_palette(color_count=top_n, quality=1)
        transform_rgb = lambda rgb: {"rgb":rgb, "name": self.closest_color_name(rgb) }
        response = self.remove_dupe_colors({
            "dominant": transform_rgb(dominant),
            "other": list(map(transform_rgb, other_colors))
        })
        
        return response

    def closest_color_name(self, requested_rgb):
        min_colors = {}
        names = webcolors.names(spec=webcolors.CSS21)
    
        for name in names:
            r_c, g_c, b_c = webcolors.name_to_rgb(name)
            rd = (r_c - requested_rgb[0]) ** 2
            gd = (g_c - requested_rgb[1]) ** 2
            bd = (b_c - requested_rgb[2]) ** 2
            min_colors[(rd + gd + bd)] = name
        return min_colors[min(min_colors.keys())]

    def parse(self, file_path:str) -> str:
        exif = self.exif_parser.parse(file_path)
        objects = self.image_objects.parse(file_path)
        colors = self.colors(file_path)
        text_version = ["Its an image type file"]
        if exif is not None:
            if "city" in exif and exif['city'] is not None:
                text_version.append(f"Image was taken at location near to {exif['city']['name']}, {exif['city']['label']}")
            if "date_taken" in exif and exif['date_taken'] is not None:
                dt = datetime.strptime(exif['date_taken'], "%Y:%m:%d %H:%M:%S")
                text_version.append(f"Image was taken at {human_time(dt)} on {human_date(dt)}")
            
        if len(objects) > 0:
            text_version.append("Some of visible objects in the image are "+", ".join(objects))
        if "dominant" in colors:
            text_version.append(f"Most dominant color in image is {colors['dominant']['name']}")
    
        if len(colors['other']) > 0:
            other_colors = ", ".join(list(map(lambda x: x["name"], colors['other'])))
            
            text_version.append(f"Some other visible colors in image are {other_colors}")


        return (". ".join(text_version))

