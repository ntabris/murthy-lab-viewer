import numpy as np
import h5py
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as anim

f = None
gFrameIdx = 0
gMaxFrameIdx = 0

def fmaxmult(*a):
    r = a[0]
    for i in range(1,len(a)):
        r = np.fmax(r,a[i])
    return r

def drawFrame(i):
    print("plotting %d"%i)
    fig.clear()
    test_frame_over = f["confmaps"][i]
    test_frame_raw = f["box"][i][0]
    plt.imshow(test_frame_raw, cmap=plt.cm.gray)
    
    # first three channels
    alpha = fmaxmult(
        test_frame_over[0],
        test_frame_over[1],
        test_frame_over[2]
        )
    # alternate: alpha = np.full((256,256),.5)

    over = np.dstack((
        test_frame_over[0],
        test_frame_over[1],
        test_frame_over[2],
        alpha
        ))

    plt.imshow(over)
    
     # second three channels
    alpha = fmaxmult(
        test_frame_over[3],
        test_frame_over[4],
        test_frame_over[5]
        )
    # alternate: alpha = np.full((256,256),.5)

    over = np.dstack((
        test_frame_over[3],
        test_frame_over[4],
        test_frame_over[5],
        alpha
        ))

    plt.imshow(over)
    plt.title("Frame %d/%d"%(i+1,gMaxFrameIdx+1))
    plt.plot()
    fig.canvas.draw_idle()

def flipFrame(inc):
    global gFrameIdx,gMaxFrameIdx
    gFrameIdx += inc
    if gFrameIdx < 0:
        gFrameIdx = 0
    elif gFrameIdx > gMaxFrameIdx:
        gFrameIdx = gMaxFrameIdx
    drawFrame(gFrameIdx)

def on_key(event):
    if event.key == 'right':
        flipFrame(1)
    elif event.key == 'left':
        flipFrame(-1)
    elif event.key == ' ':
        flipFrame(20)
    elif event.key == 'backspace':
        flipFrame(-20)
    else:
        print(event.key)
    
if __name__ == "__main__":

    f = h5py.File("training.scale=0.25,sigma=10.h5", "r")

    gMaxFrameIdx = f["box"].shape[0]-1

    matplotlib.use('Qt5Agg')   
    
    fig = plt.figure()
    fig.canvas.mpl_connect('key_press_event', on_key)
    

    #a = anim.FuncAnimation(fig, drawFrame, frames=gMaxFrameIdx, repeat=False)
    
    drawFrame(0)
    plt.show()
    
    
    

