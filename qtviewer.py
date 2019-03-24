import sys

from imagefile import ImageFile

from PySide2 import QtGui, QtCore
from PySide2.QtCore import Qt, Slot, QRect
from PySide2.QtGui import QPixmap, QImage
from PySide2.QtWidgets import (QAction, QApplication, QPushButton, QVBoxLayout, 
                               QGraphicsView, QGraphicsScene, QGraphicsPixmapItem)

class ms_ImageViewer(QGraphicsView):

    def __init__(self,filename):
        super(ms_ImageViewer, self).__init__()
        
        self.filename = filename
        self.goTo = 0
        self.frameIdx = 0
        self.doZoom = False
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
        # ascii characters
        elif e.key() < 128:
            # number keys: store digits to build number of goto frame
            if chr(e.key()).isnumeric():
                self.goTo = 10 * self.goTo + int(chr(e.key()))
            # z toggles zoom
            elif chr(e.key()) == 'Z':
                self.doZoom = not self.doZoom
                self.updateUI()
        else:
            #print("key:",e.key())
            pass
    
    def updateUI(self):
        self.pixmap.setPixmap(self.getFramePixmap(self.frameIdx))
        outlineBox = self.imageFile.box(self.imageFile.findCenterOfMass(self.frameIdx))
        if self.boxRect: self.boxRect.setRect(*outlineBox)
        #self.translate(-outlineBox[0],-outlineBox[1])
        if self.doZoom:
            self.resetTransform()
            self.scale(2,2)
            self.centerOn(*self.imageFile.findCenterOfMass(self.frameIdx))
        else:
            self.resetTransform()
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

        self.scene = QGraphicsScene(self.main_layout)
        self.pixmap = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap)
        
        self.boxRect = None
        # option to draw box around overlay spots
        if False:
            outlineBox = self.imageFile.box(
                self.imageFile.findCenterOfMass(self.frameIdx)
                )
            self.scene.addRect(QRect(*outlineBox),pen=QtGui.QPen(QtCore.Qt.blue, 1))
            self.boxRect = self.scene.items()[0] # not the best way to get rect
        
        self.setScene(self.scene)
        
#         prevButton = QPushButton('previous', self)
#         prevButton.clicked.connect(self.prevFrame)
#         self.main_layout.addWidget(prevButton)
#         nextButton = QPushButton('next', self)
#         nextButton.clicked.connect(self.nextFrame)
#         self.main_layout.addWidget(nextButton)
#         self.setLayout(self.main_layout)
        
        self.setGeometry(300, 300, self.imageFile.imgH, self.imageFile.imgW)

        self.show()
    
    
if __name__ == "__main__":

    # Qt Application
    app = QApplication(sys.argv)

    ex = ms_ImageViewer("training.scale=0.25,sigma=10.h5")

    sys.exit(app.exec_())