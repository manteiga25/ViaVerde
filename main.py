import cv2 as cv
from queue import Queue
from threading import Thread

from fast_plate_ocr import LicensePlateRecognizer

from ultralytics import YOLO

from database.Schema import Database

from datetime import datetime

def showImage(image):
    cv.imshow("Image", image)
    cv.waitKey(0)
    cv.destroyAllWindows()

def preprocessImage(image):
    resized_image = cv.resize(image, (640, 640), interpolation=cv.INTER_CUBIC)

    # Convert the image from BGR to RGB format
    rgb_image = cv.cvtColor(resized_image, cv.COLOR_BGR2RGB)

    return rgb_image

def process_object(binary, x, y, w, h):
    x_buffer = 5 if x > 5 else 0
    w_buffer = 5 if w > 5 else 0
    y_buffer = 5 if y > 5 else 0
    h_buffer = 5 if h > 5 else 0
    roi = binary[y - y_buffer:y + h + h_buffer, x - x_buffer:x + w + w_buffer]
    resized = cv.resize(roi, (960, 480), interpolation=cv.INTER_CUBIC)
    return resized

def findCarRegistration(image):
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    _, binary = cv.threshold(image, 127, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)

    contours, _ = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    text_readed = []

    for contour in contours:
        x, y, w, h = cv.boundingRect(contour)

        if w > 10 and h > 10: # if the size of the contour is big enough
            resized = process_object(image, x, y, w, h)
            resized = cv.cvtColor(resized, cv.COLOR_BGR2RGB)

            pred = ocr.run(resized)[0]

            if len(pred.plate) <= 9:
                text_readed.append(pred.plate)

    max_text = max(text_readed, key=len) if text_readed else None

    return max_text

image_queue = Queue()

db = Database()

ocr = LicensePlateRecognizer('cct-s-v2-global-model', device='cuda')

model = YOLO("yolo26n.pt")

names = list(model.names.values())  # get class names

path = ""

def process(image):
    data_pass = datetime.now()
    date_pass_formated_years = data_pass.strftime("%H-%M-%S_%d-%m-%Y")
    date_pass_formated = data_pass.strftime("%H:%M:%S")

    results = model(image)
    if len(results) == 0:
        return
    for result in results:

        if len(result.boxes.cls.int()) == 0:
            continue

        if names[result.boxes.cls.int()[0]] == "car":
            xyxy = result.boxes.xyxy
            result = findCarRegistration(
                image[int(xyxy[0][1]):int(xyxy[0][3]), int(xyxy[0][0]):int(xyxy[0][2])])

            passage_id = db.insertPassagem(result, date_pass_formated)
            if result is not None and len(result) == 9:
                if not db.checkCar(result):
                    db.insertMulta(passage_id, result, 10.00, False)
            else:
                path = f"carros_nao_lidos/{date_pass_formated_years}.png"
                cv.imwrite(path, image)
                db.insertCarroNaoLido(path, passage_id)

def image_handler():
    while True:
        image = image_queue.get()
        if image is not None:
            Thread(target=process, args=(image,), daemon=True).start()

if __name__ == "__main__":
    from time import sleep
    from os import makedirs

    makedirs("carros_nao_lidos", exist_ok=True)

    sensor_tick = 10 # simulate a sensor ticky car detection are every 10 seconds

    Thread(target=image_handler, daemon=True).start()

    while True:
        mat = cv.imread(path)

        image_queue.put_nowait(mat)

        sleep(sensor_tick)