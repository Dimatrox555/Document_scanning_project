import cv2 as cv
import numpy as np
import json
from pathlib import Path


points = []
### создание точек назначения для трансформации (примерно лист а4)
destination_points = np.array([[0, 0], [297, 0], [0, 210], [297, 210]], dtype=np.float32)


def read(img_path, json_path, k):

    ## чтение картиночки
    img_output = cv.imread(img_path)
    if img_output.any() != None:
        h = img_output.shape[0]*k
        w = img_output.shape[1]*k
        img_output = cv.resize(img_output, (w,h))
    else: img_output = 0
    ## чтение джсона
    file = open(json_path, "r")
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

def preprocess(img_path="0.png", k=4):
    ### создание путей
    parent_dir = Path(__file__).parent.absolute()
    json_dir = parent_dir / "json/json_main.json"

    ## вычисление количества изображений
    image_dir = parent_dir / "images"
    num = sum(1 for i in image_dir.iterdir())


    output_arr = []
    # программа
    for i in range(num):

        ### создание пути вывода
        output_dir = parent_dir / f"processed_images/{i}.tiff"
        img_dir = parent_dir / "images" / f"{i}.png"
        ### обработка изображения
        img = read(str(img_dir), str(json_dir), k)
        img = image_transform(img, k)
        img = grayscale(img)

        ### запись готового результата в файл и показ изображения
        cv.imwrite(output_dir, img)
        output_arr.append(str(output_dir))
        #cv.imshow("Result", img)
    #cv.waitKey(0)
    print(output_arr)
    return output_arr

if __name__ == "__main__":
    preprocess()
