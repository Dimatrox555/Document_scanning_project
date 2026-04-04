import cv2 as cv
import numpy as np
import json

h, w = 0, 0
points = []
### создание точек назначения для трансформации (примерно лист а4)
destination_points = np.array([[0, 0], [297, 0], [0, 210], [297, 210]], dtype=np.float32)


def read(img_path, json_path, k):
    ## чтение картиночки
    img_output = cv.imread("images/"+img_path)
    h = img_output.shape[0]*k
    w = img_output.shape[1]*k
    img_output = cv.resize(img_output, (w,h))

    ## чтение джсона
    file = open("images/"+json_path, "r")
    data = json.load(file)

    point_data = []
    for i in data[4]['kp-1']:
        point_data.append(i)

    global points
    points = np.array([
        [point_data[0]['x'] / 100 * w, point_data[0]['y'] / 100 * h],
        [point_data[1]['x'] / 100 * w, point_data[1]['y'] / 100 * h],
        [point_data[2]['x'] / 100 * w, point_data[2]['y'] / 100 * h],
        [point_data[3]['x'] / 100 * w, point_data[3]['y'] / 100 * h]
    ], dtype=np.float32)

    return img_output


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

def preprocess(img_path="synth_example.png", k=4):
    ### программа
    img = read(img_path, "json_main.json", k)
    img = image_transform(img, k)
    img = grayscale(img)

    ### запись готового результата в файл и показ изображения
    cv.imwrite("processed_images/Test.tiff", img)
    #cv.imshow("Result", img)

    #cv.waitKey(0)

    return "processed_images/Test.tiff"
if __name__ == "__main__":
    preprocess("synth_example.png")