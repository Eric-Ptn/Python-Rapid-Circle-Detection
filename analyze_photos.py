import os
from circle_detection import circleCounter

# Change PHOTO_PATH to the folder with all the pictures you'd like to analyze
# Change SAVE_COUNT_PATH to the folder where you'd like to save all your circle count pictures
PHOTO_PATH = r"absolute\path\Python-Rapid-Circle-Detection\assets"
SAVE_COUNT_PATH = r"absolute\path\Python-Rapid-Circle-Detection\assets\circle_counts"

my_circle_destroyer = circleCounter()

####################

if not os.path.exists(SAVE_COUNT_PATH):
    os.mkdir(SAVE_COUNT_PATH)

for item in os.listdir(PHOTO_PATH):
    item_path = os.path.join(PHOTO_PATH, item)
    if os.path.isdir(item_path):
        continue

    num_circles = my_circle_destroyer.circle_count(item_path, SAVE_COUNT_PATH)
    print(item + ": " + str(num_circles))
   