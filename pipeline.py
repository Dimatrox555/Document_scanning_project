import cv2

from OpenCV_proj.main import preprocess
from ocrnlp.progress_ocr import process_image


def run():
    image_paths = preprocess()

    results = []
    for path in image_paths:
        img = cv2.imread(path)
        result = process_image(img)
        results.append(result)

    return results


if __name__ == "__main__":
    output = run()
    for i, doc in enumerate(output):
        print(f"[{i}] {doc}")
