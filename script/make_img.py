from PIL import Image
from urllib.request import urlopen
import os
from script.attempt import make_bar
import cv2


def color_bar(url, name):
    im = Image.open(urlopen(url))
    size = (100, 100)
    out = im.resize(size)
    out.save('img.jpg')
    image = cv2.imread('img.jpg')
    bar = make_bar(image, 3)
    img = Image.fromarray(bar, 'RGB')
    img.save(f'static/img/{name}.png')


def favorite_colour(list_of_img, name):
    img = Image.new('RGB', (300, 50 * len(list_of_img)))
    for n, image in enumerate(list_of_img):
        im = Image.open(f'static/img/{image + ".png"}')
        img.paste(im, (0, 50 * n))
    img.save(f'static/img/favorite1.jpg')
    i = Image.open(f'static/img/favorite1.jpg')
    img = cv2.imread(f'static/img/favorite1.jpg')
    bar = make_bar(img, 2)
    img = Image.fromarray(bar, 'RGB')
    img.save(f'static/img/{"favorite" + name}.png')

