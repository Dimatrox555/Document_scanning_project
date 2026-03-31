import cv2 as cv
import numpy as np


### вращение изображения
def rotate(image, angle):
    height, width = image.shape[:2]
    rotation_point = (width//2, height//2)
    mat = cv.getRotationMatrix2D(rotation_point, angle, 1)
    return cv.warpAffine(image, mat, (width, height))

### конвертация изображения в чёрнобелый
def grayscale(image):
    result = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
    return result


