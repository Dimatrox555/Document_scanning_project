import cv2 as cv
import numpy as np
import json

### чтение png
img = cv.imread('images/example.jpg')
h, w = img.shape[:2]

### чтение разметки
file = open('images/json_main.json', 'r')
data = json.load(file)

### создание списка словарей с данными о точках
point_data = []
for i in data[3]['kp-1']:
    point_data.append(i)

### создание списка с координатами всех точек в пикселях
points = np.array([
    [point_data[0]['x']/100*w, point_data[0]['y']/100*h],
    [point_data[1]['x']/100*w, point_data[1]['y']/100*h],
    [point_data[2]['x']/100*w, point_data[2]['y']/100*h],
    [point_data[3]['x']/100*w, point_data[3]['y']/100*h]
], dtype=np.float32)

### создание точек назначения для трансформации (примерно лист а4)
destination_points = np.array([[0, 0], [297, 0], [0, 210], [297, 210]], dtype=np.float32)

### трансформация изображения
def image_transform(target):
    ## получение матрицы перспективы из разметки и точек назначения
    mat = cv.getPerspectiveTransform(points, destination_points*2)
    ## вывод нужного изображения
    return cv.warpPerspective(target, mat, (297*2, 210*2))

### конвертация изображения в чёрнобелый
def grayscale(image):
    result = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
    return result

### программа
img = image_transform(img)
img = grayscale(img)

### запись готового результата в файл и показ изображения
cv.imwrite("processed_images/Test.png", img)
cv.imshow("Result", img)

cv.waitKey(0)
