import cv2 as cv
import numpy as np
import json
import math


### чтение png
img = cv.imread('images/testt.png')
h, w = img.shape[:2]

### чтение разметки
file = open('images/json_main.json', 'r')
data = json.load(file)

### создание списка словарей с данными о точках
point_data = []
for i in data[1]['kp-1']:
    point_data.append(i)

### создание словаря с координатами всех точек в пикселях
points = {
    "point1": [point_data[0]['x']/100*w, point_data[0]['y']/100*h],
    "point2": [point_data[1]['x']/100*w, point_data[1]['y']/100*h],
    "point3": [point_data[2]['x']/100*w, point_data[2]['y']/100*h],
    "point4": [point_data[3]['x']/100*w, point_data[3]['y']/100*h]
}

### вычисления необходимого угла поворота через тангенс
rotation_angle = math.degrees(math.atan2((points['point1'][1]-points['point2'][1]), (points['point2'][0]-points['point1'][0])))

### вращение изображения
def rotate(image, angle):
    ## добавим чёрные края по бокам чтобы изображение себя не обрезало

    image_padded = cv.copyMakeBorder(image, 150, 150, 150, 150, cv.BORDER_CONSTANT, (255, 255, 255))
    ## найдём центр вращения
    height, width = image_padded.shape[:2]
    rotation_point = (width // 2, height // 2)

    ## найдём какую-то матрицу вращения и вернём развёрнутое изображение
    mat = cv.getRotationMatrix2D(rotation_point, angle, 1)
    return cv.warpAffine(image_padded, mat, (width, height))

### конвертация изображения в чёрнобелый
def grayscale(image):
    result = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
    return result

### программа

img = rotate(img, -rotation_angle)
img = grayscale(img)

### запись готового результата в файл и показ изображения
cv.imwrite("processed_images/Test.png", img)
cv.imshow("Result", img)

cv.waitKey(0)
