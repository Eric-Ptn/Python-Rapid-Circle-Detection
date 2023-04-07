import cv2
import numpy as np
import os
from io import BytesIO
import win32clipboard

## IF YOU WANT TO VISUALIZE THE IMAGE PROCESSING, JUST THROW IN SOME IMSHOWS AND WAITKEYS INTO circle_count - code might make more sense that way

#### GENERAL CONSTANTS THAT SHOULD WORK FOR MOST OF OUR PHOTOS ####

DARK_CIRCLE_THRESHOLD = 135                 # circles darker than this not counted, higher threshold fewer circles passed
NORMALIZED_DISTANCE_THRESHOLD = 0.3         # areas with a normalized distance transform less than this threshold are sent to zero (prevents close circles from blurring together)

ADAPTIVE_THRESHOLD_BOX = 51                 # how many neighbouring pixels included in calculation, MUST BE ODD
ADAPTIVE_THRESHOLD_BRIGHTEN = 45            # how much to offset results by
                                            # see https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html for more info (adaptive thresholding)

DEFAULT_CIRCLE_SIZE = 14                     # size of template circle used in matching
CIRCLE_GAP = 5                               # estimated gap between circles

# there are still plenty of magic numbers in the code, but those are less important and can be left alone

##################################

class circleCounter:

    # just a list of class variables will be declared later

    def __init__(self):
        self.SAVE_PATH = None
        self.IMAGE_PATH = None
        self.IMAGE_NAME = None

        self.CIRCLE_COUNT = None

        self.CIRCLED_IMAGE = None # image with circles labelled and circle count text overlay, sent to clipboard


    ############ IMAGE PROCESSING FUNCTIONS ############

    def sharpen_image(self, image):
        # uses an "unsharp" kernel, less noisy than a basic sharpen kernel

        sharp_kernel = np.array([[-0.00391, -0.01563, -0.02344, -0.01563, -0.00391],
                            [-0.01563, -0.06250, -0.09375, -0.06250, -0.01563],
                            [-0.02344, -0.09375, 1.85980, -0.09375, -0.02344],
                            [-0.01563, -0.06250, -0.09375, -0.06250, -0.01563],
                            [-0.00391, -0.01563, -0.02344, -0.01563, -0.00391]])

        image_sharp = cv2.filter2D(src=image, ddepth=-1, kernel=sharp_kernel)

        return image_sharp

    def filter_dark_circles(self, hsv):

        # convert to black and white
        # using hsv v channel is slightly better than using cv2 imread grayscale
        black_and_white = hsv[:, :, 2]

        _, bw_1 = cv2.threshold(black_and_white, DARK_CIRCLE_THRESHOLD, 255, cv2.THRESH_TOZERO)    # send spots darker than threshold to zero 
                                                                                                   # (otherwise still grayscale)

        _, bw_1_mask = cv2.threshold(black_and_white, DARK_CIRCLE_THRESHOLD, 255, cv2.THRESH_BINARY) # black and white based on threshold

        return bw_1, bw_1_mask

    def find_circle_edges(self, hsv_dark_filtered): 
        bw_2 = cv2.adaptiveThreshold(hsv_dark_filtered, 255, cv2.ADAPTIVE_THRESH_MEAN_C,\
                cv2.THRESH_BINARY, ADAPTIVE_THRESHOLD_BOX, ADAPTIVE_THRESHOLD_BRIGHTEN)
        return bw_2

    def erode(self, image_to_erode, magnitude):
        erode_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (magnitude, magnitude))
        eroded_image = cv2.erode(image_to_erode, erode_kernel)

        return eroded_image

    def distance_transform_and_match(self, im_final_erode): 
        circle_size = DEFAULT_CIRCLE_SIZE

        while circle_size != 0:
            ## makes template circle
            template_circle = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*(circle_size-CIRCLE_GAP)+1, 2*(circle_size-CIRCLE_GAP)+1))
            template_circle = cv2.copyMakeBorder(template_circle, CIRCLE_GAP, CIRCLE_GAP, CIRCLE_GAP, CIRCLE_GAP, 
                                        cv2.BORDER_CONSTANT | cv2.BORDER_ISOLATED, 0)
            dist_circle = cv2.distanceTransform(template_circle, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)

            ## prepares actual image
            dist_im = cv2.distanceTransform(im_final_erode, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
            distborder = cv2.copyMakeBorder(dist_im, circle_size, circle_size, circle_size, circle_size, 
                                    cv2.BORDER_CONSTANT | cv2.BORDER_ISOLATED, 0)

            cv2.imshow('Python Rapid Circle Detection - Circle Template', dist_circle)
            cv2.imshow('Python Rapid Circle Detection', distborder)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            circle_size = int(input('Change template circle size (initially ' + str(circle_size) + '), if correctly fitted, enter 0: '))

        ##  TEMPLATE MATCHING BETWEEN THE TWO DISTANCE TRANSFORMS
        match_dist = cv2.matchTemplate(distborder, dist_circle, cv2.TM_CCOEFF_NORMED)

        return dist_im, match_dist

    ############## COUNTING AFTER PROCESS

    def find_and_count_circles(self, clean_match_dist, dist_im):
        _, mx, _, _ = cv2.minMaxLoc(clean_match_dist)
        _, peaks = cv2.threshold(clean_match_dist, mx*0.5, 255, cv2.THRESH_BINARY)  # find peaks in clean_match_dist, locations of circles

        peaks8u = cv2.convertScaleAbs(peaks)                                        # needs to be converted to 8u format for findContours

        contours, _ = cv2.findContours(peaks8u, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

        self.CIRCLE_COUNT = len(contours)

        self.CIRCLED_IMAGE = self.IMAGE.copy()                                      # copy image to draw circles on, keep original for screenshot

        for i in range(self.CIRCLE_COUNT):
            x, y, w, h = cv2.boundingRect(contours[i])
            _, mx, _, mxloc = cv2.minMaxLoc(dist_im[y:y+h, x:x+w], peaks8u[y:y+h, x:x+w])

            center = (int(mxloc[0]+x), int(mxloc[1]+y))
            radius = int(mx)                               # the radius of the circle is 
                                                           # THE VALUE OF THE DISTANCE TRANFORM AT THE CENTER OF THE CIRCLE (crazy)

            cv2.circle(self.CIRCLED_IMAGE, center, radius, (255, 0, 0), 2)

        self.show_and_export_circle_count()

    def show_and_export_circle_count(self):
        # text on top of circles
        cv2.putText(self.CIRCLED_IMAGE, f"CIRCLES: {self.CIRCLE_COUNT}   FILENAME: {self.IMAGE_NAME}", (200,50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 4, cv2.LINE_AA)

        # copy to clipboard
        output = BytesIO()
        _, buffer = cv2.imencode(".bmp", self.CIRCLED_IMAGE)
        data = buffer.tobytes()[14:]
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        
        cv2.imshow('Python Rapid Circle Detection', self.CIRCLED_IMAGE)
        cv2.waitKey(0)

        os.chdir(self.SAVE_PATH)
        cv2.imwrite(self.IMAGE_NAME + " - count.png", self.CIRCLED_IMAGE)


    ############### MAIN FUNCTION YAY

    def circle_count(self, image_path, save_path):

        self.IMAGE = cv2.imread(image_path)
        self.IMAGE_PATH = image_path
        self.SAVE_PATH = save_path
        self.IMAGE_NAME = os.path.split(self.IMAGE_PATH)[1].split('.')[0] # get the file name

        sharp_im = self.sharpen_image(self.IMAGE)

        hsv = cv2.cvtColor(sharp_im, cv2.COLOR_BGR2HSV)

        hsv_dark_filtered, hsv_dark_filtered_mask = self.filter_dark_circles(hsv)
        hsv_edges = self.find_circle_edges(hsv_dark_filtered)                               # don't put the mask here, the mask is black and white

        im_final = cv2.bitwise_and(hsv_edges, hsv_dark_filtered_mask)                       # get the edges of all circles that are not dark

        im_final_erode = self.erode(im_final, 3)                                            # make the black edges a little thicker for when circles are close

        dist_im, match_dist = self.distance_transform_and_match(im_final_erode)             # the meat of the operation, perform the distance transform
                                                                                            # and compare to a template circle, normalized

        _, match_dist_filter1 = cv2.threshold(match_dist, 
                                NORMALIZED_DISTANCE_THRESHOLD, 1, cv2.THRESH_TOZERO)        # set low distances to black

        clean_match_dist = self.erode(match_dist_filter1, 7)                                # erode final result to get rid of small artifacts

        self.find_and_count_circles(clean_match_dist, dist_im)                               # does calculation and image saving

        return self.CIRCLE_COUNT
