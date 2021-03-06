import cv2
import numpy as np 
from PIL import Image
from skimage import measure, color, io, data, segmentation
from skimage.future import graph
from scipy import ndimage
from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
import streamlit as st

#! import images, maybe convert to .tiff later?
@st.cache(suppress_st_warning=True) 
def import_image(file):
    img = Image.open(file)
    img = img.convert("RGB")
    img = np.array(img)
    return img

#! Edge detections, HED in hed.py
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

#! Color models! 
@st.cache(suppress_st_warning=True) 
def convert_hsl(img):
    img= cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_hsl = cv2.cvtColor(img,cv2.COLOR_BGR2HLS)
    return img_hsl

@st.cache(suppress_st_warning=True) 
def convert_hsv(img):
    img= cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    return img_hsv

@st.cache(suppress_st_warning=True) 
def convert_ybr(img):
    img= cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_ybr = cv2.cvtColor(img,cv2.COLOR_BGR2YCR_CB)
    return img_ybr

@st.cache(suppress_st_warning=True) 
def convert_gray(img):
    img= cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    return img_gray

#! Grain counting algorithms
@st.cache(suppress_st_warning=True) 
def watershed(img):
    try:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except:
        pass # alreary converted to grayscale for filter
    kernel = np.ones((3,3), np.uint8)
    img =  cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    _,thresh1 = cv2.threshold(img,30,255,cv2.THRESH_BINARY)
    dst = cv2.filter2D(thresh1,-1,kernel)
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

#! Preprocessing (mean shit and gaussian blur)
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
def binarize(img, lw=100, hg=255):
    try:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except:
        pass
    _,binary = cv2.threshold(img,lw,hg,cv2.THRESH_BINARY)
    return binary


#! Hough Transform
@st.cache(suppress_st_warning=True)
def findLines(bordes, rho, theta, thr, mll, mlg):
    lineas = cv2.HoughLinesP(bordes, rho, theta, thr, minLineLength=mll, maxLineGap=mlg)
    return lineas
@st.cache(suppress_st_warning=True)
def drawLines(lineas, imagen):  
    if lineas is not None:
        for linea in lineas:
            x1,y1,x2,y2 = linea[0]
            # dibuja las lineas una a una en imagen, con color (255,0,0) y grosor de linea 1
            cv2.line(imagen, (x1,y1), (x2,y2), (255, 0,0), 1)
    else:
        # por si no se encuentra lineas o el algoritmo no funciona con los params dados
        raise ValueError("No se encontraron lineas con los parámetros dados")
    return imagen
@st.cache(suppress_st_warning=True)
def findCircles(bordes,n, pm1, pm2, mnDis, mnRad,  mxRad):
    circles = cv2.HoughCircles(bordes, cv2.HOUGH_GRADIENT, n,  param1=pm1,  param2=pm2,
                            minDist=mnDis,  minRadius=mnRad, maxRadius=mxRad)
    return circles

#circulos = findCircles(imagen2,1,50,30,100,0,100)
@st.cache(suppress_st_warning=True)
def drawCircles(circulos, img, escala=None):

    if circulos is not None:
        circulos = np.uint16(np.around(circulos))
        for punto in circulos[0, :]:
            x, y, r = punto[0], punto[1], punto[2]

            # circunferencia del circulo
            cv2.circle(img, (x, y), r, (0, 255, 0), 2)
            # pone el dato del valor como un texto adjunto
            if escala is not None:
                pixsUm = escala/100
                um = r*pixsUm
                cv2.putText(img,f"Tamano={round(um,1)}um\n Area = {round(np.pi*um**2,1)} um^2", (x+10,y+10), cv2.FONT_ITALIC, 0.5, (200,50,0,255),2)
                 
            else: 
                cv2.putText(img,f"RADIO={r}px", (x+20,y+20), cv2.FONT_ITALIC, 0.5, (200,50,0,255),2)
                cv2.putText(img,f"AREA={np.round(np.pi*(r**2),1)}px^2", (x+20,y+40), cv2.FONT_ITALIC, 0.5, (200,50,0,255),2)


            # circulo para dibujar el radio, con color (0,122,255) y grosor de linea 3
            cv2.circle(img, (x, y), 1, (0, 122, 255), 3)
        return img
    else:
        raise ValueError("No se encontraron Círculos en la imagen que me pasaste con los parámetros dados")

@st.cache(suppress_st_warning=True)
def rag_merging(img):
    def weight_mean_color(graph, src, dst, n):
        diff = graph.nodes[dst]['mean color'] - graph.nodes[n]['mean color']
        diff = np.linalg.norm(diff)
        return {'weight': diff}

    def merge_mean_color(graph, src, dst):
        graph.nodes[dst]['total color'] += graph.nodes[src]['total color']
        graph.nodes[dst]['pixel count'] += graph.nodes[src]['pixel count']
        graph.nodes[dst]['mean color'] = (graph.nodes[dst]['total color'] /
                                        graph.nodes[dst]['pixel count'])
    labels = segmentation.slic(img, compactness=30, n_segments=400, start_label=1)
    g = graph.rag_mean_color(img, labels)

    labels2 = graph.merge_hierarchical(labels, g, thresh=35, rag_copy=False,
                                    in_place_merge=True,
                                    merge_func=merge_mean_color,
                                    weight_func=weight_mean_color)
    out = color.label2rgb(labels2, img, kind='avg', bg_label=0)
    out = segmentation.mark_boundaries(out, labels2, (0, 0, 0))
    return out, labels2 