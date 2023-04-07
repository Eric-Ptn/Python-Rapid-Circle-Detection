from tkinter import *
import cv2
import os
from circle_detection import circleCounter

# Change PHOTO_PATH to the folder where you'd like to save all your camera pictures
# Change SAVE_COUNT_PATH to the folder where you'd like to save all your circle count pictures
SAVE_PHOTO_PATH = r"PATH\TO\SAVE\PHOTOS"
SAVE_COUNT_PATH = r"PATH\TO\SAVE\COUNTS"

my_circle_destroyer = circleCounter()

########### GUI ############
root = Tk(className = "Photo Capturer")

def myCamera():
    ImageName = str(Input.get())

    cv2.namedWindow("Preview")
    vc = cv2.VideoCapture(0)

    if vc.isOpened():
        rval, frame = vc.read()
    else:
        rval = False
    while rval:
        cv2.imshow("Preview", frame)
        rval, frame = vc.read()

        key = cv2.waitKey(20)  

        # Space to take a photo
        if key == 32:
            os.chdir(SAVE_PHOTO_PATH)
            filename = ImageName + ".jpg"

            cv2.imwrite(filename, frame)
            print("Image '" + ImageName + "' Taken!")

            num_circles = my_circle_destroyer.circle_count(os.path.join(SAVE_PHOTO_PATH, filename), SAVE_COUNT_PATH)
            print("Number of circles: " + str(num_circles))

        # Esc to exit
        elif key == 27:
            break

    vc.release()
    cv2.destroyWindow("Preview")
   
    myButton = Button(text = "Exit program", padx = 25, pady = 10, fg = "white", bg = "red", relief = RAISED, borderwidth = 3,command = root.quit)
    myButton.place(x = 185, y = 120, anchor = NW)


Input = Entry(root, width = 100, font = 'ArialBold 16')
Input.insert(0, "Enter Image Name Here: ")
Input.place(x = 0, y = 0, anchor = NW)

myButton = Button(text = "Click to Open the Camera", padx = 50, pady = 10, fg = "white", bg = "grey", relief = RAISED, borderwidth = 4, command = myCamera)   
myButton.place(x = 125, y = 50, anchor = NW)

root.geometry("500x190")
root.mainloop()
