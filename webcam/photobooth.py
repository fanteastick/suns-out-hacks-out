# -*- coding: utf-8 -*-
"""
Created on Sat Aug 29 12:03:50 2020

@author: ellie
"""
# import system module
import sys

# import some PyQt5 modules
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import *


# import Opencv module
import cv2

from ui_main_window import *

global widthPercent
global lengthPercent
global origLength 
global origWidth

origWidth =  662
origLength = 531

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
        

    # view camera
    def viewCam(self):
        # read image in BGR format
        ret, image = self.cap.read()
        # convert image to RGB format
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = self.rescale_frame(image)
        # get image infos

        height, width, channel = image.shape
        step = channel * width
        # create QImage from image
        qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
        # show image in img_label
        self.ui.image_label.setPixmap(QPixmap.fromImage(qImg))

    # start/stop timer
    def controlTimer(self):
        # if timer is stopped
        if not self.timer.isActive():
            # create video capture
            self.cap = cv2.VideoCapture(0)
            # start timer
            self.timer.start(20)
            # update control_bt text
            self.ui.control_bt.setText("Stop")
        # if timer is started
        else:
            # stop timer
            self.timer.stop()
            # release video capture
            self.cap.release()
            # update control_bt text
            self.ui.control_bt.setText("Start")
    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)
        length = event.size().height()

        oldWidth = event.oldSize().width()
        width = event.size().width()
        oldLength = event.oldSize().height()
        listOfGlobals = globals()
        print ("length", length)
        print ("width", width)
        if oldLength < 0 :
            oldLength = length
        else:
            oldLength = 531
        if oldWidth < 0 :
            oldWidth = width
        else:
            oldWidth = 662
        n = (width / oldWidth) * 100
        m = (length / oldLength) * 100
        listOfGlobals['widthPercent'] = n
        listOfGlobals['lengthPercent'] = m
        print("widthPercent", widthPercent)
        print("lengthPercent", lengthPercent)

        
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
