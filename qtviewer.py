import sys
import numpy as np
import h5py

from PIL import Image

from PySide2 import QtGui, QtCore
from PySide2.QtCore import Qt, Slot, QRect
from PySide2.QtGui import QPixmap, QImage
from PySide2.QtWidgets import (QAction, QApplication, QPushButton, QVBoxLayout, 
                               QMainWindow, QSizePolicy, QWidget, QLabel, QGraphicsView,
                               QGraphicsScene)


class ImageFile():
    def __init__(self,filename):
        self.doCaching = False # caching images doesn't seem to improve speed
        self.filename = filename
        self.loadData()

        self.colors = [
                        (248,240,124),
                        (248,48,60),
                        (168,56,44),
                        (242,50,138),
                        (30,82,182),
                        (4,150,100)
                    ]

    def loadData(self):
        self.file = h5py.File(self.filename, "r")
        self.imgH, self.imgW = self.file["box"][0][0].shape
        self.frameMax = self.file["box"].shape[0]-1
        self.clearCache()
        
    def clearCache(self):
        self.frameCache = [None] * (self.frameMax+1)

    def getFrame(self,i,showOverlay = True):
        if i < 0 or i > self.frameMax:
            return None
        # if caching is turned off, just return frame
        if not self.doCaching:
            return self.getUncachedFrame(i,showOverlay)
        
        # otherwise, put frame into cache if it isn't
        if self.frameCache[i] is None:
            self.frameCache[i] = self.getUncachedFrame(i,showOverlay)
        # return cached frame
        return self.frameCache[i]
        
    def getUncachedFrame(self,i,showOverlay):
        test_frame_over = self.file["confmaps"][i]
        test_frame_raw = self.file["box"][i][0]

        under_arr = np.dstack((
                    (test_frame_raw).astype(np.uint8),
                    (test_frame_raw).astype(np.uint8),
                    (test_frame_raw).astype(np.uint8)
                    ))
        img = Image.fromarray(under_arr)
        img.putalpha(255)
        
        if showOverlay:
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

class ms_ImageViewer(QGraphicsView):

    def __init__(self,filename):
        super(ms_ImageViewer, self).__init__()
        
        self.filename = filename
        self.goTo = 0
        self.frameIdx = 0
        self.showOverlay = True
        
        self.imageFile = ImageFile(self.filename)
        self.initUI()
        self.updateUI()

    def prevFrame(self):
        if self.frameIdx > 0:
            self.frameIdx -= 1
            self.updateUI()
    
    def nextFrame(self):
        if self.frameIdx < self.imageFile.frameMax:
            self.frameIdx += 1
            self.updateUI()

    def keyPressEvent(self, e):
        # left arrow goes to previous frame
        if e.key() == 16777234:
            self.prevFrame()
        # right arrow goes to next frame
        elif e.key() == 16777236:
            self.nextFrame()
        # up arrow goes to first frame
        elif e.key() == 16777235:
            self.frameIdx = 0
            self.updateUI()
        # down arrow goes to last frame
        elif e.key() == 16777237:
            self.frameIdx = self.imageFile.frameMax
            self.updateUI()
        # tab key toggles overlay
        elif e.key() == 16777217:
            self.showOverlay = not self.showOverlay
            self.updateUI()
        # enter key goes to number entered
        elif e.key() == 16777220:
            if self.goTo >= 0 and self.goTo <= self.imageFile.frameMax:
                self.frameIdx = self.goTo
                self.updateUI()
            self.goTo = 0
        # number keys: store digits to build number of goto frame
        elif e.key() < 128 and chr(e.key()).isnumeric():
            self.goTo = 10 * self.goTo + int(chr(e.key()))
        else:
            print(e.key())
            pass
    
    def updateUI(self):        
        self.image_label.setPixmap(self.getFramePixmap(self.frameIdx))
        self.setWindowTitle("%s... [%d/%d]"%
            (self.filename[:20],self.frameIdx,self.imageFile.frameMax))
    
        
    def getFramePixmap(self,i):
        image = QtGui.QImage(
                        self.imageFile.getFrame(i,self.showOverlay),
                        self.imageFile.imgH, self.imageFile.imgW,
                        QtGui.QImage.Format_ARGB32
                        )
        return QtGui.QPixmap.fromImage(image)
        

    
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