"""
Author: Iván E. Ferreira
License: MIT
"""
import streamlit as st
from helper import *
from hed  import *
import pandas as pd
import matplotlib.pyplot as plt

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

st.markdown("""## Computer vision algorithms and thin sections (petrography)""")
st.sidebar.title("Algorithms and parameters")
st.markdown("An online app for petrographers (work in progress) please leave any comments to iveferreirach[at]unal.edu.co")
st.sidebar.markdown("Algorithms to use and parameters")
st.write("#### Please, Upload an Image")

file = st.file_uploader("", type=["jpg","png"])

if file is None:
    st.text("Upload an image..")
    st.sidebar.markdown("#### Waiting for an image...")

if file:
    img = import_image(file)
    img_org = img.copy()    
    st.sidebar.markdown("### Preprocessing")
    color_model = st.sidebar.selectbox("Color Model", ("RGB", "GRAY", "HSL", "HSV", "YBR"))

    if color_model == "RGB":
        pass
    elif color_model == "HSL":
        img = convert_hsl(img)
    elif color_model == "HSV":
        img = convert_hsv(img)
    elif color_model == "YBR":
        img = convert_ybr(img)
    else:
        img = convert_gray(img)


    gauss = st.sidebar.radio("Gaussian Filter", (False, True), key='gauss')    

    if gauss:
        ksize = st.sidebar.number_input("Size of kernel (odd)", 3, 15, step=2, key='ksize')
        try: 
            img = gaussian_blur(img, ksize)
        except: 
            st.write("Couldn't realize operation, try image without filters (none)")



    if not gauss:
        mshift = st.sidebar.radio("Mean Shift Filter (Gaussian en False)", (False, True), key='meanshift')
        if mshift:
            sp = st.sidebar.number_input("sp: radio ventana", 1, 500,20, step=10, key='sp')
            sr = st.sidebar.number_input("sr: radio ventana de color", 1, 500,50, step=10, key='sr')
            img = mean_shift(img, sp, sr)
            img_mshift = img.copy()

    st.sidebar.markdown("### Edge detection")
    bordes = st.sidebar.radio("", ("None", "Canny", "Sobel", "Prewitt"), key="border")#, "HED"#

    st.write("### Imagen")

    if bordes=="None":
        st.image(img, use_column_width=True)
    else:
        st.write("#### Image with applied filters") 

        if bordes == "Canny":
            lw = st.sidebar.number_input("Lower threshold", 1, 500,100, step=10, key='l')
            hg = st.sidebar.number_input("Upper threshold (around twice or thrice lower)", 2, 500,200, step=10, key='s')
            img = canny_edge(img, lw, hg)
            st.image(img, use_column_width=True)     

        elif bordes == "Sobel":
            img = sobel_edge(img)
            if st.sidebar.radio("Binarize ☯", (False, True), key="bin"):
                low = st.sidebar.number_input("Lower threshold (binarization)", 0, 254,100, step=10, key='low')
                high = st.sidebar.number_input("Upper threshold (binarization)", 1, 255,255, step=10, key='high') 
                img = binarize(img, low, high)
            st.image(img, use_column_width=True)


        elif bordes == "Prewitt":
            img = prewitt_edge(img)
            if st.sidebar.radio("Binarize ☯", (False, True), key="bin"):
                low = st.sidebar.number_input("Lower threshold (binarization)", 0, 254,100, step=10, key='low')
                high = st.sidebar.number_input("Upper threshold (binarization)", 1, 255,255, step=10, key='high') 
                img = binarize(img, low, high)
            st.image(img, use_column_width=True)
        
        # elif bordes == "HED":
        #     img = hed_filter(img)

        #     if st.sidebar.radio("Binarize ☯", (False, True), key="bin"):
        #         low = st.sidebar.number_input("Lower threshold (binarization)", 0, 254,100, step=10, key='low')
        #         high = st.sidebar.number_input("Upper threshold (binarization)", 1, 255,255, step=10, key='high') 
        #         img = binarize(img, low, high)
        #     st.image(img, use_column_width=True)

        st.sidebar.markdown("### Grain Counting (work in progress) 🤹‍♂️")
        if st.sidebar.radio("Watershed", (False, True), key="watershed"):           
            img_res, labels = watershed(img)
            st.write(f"Grains found using watershed: {labels}")
            st.image(img_res, use_column_width=True)
            if st.sidebar.checkbox("Show statistical data: ", False):
                st.subheader("Statistical data found (units are pixels, pixels$^2$ or degrees)")
                df = pd.read_csv("medidas.csv")
                df = df.drop(columns = ["Unnamed: 0", "MinIntensity", "MeanIntensity","MaxIntensity", "Perimeter.1"])
                df = df.rename(columns={"Area": "Area", "equivalent_diameter": "Equivalent Diameter", "orientation": "Orientation",\
                                "MajorAxisLength": "Major Axis Length", "MinorAxisLength": "Minor Axis Length",\
                                "Perimeter": "Perimeter"})                                
                st.write(df)
                fig, ax = plt.subplots()
                df_hist = df["Perimeter"]
                df_hist.hist(bins=100)
                plt.title("Size Distribution of Grain Diameter")
                st.pyplot(fig)
            try:
                if mshift == True:
                    if st.sidebar.radio("SLIC (Clusters)", (False, True), key="slic"):
                        img_slic, segments = slic_image(img_mshift, labels)
                        st.write(f"Usando los granos encontrados en Watershed, se encuentran {len(np.unique(segments))} usando SLIC")
                        st.image(img_slic, use_column_width=True)
            except:
                st.write("Mean Shift not applied")
        if bordes == "Canny":
            if st.sidebar.radio("Find Contours", (False, True), key="fcontours"):
                treshold = st.sidebar.number_input("Umbral desde el cual contar contornos", 1, 300, 50,step=10, key='th')
                contours, nums = draw_borders(img,  img_org, treshold)
                st.write(f"Granos encontrados usando contornos {len(nums)}")
                st.image(contours, use_column_width=True)

st.markdown("Programmed by Iván Ferreira, UnalGeo-Bogotá (2020). [Github! 🎯](https://github.com/ieferreira)")
