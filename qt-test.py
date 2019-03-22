import sys
import argparse
import pandas as pd
import numpy as np
import h5py

from PIL import Image

from PySide2 import QtGui, QtCore
from PySide2.QtCore import Qt, Slot, QRect
from PySide2.QtGui import QPixmap, QImage
from PySide2.QtWidgets import (QAction, QApplication, QPushButton, QVBoxLayout,
                               QMainWindow, QSizePolicy, QWidget, QLabel)


def fmaxmult(*a):
    r = a[0]
    for i in range(1,len(a)):
        r = np.fmax(r,a[i])
    return r




class ms_ImageViewer(QWidget):

    def __init__(self,filename):
        super(ms_ImageViewer, self).__init__()
        
        self.filename = filename
        self.goTo = 0
        self.showOverlay = True
        self.colors0 = [
                        (236,57,100),
                        (71,38,67),
                        (38,107,160),
                        (38,91,55),
                        (238,208,87),
                        (223,78,54)
                    ]

        self.colors = [
                        (248,240,124),
                        (248,48,60),
                        (168,56,44),
                        (242,50,138),
                        (30,82,182),
                        (4,150,100)
                    ]

        self.colors2 = [
                        (255,0,0),
                        (0,255,0),
                        (0,0,255),
                        (128,128,0),
                        (128,0,128),
                        (0,128,128)
                    ]
        
        self.loadData()
        self.initUI()
        self.updateUI()

    def prevFrame(self):
        if self.frameIdx > 0:
            self.frameIdx -= 1
            self.updateUI()
    
    def nextFrame(self):
        if self.frameIdx < self.frameMax:
            self.frameIdx += 1
            self.updateUI()

    def keyPressEvent(self, e):
        # left arrow
        if e.key() == 16777234:
            self.prevFrame()
        # right arrow
        elif e.key() == 16777236:
            self.nextFrame()
        # up arrow
        elif e.key() == 16777235:
            self.frameIdx = 0
            self.updateUI()
        # down arrow
        elif e.key() == 16777237:
            self.frameIdx = self.frameMax
            self.updateUI()
        # tab key
        elif e.key() == 16777217:
            self.showOverlay = not self.showOverlay
            self.updateUI()
        # enter key
        elif e.key() == 16777220:
            if self.goTo >= 0 and self.goTo <= self.frameMax:
                self.frameIdx = self.goTo
                self.updateUI()
            self.goTo = 0
        # number keys
        elif e.key() < 128 and chr(e.key()).isnumeric():
            self.goTo = 10 * self.goTo + int(chr(e.key()))
        else:
            pass
            #print(e.key())
        

    def updateUI(self):
        self.image_label.setPixmap(self.getFramePixmap(self.frameIdx))
        self.setWindowTitle("%s... [%d/%d]"%
            (self.filename[:20],self.frameIdx,self.frameMax)
            )

    def loadData(self):
        self.file = h5py.File(self.filename, "r")
        self.imgH, self.imgW = self.file["box"][0][0].shape
        self.frameIdx = 0
        self.frameMax = self.file["box"].shape[0]-1
        
    def getFramePixmap(self,i):
        image = QtGui.QImage(
                        self.getFrame(i),
                        self.imgH, self.imgW,
                        QtGui.QImage.Format_ARGB32
                        )
        
        return QtGui.QPixmap.fromImage(image)
        
    def getFrame(self,i):
        #i = 47

        test_frame_over = self.file["confmaps"][i]
        test_frame_raw = self.file["box"][i][0]

        under_arr = np.dstack((
                    (test_frame_raw).astype(np.uint8),
                    (test_frame_raw).astype(np.uint8),
                    (test_frame_raw).astype(np.uint8)
                    ))
        img = Image.fromarray(under_arr)
        img.putalpha(255)
        
        if self.showOverlay:
            for channel in range(min(test_frame_over.shape[0],len(self.colors))):
                alpha = (test_frame_over[channel] * 255).astype(np.uint8)
                r = (test_frame_over[channel] * self.colors[channel][0]).astype(np.uint8)
                g = (test_frame_over[channel] * self.colors[channel][1]).astype(np.uint8)
                b = (test_frame_over[channel] * self.colors[channel][2]).astype(np.uint8)
            
                over_arr = np.dstack((b,g,r,alpha))
        
                over = Image.fromarray(over_arr)
                img = Image.alpha_composite(img, over)
        
        img_arr = np.array(img)
        
        return img_arr
    
    def initUI(self):               

        self.main_layout = QVBoxLayout()

        self.image_label = QLabel(" ")
        self.main_layout.addWidget(self.image_label)        
        prevButton = QPushButton('previous', self)
        prevButton.clicked.connect(self.prevFrame)
        self.main_layout.addWidget(prevButton)
        nextButton = QPushButton('next', self)
        nextButton.clicked.connect(self.nextFrame)
        self.main_layout.addWidget(nextButton)
        self.setLayout(self.main_layout)
        
        self.setGeometry(300, 300, 290, 300)
        self.show()
        


if __name__ == "__main__":

    # Qt Application
    app = QApplication(sys.argv)

    ex = ms_ImageViewer("training.scale=0.25,sigma=10.h5")

    sys.exit(app.exec_())