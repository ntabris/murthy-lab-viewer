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


def pil2pixmap(self,im):
    if im.mode == "RGB":
        pass
    elif im.mode == "L":
        im = im.convert("RGBA")
    data = im.convert("RGBA").tostring("raw", "RGBA")
    qim = QtGui.QImage(data, im.size[0], im.size[1], QtGui.QImage.Format_ARGB32)
    pixmap = QtGui.QPixmap.fromImage(qim)
    return pixmap

class ms_ImageViewer(QWidget):

    def __init__(self):
        super(ms_ImageViewer, self).__init__()
        self.initUI()

    def initUI(self):               

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.image = QImage(256, 256, QImage.Format_ARGB32)
        intial_color = QtGui.qRgb(189, 149, 39)
        self.image.fill(QtGui.qRgb(255,0,0))
        
        
        # self.image.load('/projects/test.png')
        image_label = QLabel(" ")
        
        
        f = h5py.File("training.scale=0.25,sigma=10.h5", "r")
        test_frame_raw = f["box"][13][0].astype(np.uint32)
        test_frame_over = f["confmaps"][13]
        
        a0 = (test_frame_over[0] * 255).astype(np.uint32)
        a1 = (test_frame_over[1] * 255).astype(np.uint32)
        a2 = (test_frame_over[2] * 255).astype(np.uint32)
        
        alpha = fmaxmult(
            test_frame_over[0]*255,
            test_frame_over[1]*255,
            test_frame_over[2]*255
            ).astype(np.uint32)

        under = (255 << 24 | test_frame_raw << 16 | test_frame_raw << 8 | test_frame_raw)
        over = (255 << alpha | a0 << 16 | a1 << 8 | a2)
        
        
        #b = (255 << 24 | over[0] << 16 | over[1] << 8 | over[2])
        #self.image = QtGui.QImage(b, 256, 256, QImage.Format_ARGB32)
        self.image = QtGui.QImage(b, 256, 256, QImage.Format_ARGB32)
        
        image_label.setPixmap(QtGui.QPixmap.fromImage(self.image))
        
        
        prevButton = QPushButton('previous', self)
        main_layout.addWidget(prevButton)
        nextButton = QPushButton('next', self)
        main_layout.addWidget(nextButton)
        
        
        main_layout.addWidget(image_label)

        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle('Frames')    
        self.show()

def fmaxmult(*a):
    r = a[0]
    for i in range(1,len(a)):
        r = np.fmax(r,a[i])
    return r


if __name__ == "__main__":

    # Qt Application
    app = QApplication(sys.argv)

    #window = MainWindow()
    #window.show()
    ex = ms_ImageViewer()

    sys.exit(app.exec_())