from datetime import datetime
from extracters.image_colors import image_colors
from extracters.image_exif import image_exif
from extracters.image_objects import image_objects
from utils.dd import dd

def human_time(dt):
    hour = dt.hour

    if 0 <= hour < 3:
        return "late night"
    elif 3 <= hour < 5:
        return "midnight"
    elif 5 <= hour < 8:
        return "early morning"
    elif 8 <= hour < 12:
        return "morning"
    elif 12 <= hour < 14:
        return "noon"
    elif 14 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 20:
        return "evening"
    elif 20 <= hour < 23:
        return "night"
    else:
        return "late night"
    
def human_date(dt):
    return dt.strftime("%A %B %Y")

def image_nlp(image_path):
    exif = image_exif(image_path)
    objects = image_objects(image_path)
    colors = image_colors(image_path)
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