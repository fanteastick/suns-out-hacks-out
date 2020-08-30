# -*- coding: utf-8 -*-
"""
Created on Sat Aug 29 12:03:50 2020
@author: ellie
"""
# import system module
import sys

# import some PyQt5 modules
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

# importing os module for saving 
import os
import time

# import Opencv module
import cv2

# importing UI
from ui_main_window import *

# importing all the ML face stuff
import filter_pos # has the stuff from face_filter
import emotions 


global widthPercent
global lengthPercent
global origLength 
global origWidth

origWidth =  662
origLength = 557

class MainWindow(QWidget):
    # class constructor
    def __init__(self, *args, **kwargs):
        # call QWidget constructor
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # create a timer
        self.timer = QTimer()
        # set timer timeout callback function
        self.timer.timeout.connect(self.viewCam)
        # set control_bt callback clicked  function
        self.ui.control_bt.clicked.connect(self.controlTimer)
        self.filterPos = filter_pos.faceFilter()
        # self.qImg = None
        self.ui.cb.currentIndexChanged.connect(self.updateFilter)

    def updateFilter(self):
        # saving the image w/ timestamp
        homedir = os.path.expanduser("~")
        savepath = homedir + "\Pictures\photobooth" + str(int(time.time())) + ".jpg"
        self.qImg.save(savepath)

        # write image, add filter, write it again
        image = cv2.imread(savepath)
        image, top_emotions = self.filterPos.addFilter(image, self.ui.cb.currentIndex(), self.ui.emotion_chkbox.isChecked())
        cv2.imwrite(savepath, image)

        #showing the filtered image?!?!
        newPixmap = QPixmap(savepath)
        self.ui.image_label.setPixmap(newPixmap)
        if self.ui.emotion_chkbox.isChecked():
            self.ui.emotion_label.setText("The emotions in this photo include: " + ", ".join(top_emotions))
        else:
            self.ui.emotion_label.clear()


    # view camera
    def viewCam(self):
        # read image in BGR format
        ret, image = self.cap.read()
        # convert image to RGB format
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = self.rescale_frame(image)

        # grab image attributes before adding filter
        height, width, channel = image.shape
        imagedata = image.data # because of issues w/ opencv and PIL
        
        # get image infos
        step = channel * width
        # create QImage from image
        self.qImg = QImage(imagedata, width, height, step, QImage.Format_RGB888)
        # show image in img_label
        self.ui.image_label.setPixmap(QPixmap.fromImage(self.qImg))

    # start/stop timer
    def controlTimer(self):
        # if timer is stopped
        if not self.timer.isActive():
            # create video capture
            self.cap = cv2.VideoCapture(0)
            # start timer
            self.timer.start(20)
            # update control_bt text
            self.ui.control_bt.setText("☀ Take Photo ☀")
            self.ui.emotion_label.setText("This photobooth detects your emotions!")
        # if timer is started
        else:
            # stop timer
            self.timer.stop()
            # release video capture
            self.cap.release()

            # update the filter
            self.updateFilter()


            # update control_bt text
            self.ui.control_bt.setText("▶ Start camera ▶")
            

            

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)
        length = event.size().height()

        oldWidth = event.oldSize().width()
        width = event.size().width()
        oldLength = event.oldSize().height()
        listOfGlobals = globals()
        if oldLength < 0 :
            oldLength = length
        else:
            oldLength = 566
        if oldWidth < 0 :
            oldWidth = width
        else:
            oldWidth = 662
        n = (width / oldWidth) * 100
        m = (length / oldLength) * 100
        listOfGlobals['widthPercent'] = n
        listOfGlobals['lengthPercent'] = m

        
    def rescale_frame(self, frame):
        scale_percent = min(widthPercent, lengthPercent)
        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        dim = (width, height)
        return cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

    

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # create and show mainWindow
    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())
