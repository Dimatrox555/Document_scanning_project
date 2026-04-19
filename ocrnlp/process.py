from ocrnlp.progress_ocr import process_image


def mass(arr):
    """Batch wrapper around process_image for a list of inputs."""
    t = []
    for i in arr:
        t.append(process_image(i))
    print(t)


if __name__ == "__main__":
    # Example single-run entry point (adjust path as needed)
    result = process_image()
    print(result)
