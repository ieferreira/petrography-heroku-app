import cv2
import streamlit as st
from helper import *
from PIL import Image, ImageOps


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

st.markdown("""## Algoritmos de visión artificial y secciones delgadas""")
st.sidebar.title("Panel de control")
st.markdown("Diseñado para imagenes petrográficas de secciones delgadas")
st.sidebar.markdown("Parametros y valores")
st.write("#### Por favor, sube una imagen")

file = st.file_uploader("", type=["jpg"])

if file is None:
    st.text("Por favor, sube una imagen...")

if file:
    img = import_image(file)

    st.sidebar.subheader("Elige un algoritmo de detección de bordes")
    bordes = st.sidebar.radio("Detección de bordes", ("Ninguno", "Canny", "Sobel", "Prewitt"), key="border")

    gauss = st.sidebar.radio("Gaussian Filter (kernel de 5x5)", (False, True), key='gauss')
    mshift = st.sidebar.radio("Mean Shift Filter (Gaussian en False)", (False, True), key='meanshift')



    if gauss:
        try: 
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.GaussianBlur(img,(5,5),0)
        except: 
            st.write("No se pudo realizar la operación, trata de hacerlo con la imagen original sin filtros")



    if mshift:
        sp = st.sidebar.number_input("sp: radio ventana", 20, 500, step=10, key='sp')
        sr = st.sidebar.number_input("sr: radio ventana de color", 50, 500, step=10, key='sr')
        img = cv2.pyrMeanShiftFiltering(img, sp, sr)
        img_mshift = img.copy()
    st.write("### Imagen")
    #st.image(img, use_column_width=True)
 
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
            st.image(img, use_column_width=True)

        elif bordes == "Prewitt":
            img = prewitt_edge(img)
            st.image(img, use_column_width=True)


        if st.sidebar.radio("Watershed", (False, True), key="watershed"):           
            img_res, labels = watershed(img)
            st.write(f"Granos encontrados usando Watershed: {labels}")
            st.image(img_res, use_column_width=True)

            if st.sidebar.radio("SLIC (Clusters)", (False, True), key="slic"):
                img_slic, segments = slic_image(img_mshift, labels)
                st.write(f"Usando los granos encontrados en Watershed, se encuentran {len(np.unique(segments))} usando SLIC")
                st.image(img_slic, use_column_width=True)

st.write("Programado por Iván Ferreira, unalgeo-Bogotá (2020)")