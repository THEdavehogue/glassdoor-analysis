#!/usr/bin/python

# [PoC] tesseract OCR script - tuned for scr.im captcha
#
# Chris John Riley
# blog.c22.cc
# contact [AT] c22 [DOT] cc
# 12/10/2010
# Version: 1.0
#
# Changelog
# 0.1> Initial version taken from Andreas Riancho's \
#      example script (bonsai-sec.com)
# 1.0> Altered to use Python-tesseract, tuned image \
#      manipulation for scr.im specific captchas
#

from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from pytesseract import image_to_string
import os


def solve_captcha(path, i=0):
    img = Image.open(path)
    img = img.convert("RGBA")

    pixdata = img.load()

    # Make the letters bolder for easier recognition

    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            if pixdata[x, y][0] < 90:
                pixdata[x, y] = (0, 0, 0, 255)

    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            if pixdata[x, y][1] < 136:
                pixdata[x, y] = (0, 0, 0, 255)

    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            if pixdata[x, y][2] > 0:
                pixdata[x, y] = (255, 255, 255, 255)

    img.save("captchas/captcha_bw.tif")

    #   Make the image bigger (needed for OCR)
    im_orig = Image.open('captchas/captcha_bw.tif')
    w, h = im_orig.size
    big = im_orig.resize((w * 2, h * 2), Image.NEAREST)

    ext = ".tif"
    big.save('captchas/captcha_tess_{}.tif'.format(i))

    #   Perform OCR using tesseract-ocr library
    image = Image.open('captchas/captcha_tess_{}.tif'.format(i))
    solved = image_to_string(image)
    if solved = '':
        image = ImageOps.invert(image)
        solved = image_to_string(image)
    return solved


# def solve_captcha_2(path, i=0):
#     im = Image.open(path) # the second one
#     im = im.filter(ImageFilter.MedianFilter())
#     enhancer = ImageEnhance.Contrast(im)
#     im = enhancer.enhance(2)
#     im = im.convert('1')
#     im.save('captchas/captcha_tess_{}_2.tif'.format(i))
#     text = image_to_string(Image.open('captchas/captcha_tess_{}.tif'.format(i)))
#     return text


if __name__ == '__main__':
    solved = solve_captcha('captchas/captcha.tif')
    # solved2 = solve_captcha_2(f, i)
    print solved
