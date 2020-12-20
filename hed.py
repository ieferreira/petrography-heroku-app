# Load the model.
import cv2 as cv
import numpy as np
import streamlit as st 

@st.cache(suppress_st_warning=True)
def hed_filter(image):

    class CropLayer(object):
        # TAKEN FROM: https://github.com/opencv/opencv/blob/master/samples/dnn/edge_detection.py
        def __init__(self, params, blobs):
            self.xstart = 0
            self.xend = 0
            self.ystart = 0
            self.yend = 0

        # Our layer receives two inputs. We need to crop the first input blob
        # to match a shape of the second one (keeping batch size and number of channels)
        def getMemoryShapes(self, inputs):
            inputShape, targetShape = inputs[0], inputs[1]
            batchSize, numChannels = inputShape[0], inputShape[1]
            height, width = targetShape[2], targetShape[3]

            self.ystart = int((inputShape[2] - targetShape[2]) / 2)
            self.xstart = int((inputShape[3] - targetShape[3]) / 2)
            self.yend = self.ystart + height
            self.xend = self.xstart + width

            return [[batchSize, numChannels, height, width]]

        def forward(self, inputs):
            return [inputs[0][:,:,self.ystart:self.yend,self.xstart:self.xend]]

    net = cv.dnn.readNetFromCaffe("deploy.prototxt", "hed_pretrained_bsds.caffemodel")
    cv.dnn_registerLayer('Crop', CropLayer)




    #image=cv.resize(image,(args.width,args.height))

    inp = cv.dnn.blobFromImage(image, scalefactor=1.0, size=image.shape[:2],
                            mean=(104.00698793, 116.66876762, 122.67891434),
                            swapRB=False, crop=False)
    net.setInput(inp)
    # edges = cv.Canny(image,image.shape[1],image.shape[0])
    out = net.forward()

    out = out[0, 0]
    out = cv.resize(out, (image.shape[1], image.shape[0]))
    out=cv.cvtColor(out,cv.COLOR_GRAY2BGR)
    out = 255 * out
    out = out.astype(np.uint8)

    return out