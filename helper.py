import cv2
import numpy as np 
from PIL import Image
from skimage import measure, color, io
from scipy import ndimage
from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
import streamlit as st

@st.cache(suppress_st_warning=True) 
def import_image(file):
    img = Image.open(file)
    img = img.convert("RGB")
    img = np.array(img)
    return img

@st.cache(suppress_st_warning=True) 
def canny_edge(img, lw=100, hg=200):
    try:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except:
        pass # alreary converted to grayscale for filter
    return cv2.Canny(img, lw, hg)

@st.cache(suppress_st_warning=True) 
def sobel_edge(img):
    try:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except: 
        pass # alreary converted to grayscale for filter
    grad_x = cv2.Sobel(img,  cv2.CV_16S, 1, 0, ksize=3, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT) # sobel on x
    grad_y = cv2.Sobel(img,  cv2.CV_16S, 0, 1, ksize=3, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT) # "" on y
    abs_grad_x = cv2.convertScaleAbs(grad_x) 
    abs_grad_y = cv2.convertScaleAbs(grad_y)    
    grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0) # add x and y
    return grad

@st.cache(suppress_st_warning=True) 
def prewitt_edge(img):
    try:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except:
        pass # alreary converted to grayscale for filter
    kernelx = np.array([[1,1,1],[0,0,0],[-1,-1,-1]])
    kernely = np.array([[-1,0,1],[-1,0,1],[-1,0,1]])
    img_prewittx = cv2.filter2D(img, -1, kernelx)
    img_prewitty = cv2.filter2D(img, -1, kernely)
    prewitt = img_prewittx + img_prewitty
    return prewitt

@st.cache(suppress_st_warning=True) 
def watershed(img):
    try:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except:
        pass # alreary converted to grayscale for filter
    kernel = np.ones((3,3), np.uint8)
    _,thresh1 = cv2.threshold(img,30,255,cv2.THRESH_BINARY)
    eroded = cv2.erode(thresh1, kernel, iterations=0)
    dilated = cv2.dilate(eroded, kernel, iterations=0)
    dst = cv2.filter2D(dilated,-1,kernel)
    blur = cv2.GaussianBlur(dst,(5,5),0)
    mask = blur == 0
    s = [[1,1,1], [1,1,1], [1,1,1]]
    labeled_mask, num_labels = ndimage.label(mask, structure=s)
    resultado_final = color.label2rgb(labeled_mask, bg_label=0)
    clusters = measure.regionprops(labeled_mask, img)
    propList = ["Area", "equivalent_diameter", "orientation",
                "MajorAxisLength", "MinorAxisLength", "Perimeter", 
                "Perimeter", "MinIntensity", "MeanIntensity", 
                "MaxIntensity"]

    output_file = open("medidas"+".csv", "w")
    output_file.write(("," + ",".join(propList)+"\n"))

    for cluster_props in clusters:
        output_file.write(str(cluster_props["Label"]))
        for _, prop in enumerate(propList):
            if(prop=="Area"):
                to_print = cluster_props[prop]*1**2
            elif(prop=="orientation"):
                to_print = cluster_props[prop]*57.2958
            elif(prop.find("Intensity")<0):
                to_print = cluster_props[prop]*1
            else:
                to_print = cluster_props[prop]
            output_file.write("," +str(to_print))
        output_file.write("\n")
        

    return resultado_final, num_labels

@st.cache(suppress_st_warning=True) 
def slic_image(img, num):
    segments = slic(img, n_segments = num, sigma = 3, start_label=1)
    result = mark_boundaries(img, segments)
    return result, segments

@st.cache(suppress_st_warning=True)
def mean_shift(img, sp, sr):
    return cv2.pyrMeanShiftFiltering(img, sp, sr)

@st.cache(suppress_st_warning=True)
def gaussian_blur(img, kernel):
    try:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except:
        pass
    return cv2.GaussianBlur(img,(kernel,kernel),0)


@st.cache(suppress_st_warning=True)
def draw_borders(img,img_real, gthan=50):
    kernel = np.ones((3,3),np.uint8)
    closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    binary = cv2.threshold(closing,127,255,cv2.THRESH_BINARY)[1]
    w, h ,x= img_real.shape
    original = np.ones((w,h,x), dtype="uint8")*255
    cnts = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    found = []
    for c in cnts:
        area = cv2.contourArea(c)
        if area > gthan:
            cv2.drawContours(original,[c], 0, ( 200, 0, 128 ), 2)
            found.append(c)
    contours = cv2.addWeighted(img_real,0.4,original,0.6,0) 

    return contours, found