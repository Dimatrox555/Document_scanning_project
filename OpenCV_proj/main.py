import cv2 as cv
import numpy as np
import json

h, w = 0, 0
points = []
### создание точек назначения для трансформации (примерно лист а4)
destination_points = np.array([[0, 0], [297, 0], [0, 210], [297, 210]], dtype=np.float32)

### чтение png
def img_read(path, k):
    result = cv.imread(path)
    if result != None:
        global h,w
        h = result.shape[0]*k
        w = result.shape[1]*k
        result = cv.resize(result, (w, h))
        return result
    else: return 0

### чтение разметки
def markdown_read(path):
    file = open(path, 'r')
    data = json.load(file)

    ### создание списка словарей с данными о точках
    point_data = []
    for i in data[4]['kp-1']:
        point_data.append(i)

### создание списка с координатами всех точек в пикселях
    global points
    points = np.array([
        [point_data[0]['x']/100*w, point_data[0]['y']/100*h],
        [point_data[1]['x']/100*w, point_data[1]['y']/100*h],
        [point_data[2]['x']/100*w, point_data[2]['y']/100*h],
        [point_data[3]['x']/100*w, point_data[3]['y']/100*h]
    ], dtype=np.float32)


### трансформация изображения
def image_transform(target, k):
    ## получение матрицы перспективы из разметки и точек назначения
    mat = cv.getPerspectiveTransform(points, destination_points*k)
    ## вывод нужного изображения
    return cv.warpPerspective(target, mat, (297*k, 210*k))

### конвертация изображения в чёрно-белый
def grayscale(image):
    result = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
    _, result = cv.threshold(result, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)
    return result

def main():
    ### программа
    img = img_read('images/synth_example.png', 14)
    markdown_read('images/json_main.json')

    img = image_transform(img, 14)
    img = grayscale(img)

    ### запись готового результата в файл и показ изображения
    cv.imwrite("processed_images/Test.tiff", img)
    cv.imshow("Result", img)

    cv.waitKey(0)
main()