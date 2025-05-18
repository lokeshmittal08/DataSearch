from nlp.image_nlp import image_nlp
from utils.dd import dd
from dotenv import load_dotenv

load_dotenv()

# data = image_exif("/workspaces/DataSearch/docs/location-image.jpg")
# dd(data)

objects = image_nlp("/workspaces/DataSearch/docs/1747554694405.jpg")
dd(objects)