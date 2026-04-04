import cv2 as cv
def preprocess_local(img_path):
    img = cv.imread(img_path, cv.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"файл не найден: {img_path}")
    img = cv.resize(img, None, fx=2, fy=2, interpolation=cv.INTER_CUBIC)
    _, img = cv.threshold(img, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    return img