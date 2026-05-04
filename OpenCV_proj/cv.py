import cv2 as cv
import numpy as np
import json
from pathlib import Path
from pdf2image import convert_from_path
import platform
import shutil
b = 0

### создание точек назначения для трансформации (примерно лист а4)
destination_points = np.array([[0, 0], [297, 0], [0, 210], [297, 210]], dtype=np.float32)
### абсолютный путь на папку моего проекта чтобы иные модули не взрывались
parent_dir = Path(__file__).parent.absolute()

### переделка пдфайла в пнг
def pdf2png(path):
    pdf_path = str(path)

    poppler_path = parent_dir / "poppler" / "Library" / "bin"
    images_dir = parent_dir / "images"

    images = convert_from_path(pdf_path, poppler_path=poppler_path)

    ## переименование картинок в 1234...
    global b
    for i, image in enumerate(images, start=b):
        image.save(images_dir / f"{b}.png", "PNG")
        b += 1

def read(img_path, json_path, k):
    ## чтение картиночки
    img_output = cv.imread(img_path)
    if img_output is not None:
        h = int(img_output.shape[0] * k)
        w = int(img_output.shape[1] * k)
        img_output = cv.resize(img_output, (w, h))
    else: img_output = 0
    ## чтение джсона
    with open(json_path, "r") as file:
        data = json.load(file)

    point_data = []
    for i in data[4]['kp-1']:
        point_data.append(i)


    points = np.array([
        [point_data[0]['x'] / 100 * w, point_data[0]['y'] / 100 * h],
        [point_data[1]['x'] / 100 * w, point_data[1]['y'] / 100 * h],
        [point_data[2]['x'] / 100 * w, point_data[2]['y'] / 100 * h],
        [point_data[3]['x'] / 100 * w, point_data[3]['y'] / 100 * h]
    ], dtype=np.float32)
    return img_output, points


### трансформация изображения
def image_transform(target, k, points):
    ## получение матрицы перспективы из разметки и точек назначения
    mat = cv.getPerspectiveTransform(points, destination_points*k)
    ## вывод нужного изображения
    return cv.warpPerspective(target, mat, (297*k, 210*k))

### конвертация изображения в чёрно-белый
def grayscale(image):
    result = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    _, result = cv.threshold(result, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)
    return result

def preprocess(img_path="0.png", k=2):
    ### создание путей
    json_dir = parent_dir / "json/json_main.json"
    pdf_dir = parent_dir / "pdfs/0.pdf"
    image_dir = parent_dir / "images"
    ## вычисление количества изображений
    num = sum(1 for i in image_dir.iterdir() if i.suffix.lower() == ".png")

    ## проверка и переделка пдфов
    if pdf_dir.exists():
        for i in range(0, sum(1 for i in (parent_dir/"pdfs").iterdir() if i.suffix.lower() == ".pdf")):
            pdf_dir = parent_dir / f"pdfs/{i}.pdf"
            pdf2png(pdf_dir)


    if num == 0:
        return []

    output_arr = []
    # программа
    for i in range(num):
        ### создание пути вывода
        output_dir = parent_dir / f"processed_images/{i}.tiff"
        img_dir = parent_dir / "images" / f"{i}.png"

        ### обработка изображения
        img, points = read(str(img_dir), str(json_dir), k)
        img = grayscale(img)
        img = image_transform(img, k, points)


        ### запись готового результата в файл
        cv.imwrite(output_dir, img)
        output_arr.append(str(output_dir))
        #cv.imshow("Result", img)
        #cv.waitKey(0)
    return output_arr

if __name__ == "__main__":
    preprocess()
