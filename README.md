# Python-Rapid-Circle-Detection
## Overview
Get info on colour-contrasted circular objects in an image within seconds, using OpenCV library. The original application was with optical fiber bundles, so the algorithm is tuned to detect and count circles with a totally dark background and lighter circles.

The algorithm is inspired by this StackOverflow post: https://stackoverflow.com/questions/26932891/detect-touching-overlapping-circles-ellipses-with-opencv-and-python. 

I have added several different masks and filters to remove circles that are too dark or out of bounds, remove small artifacts, as well as improve the general image processing.

The algorithm completes a circle counting job much faster than the Hough Gradient method, **especially with large circle counts**, as running an accumulator along all the detected edges in an image takes time.

Can handle touching circles reasonably well.

Assumes circles are all roughly the same size.

## Setting Up
You'll just need to clone this repo and get the necessary libraries.

Clone this repository with Git:
```
git clone https://github.com/Eric-Ptn/Python-Rapid-Circle-Detection.git
```

Make a virtual environment, activate it, then run
```
pip install -r requirements.txt
```

Now use either of `analyze_photos.py` or `camera_and_analyze_photo.py` to your liking :) 

(with the venv activated if you created one)

## Usage
coming soon