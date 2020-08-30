# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!
import sys
from PyQt5 import QtCore, QtGui, QtWidgets

global currFilterIndex

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(525, 386)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.image_label = QtWidgets.QLabel(Form)
        self.image_label.setObjectName("image_label")
        self.verticalLayout.addWidget(self.image_label)


        # label for emotion recognition
        self.emotion_label = QtWidgets.QLabel(Form)
        self.emotion_label.setObjectName("emotion_label")
        self.verticalLayout.addWidget(self.emotion_label)

        # button 
        self.control_bt = QtWidgets.QPushButton(Form)
        self.control_bt.setObjectName("control_bt")
        self.verticalLayout.addWidget(self.control_bt)


        self.horizontalLayout.addLayout(self.verticalLayout)
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)


        
        filter_options = ["Flowers", "Sunglasses", "Cat Ears", "Flower Crown",
        "Rainbow Vomit", "Necklace", "Clown nose and wig"]
        self.cb = QtWidgets.QComboBox()
        self.cb.addItems(filter_options)
        self.cb.currentIndexChanged.connect(self.selectionchange)
            
        self.verticalLayout.addWidget(self.cb)

        currFilterIndex = 0

    # function for keeping track of the selections made
    def selectionchange(self,i): # modify this later for when we want to do something w filters
      global currFilterIndex
      # loop through all the options 
      # print ("Items in the list are :")
      #for count in range(self.cb.count()):
      #   print (self.cb.itemText(count))
      # print ("Current index",i,"selection changed",self.cb.currentText())
      currFilterIndex = i
        

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Starting Sun's Out Photobooth", "☀ Sun's Out Photobooth ☀"))
        self.image_label.setText(_translate("Form", "Welcome to our photobooth! Choose your filter:"))
        self.control_bt.setText(_translate("Form", "Start"))
        self.emotion_label.setText(_translate("Form", "This photobooth detects your emotions!"))
        
