import os
from circle_detection import circleCounter

# Change PHOTO_PATH to the folder with all the pictures you'd like to analyze
# Change SAVE_COUNT_PATH to the folder where you'd like to save all your circle count pictures
PHOTO_PATH = r"PATH\TO\YOUR\PHOTOS"
SAVE_COUNT_PATH = r"PATH\TO\SAVE\COUNTS"

my_circle_destroyer = circleCounter()

####################

if not os.path.exists(SAVE_COUNT_PATH):
    os.mkdir(SAVE_COUNT_PATH)

for item in os.listdir(PHOTO_PATH):
    num_circles = my_circle_destroyer.circle_count(os.path.join(PHOTO_PATH, item), SAVE_COUNT_PATH)
    print(item + ": " + str(num_circles))
   