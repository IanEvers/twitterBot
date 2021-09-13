import urllib.request
import numpy as np
import os
import cv2
from simple_image_download import simple_image_download as simp
import mediapipe as mp
mp_selfie_segmentation = mp.solutions.selfie_segmentation
import tweepy
from PIL import Image, ImageFont, ImageDraw

# INICIO DE DATOS PARA TWITTER

oauth_token= '1430932295096078344-n9KF0y5GQHU07CX7tDc60eklI0sT7j'
oauth_token_secret= 'Uxtx2inm2jBJNUUHfiEtjwxeV7ds7oAnY5hxASzH6mjxz'
#user_id= '1430932295096078344'
#screen_name= 'AlguienDiceBot'

oauth_token_trucho= 'dc0VVgAAAAABS8w-AAABe5RJNio&oauth_token_secret=gyjVaCyzSL6RDqZxlVNiXO7nvRLXFbkQ&oauth_callback_confirmed=true'
api_key = 'lkWMGmFK300lszKQY6tPYbYEA'
api_secret_key = 'GfxVMbxr8AEIUeyt5KjurCK3I9hf6vdPtHam5k4Ft2cOnRVVNZ'
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAD7MSwEAAAAAfiDCTAgANOPLgEHVwjw8LtDUw6Y%3DKzJWF5uAn8HumNcDqhSReGUzN65h6E6ragNvYLecHfwtcG24yb'


auth = tweepy.OAuthHandler(api_key, api_secret_key)
auth.set_access_token(oauth_token, oauth_token_secret)
api = tweepy.API(auth)

# FIN DE DATOS PARA TWITTER
# INICIO DE MANEJO DE IMAGEN

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


def remove_background(image):
    with mp_selfie_segmentation.SelfieSegmentation() as selfie_segmentation:
        results = selfie_segmentation.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        image_height, image_width, channels = image.shape
        # hago una imagen full negro para poner donde no esta la persona
        negro = np.zeros((image_height,image_width, 3), np.uint8)
        condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.8
        output_image = np.where(condition, image, negro)
        # ahora que tengo la imagen cropeada, la fuerzo 400 x 400
        dim = (400, 400)
        resized = cv2.resize(output_image, dim, interpolation=cv2.INTER_AREA)
        cv2.imwrite("resized.png", resized)

        img = Image.open("resized.png")
        rgba = img.convert("RGBA")

        datas = rgba.getdata()
        newData = []

        for item in datas:

            if item[0] == 0 and item[1] == 0 and item[2] == 0:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)

        img.putdata(newData)
        img.save("imagenPersona.png", "PNG")
        iaasas = cv2.imread("imagenPersona.png")
        cv2.imshow("aa", iaasas)
        cv2.waitKey(0)
        return resized


def paste_in_background():
    title_font = ImageFont.truetype('PlayfairDisplay-VariableFont_wght.ttf', 200)
    imagen_a_pegar = Image.open("imagenPersona.png").convert('RGBA')

    img = cv2.imread('quote.jfif', cv2.IMREAD_UNCHANGED)
    width = 1800
    height = 1000
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    cv2.imwrite('imagen.jpg', resized)
    new_background = Image.open("imagen.jpg")

    new_background.paste(imagen_a_pegar, (1400,600), imagen_a_pegar)
    new_background_editable = ImageDraw.Draw(new_background)

    new_background_editable.text((15,15), texto, (237, 230, 211), font=title_font)
    new_background.save('imagen.jpg', quality=95, format="png")


# bueno, paso a plantear al bot ya que estamos
# 1. le llega un texto tipo "alberto fernandez dice tal cosa en letra arial tamaño 12 con fondo de pobres " o "@iansitoE dice me la como"
# 2. Si es una persona:
# 2a. se divide el string en: la persona a buscar (antes del 'dice'), el texto (después del 'dice', hasta el 'en letra'),
#     el font-style (entre 'en letra' y 'tamaño')
# 2b. se guglea laPersona + 'de frente' y se obtiene una imagen cropeada 400x400 de la misma.
# 2c. si el texto empieza con un '@' entonces se genera un falso tuit del usuario correspondiente

texto_mock = 'la china suarez dice estuve con wos, lo admito'
texto_mock_2 = 'trump dice Biden, no me la contes'

persona, texto, letra, fondo = ["","","",""]

def defino_variables(texto_mock_2, persona, texto, letra, fondo):
    # separo al string en substrings
    if texto_mock_2.find("dice") != -1:
        persona = texto_mock_2.split('dice')[0]
    else:
        persona = ""
    if texto_mock_2.find("dice") != -1:
        texto = texto_mock_2.split('dice')[1].split('en letra')[0].split('con fondo de')[0]
    else:
        texto = ""
    if texto_mock_2.find("en letra") != -1:
        letra = texto_mock_2.split('en letra')[1].split('con fondo de')[0]
    else:
        letra = ""
    if texto_mock_2.find("con fondo de") != -1:
        fondo = texto_mock_2.split('con fondo de')[1]
    else:
        fondo = ""
        return  persona, texto, letra, fondo

persona, texto, letra, fondo = defino_variables(texto_mock_2, persona, texto, letra, fondo)

print("arranco")
print("busco en google")
urls = google_images(persona + ' ' + 'de frente')
print("traigo la imagen")
imagen = url_to_image(urls)
print("le saco el fondo")
imagenPersona = remove_background(imagen)
print("le meto las cosas")
paste_in_background()


tuit = api.media_upload("imagen.jpg")
#os.remove("imagen.jpg")
#os.remove("imagenPersona.png")
#os.remove("resized.png")
#tuit = api.update_status(" '" + texto + "' - " + persona, media_ids=[tuit.media_id])
print(tuit)

