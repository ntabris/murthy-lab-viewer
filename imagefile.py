import numpy as np
import h5py

from PIL import Image

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
        
    def findCenterOfMass(self, arr, a=0, b=-1):
        if type(arr) is int:
            over_flat = self.file["confmaps"][arr].sum(axis=0)
            return self.findCenterOfMass(over_flat,0,-1)
    
        # if given two dimensional array, flatten and calculate along each axis
        if len(arr.shape) == 2:
            return (
                self.findCenterOfMass(arr.sum(axis=0), a, b), # x: left
                self.findCenterOfMass(arr.sum(axis=1), a, b)  # y: down
                )
    
        if b == -1:
            b = len(arr) - 1
        
        cut = (a + b)//2
        left = arr[:cut].sum().astype(np.float64)
        right = arr[cut:].sum().astype(np.float64)
        
        if (b - a) < 4:
            return cut
        elif left < right:
            return self.findCenterOfMass(arr, cut, b)
        else:
            return self.findCenterOfMass(arr, a, cut)
        
if __name__ == "__main__":
    im = ImageFile("training.scale=0.25,sigma=10.h5")
    
    print(im.findCenterOfMass(0))