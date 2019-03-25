import sys

from imagefile import ImageFile

from PySide2 import QtGui, QtCore
from PySide2.QtCore import Qt, Slot, QRect
from PySide2.QtGui import QPixmap, QImage
from PySide2.QtWidgets import (QAction, QApplication, QPushButton, QHBoxLayout,
                               QMainWindow, QDockWidget, QWidget,
                               QGraphicsView, QGraphicsScene, QGraphicsPixmapItem)

class MyGraphicsView(QGraphicsView):
    
    def __init__(self, parent):
        super(MyGraphicsView, self).__init__()
        self.parent = parent
        
    def keyPressEvent(self, e):
        # left arrow goes to previous frame
        if e.key() == 16777234:
            self.parent.prevFrame()
        # right arrow goes to next frame
        elif e.key() == 16777236:
            self.parent.nextFrame()
        # up arrow goes to first frame
        elif e.key() == 16777235:
            self.parent.firstFrame()
        # down arrow goes to last frame
        elif e.key() == 16777237:
            self.parent.lastFrame()
        # pass event to parent
        else:
            self.parent.keyPressEvent(e)

class MyImageViewer(QMainWindow):

    def __init__(self,filename):
        super(MyImageViewer, self).__init__()
        
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
    
    def firstFrame(self):
        self.frameIdx = 0
        self.updateUI()

    def lastFrame(self):
        self.frameIdx = self.imageFile.frameMax
        self.updateUI()
    
    def toggleZoom(self):
        self.doZoom = not self.doZoom
        self.updateUI()
    
    def toggleOverlay(self):
        self.showOverlay = not self.showOverlay
        # don't recenter since we're not changing the frame
        self.updateUI(updateCenter=False)
    
    def keyPressEvent(self, e):
        # tab key toggles overlay
        if e.key() == 16777217:
            self.toggleOverlay()
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
                self.toggleZoom()
            else:
                #print("key:",e.key())
                pass
    
    def updateUI(self, updateCenter=True):
        self.pixmap.setPixmap(self.getFramePixmap(self.frameIdx))
        outlineBox = self.imageFile.box(self.imageFile.findCenterOfMass(self.frameIdx))
        if self.boxRect: self.boxRect.setRect(*outlineBox)
        #self.translate(-outlineBox[0],-outlineBox[1])
        if self.doZoom:
            self.view.resetTransform()
            self.view.scale(2,2)
            if updateCenter:
                self.view.centerOn(*self.imageFile.findCenterOfMass(self.frameIdx))
        else:
            self.view.resetTransform()
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
        self.scene = QGraphicsScene()
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
        
        self.view = MyGraphicsView(self)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.view.setFixedSize(256,256) # ???
        #self.view.setGeometry(20, 20, self.imageFile.imgW, self.imageFile.imgH)
        self.view.setScene(self.scene)
        
        self.setCentralWidget(self.view)
        
        controlDock = QDockWidget()
        controlDock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.TopDockWidgetArea, controlDock)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        # first frame
        firstButton = QPushButton('<<', self)
        firstButton.clicked.connect(self.firstFrame)
        main_layout.addWidget(firstButton)
        # previous frame
        prevButton = QPushButton('<', self)
        prevButton.clicked.connect(self.prevFrame)
        main_layout.addWidget(prevButton)
        # next frame
        nextButton = QPushButton('>', self)
        nextButton.clicked.connect(self.nextFrame)
        main_layout.addWidget(nextButton)
        # last frame
        lastButton = QPushButton('>>', self)
        lastButton.clicked.connect(self.lastFrame)
        main_layout.addWidget(lastButton)
        # zoom
        zoomButton = QPushButton('zoom', self)
        zoomButton.clicked.connect(self.toggleZoom)
        main_layout.addWidget(zoomButton)
        # zoom
        overlayButton = QPushButton('color', self)
        overlayButton.clicked.connect(self.toggleOverlay)
        main_layout.addWidget(overlayButton)
        # add dock widget
        dockContainerWidget = QWidget(controlDock)
        dockContainerWidget.setLayout(main_layout)
        dockContainerWidget.setGeometry(0,0,self.imageFile.imgW,20)
        
        self.setFixedSize(self.imageFile.imgW, self.imageFile.imgH+dockContainerWidget.height())
        #self.setGeometry(320, 320, self.imageFile.imgW, self.imageFile.imgH+dockContainerWidget.height())

        self.show()
    
    
if __name__ == "__main__":
    # Qt Application
    app = QApplication(sys.argv)
    
    # take filename from command-line argument, or use default if none passed in
    filename = "training.scale=0.25,sigma=10.h5"
    if len(sys.argv) > 1:
        filename = sys.argv[-1]
    # show image viewer
    ex = MyImageViewer(filename)

    sys.exit(app.exec_())