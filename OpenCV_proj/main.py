import cv2 as cv
import numpy as np

img = cv.imread('images/test3.png')

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

### программа
img = rotate(img, 90)
img = grayscale(img)

cv.imwrite("processed_images/Test.png", img)
cv.imshow("Result", img)
cv.waitKey(0)
