from image_exif import image_exif
from image_objects import image_objects
from image_colors import image_colors
from utils.dd import dd
from dotenv import load_dotenv

load_dotenv()

# data = image_exif("/workspaces/DataSearch/docs/location-image.jpg")
# dd(data)

objects = image_objects("/workspaces/DataSearch/docs/location-image.jpg")
dd(objects)

# image_objects("/workspaces/DataSearch/docs/balloons.jpg")
# image_objects("/workspaces/DataSearch/docs/people.jpg")
# image_objects("/workspaces/DataSearch/docs/car-person.jpg")
# cat_color = image_colors("/workspaces/DataSearch/docs/balloons.jpg")
# print(cat_color)
# car_person = image_colors("/workspaces/DataSearch/docs/car-person.jpg")
# print(car_person)
# jug = image_colors("/workspaces/DataSearch/docs/location-image.jpg")
# print(jug)
# people = image_colors("/workspaces/DataSearch/docs/people.jpg")
# print(people)



# image_color("/workspaces/DataSearch/docs/balloons.jpg")
# image_color("/workspaces/DataSearch/docs/people.jpg")
# image_color("/workspaces/DataSearch/docs/car-person.jpg")

    