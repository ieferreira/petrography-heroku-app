import streamlit as st
from helper import *
from hed  import *
import pandas as pd

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

st.markdown("""## Algoritmos de visión artificial y secciones delgadas 🔬""")
st.sidebar.title("Algoritmos y parámetros")
st.markdown("Diseñado para imagenes petrográficas de secciones delgadas")
st.sidebar.markdown("Algoritmos a usar y parámetros con los que se implementan")
st.write("#### Por favor, sube una imagen")

file = st.file_uploader("", type=["jpg","png"])

if file is None:
    st.text("Por favor, sube una imagen...")

if file:
    img = import_image(file)
    img_org = img.copy()
    
    st.sidebar.markdown("### Preprocesamiento")
    gauss = st.sidebar.radio("Gaussian Filter", (False, True), key='gauss')
    

    if gauss:
        ksize = st.sidebar.number_input("tamaño del kernel para gauss (impar)", 3, 15, step=2, key='ksize')
        try: 
            img = gaussian_blur(img, ksize)
        except: 
            st.write("No se pudo realizar la operación, trata de hacerlo con la imagen original sin filtros")



    if not gauss:
        mshift = st.sidebar.radio("Mean Shift Filter (Gaussian en False)", (False, True), key='meanshift')
        if mshift:
            sp = st.sidebar.number_input("sp: radio ventana", 20, 500, step=10, key='sp')
            sr = st.sidebar.number_input("sr: radio ventana de color", 50, 500, step=10, key='sr')
            img = mean_shift(img, sp, sr)
            img_mshift = img.copy()

    st.sidebar.markdown("### Detección de Bordes")
    bordes = st.sidebar.radio("", ("Ninguno", "Canny", "Sobel", "Prewitt", "HED"), key="border")

    st.write("### Imagen")

    if bordes=="Ninguno":
        st.image(img, use_column_width=True)
    else:
        st.write("#### Imagen con Filtros aplicados") 

        if bordes == "Canny":
            lw = st.sidebar.number_input("umbral inferior", 100, 500, step=10, key='l')
            hg = st.sidebar.number_input("umbral superior (doble o triple que el inferior", 200, 500, step=10, key='s')
            img = canny_edge(img, lw, hg)
            st.image(img, use_column_width=True)     

        elif bordes == "Sobel":
            img = sobel_edge(img)
            if st.sidebar.radio("Binarize ☯", (False, True), key="bin"):
                low = st.sidebar.number_input("umbral inferior binarización", 0, 254,100, step=10, key='low')
                high = st.sidebar.number_input("umbral superior binarización", 1, 255,255, step=10, key='high') 
                img = binarize(img, low, high)
            st.image(img, use_column_width=True)


        elif bordes == "Prewitt":
            img = prewitt_edge(img)
            if st.sidebar.radio("Binarize ☯", (False, True), key="bin"):
                low = st.sidebar.number_input("umbral inferior binarización", 0, 254,100, step=10, key='low')
                high = st.sidebar.number_input("umbral superior binarización", 1, 255,255, step=10, key='high') 
                img = binarize(img, low, high)
            st.image(img, use_column_width=True)
        
        elif bordes == "HED":
            img = hed_filter(img)

            if st.sidebar.radio("Binarize ☯", (False, True), key="bin"):
                low = st.sidebar.number_input("umbral inferior binarización", 0, 254,100, step=10, key='low')
                high = st.sidebar.number_input("umbral superior binarización", 1, 255,255, step=10, key='high') 
                img = binarize(img, low, high)
            st.image(img, use_column_width=True)

        st.sidebar.markdown("### Conteo de granos (rudimentario) 🤹‍♂️")
        if st.sidebar.radio("Watershed", (False, True), key="watershed"):           
            img_res, labels = watershed(img)
            st.write(f"Granos encontrados usando Watershed: {labels}")
            st.image(img_res, use_column_width=True)
            if st.sidebar.checkbox("Mostrar datos estadísticos", False):
                st.subheader("Datos Estadísticos (en pixeles o pixeles cuadrados)")
                df = pd.read_csv("medidas.csv")
                df = df.drop(columns = ["Unnamed: 0", "MinIntensity", "MeanIntensity","MaxIntensity", "Perimeter.1"])
                df = df.rename(columns={"Area": "Área", "equivalent_diameter": "Diámetro equivalente", "orientation": "Orientación",\
                                "MajorAxisLength": "Longitud Eje Mayor", "MinorAxisLength": "Longitud Eje Menor",\
                                "Perimeter": "Perímetro"})
                st.write(df)
            if mshift == True:
                if st.sidebar.radio("SLIC (Clusters)", (False, True), key="slic"):
                    img_slic, segments = slic_image(img_mshift, labels)
                    st.write(f"Usando los granos encontrados en Watershed, se encuentran {len(np.unique(segments))} usando SLIC")
                    st.image(img_slic, use_column_width=True)

        if bordes == "Canny":
            if st.sidebar.radio("Find Contours", (False, True), key="fcontours"):
                treshold = st.sidebar.number_input("Umbral desde el cual contar contornos", 1, 300, 50,step=10, key='th')
                contours, nums = draw_borders(img,  img_org, treshold)
                st.write(f"Granos encontrados usando contornos {len(nums)}")
                st.image(contours, use_column_width=True)

st.markdown("Programado por Iván Ferreira, UnalGeo-Bogotá (2020). [Github! 🎯](https://github.com/ieferreira)")
