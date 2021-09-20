import urllib.request
import numpy as np
import os
import cv2
import tweepy
import random
import textwrap
import json
from simple_image_download import simple_image_download as simp
from PIL import Image, ImageFont, ImageDraw
import mediapipe as mp
mp_selfie_segmentation = mp.solutions.selfie_segmentation
# INICIO DE DATOS PARA TWITTER

oauth_token = '1430932295096078344-n9KF0y5GQHU07CX7tDc60eklI0sT7j'
oauth_token_secret = 'Uxtx2inm2jBJNUUHfiEtjwxeV7ds7oAnY5hxASzH6mjxz'
api_key = 'XCMHWaOvQyvEdDZW6ZNVN1Uis'
api_secret_key = 'Q4sEiXvokpp53319sijt23cQyWVueSC2zHiWUdR9lh1cc6ypQK'

oauth_token='1433442528708157444-doUOLaRJ9mP9fEWpTznEcYyfufVtx4'
oauth_token_secret='a159bFEUD9Lage6R5xmiAAV9ufIP8UtSxlrLASs3Fetjm'

auth = tweepy.OAuthHandler(api_key, api_secret_key)
auth.set_access_token(oauth_token, oauth_token_secret)
api = tweepy.API(auth)

def google_images(busqueda):
    response = simp.simple_image_download
    return response().urls(busqueda, 10, extensions={'.jpg', '.png', '.ico', '.gif', '.jpeg'})


def conversor(url):
    req = urllib.request.urlopen(url)
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    image = cv2.imdecode(arr, -1)
    return image


def url_to_image(urls, i=0):
    for url in urls:
        try:
            image = conversor(url)
            break
        except:
            if i > len(urls):
                print("no anduvo ninguna!")
            else:
                print("Error. Probando con la siguiente")
    return image


def random_noticia():
    f = open('noticias.json', encoding="utf-8")
    data = json.load(f)

    lugar = random.choice(data['lugar'])
    print("busco en google")
    urls = google_images(lugar)
    print("traigo la imagen")

    imagen = url_to_image(urls)

    noticia = random.choice(data['name']) + ", " + random.choice(data['job']) + ", fue visto con " + random.choice(data['acompañante']) + " en " + lugar + " " + random.choice(data['accion']) + "."

    return noticia, imagen


def resize(width, height, image):
    dim = (width, height)
    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)


def paste_in_background(texto, imagen):
    imgFondo = cv2.imread('fondo.jpg', cv2.IMREAD_UNCHANGED)

    resized_fondo = resize(1000, 1200, imgFondo)
    cv2.imwrite('imagen.jpg', resized_fondo)

    resized_lugar = resize(970, 650, imagen)

    cv2.imwrite('imagenLugar.jpg', resized_lugar)
    fondo = Image.open("imagen.jpg")

    imagen_a_pegar = Image.open("imagenlugar.jpg").convert('RGBA')
    fondo.paste(imagen_a_pegar, (5, 230), imagen_a_pegar)

    fondo_editable = ImageDraw.Draw(fondo)

    font = ImageFont.truetype(font='Clarins-Regular Regular.ttf', size=42)
    text = textwrap.fill(text=texto, width=60)

    fondo_editable.text(xy=(20, 900), text=text, font=font, fill='#000000')
    fondo.save('imagen.jpg', quality=95, format="png")


print("arranco")

texto, imagen = random_noticia()
paste_in_background(texto, imagen) 

iaasas = cv2.imread("imagen.jpg")

# descomentar lineas para ver la imagen antes de tuitear
# cv2.imshow("aa", iaasas)
# cv2.waitKey(0)

tuit = api.media_upload("imagen.jpg")
os.remove("imagen.jpg")
os.remove("imagenLugar.jpg")

tuit = api.update_status(texto, media_ids=[tuit.media_id])

print(tuit)


