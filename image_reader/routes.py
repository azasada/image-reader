from flask import json, render_template, send_from_directory, url_for, request, jsonify
from image_reader import app
import io

from PIL import Image
import pytesseract
import datetime
import pypandoc
import os
import cv2

# import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from scipy.signal import savgol_filter
from werkzeug.utils import secure_filename

from .spellcheck import spellcheck


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    images = request.files.getlist("file")
    lang = request.form["lang"]
    read_text = ""

    crop_flag = request.values.get("crop") == "on"
    spellcheck_flag = request.values.get("spellcheck") == "on"

    for image in images:
        image_data = image.read()
        filename = "/tmp/tmp." + image.filename[image.filename.index(".") + 1 :]
        image.stream.seek(0)
        image.save(filename)
        if crop_flag:
            cropping(filename)
        image_data = cv2.imread(filename, cv2.IMREAD_COLOR)

        text_chunk = pytesseract.image_to_string(image_data, lang=lang, config="--psm 6")
        if spellcheck_flag:
            text_chunk = spellcheck(text_chunk, lang)

        read_text += text_chunk
        read_text += "\n<br>\n"
    pypandoc.convert_text(
        read_text,
        "pdf",
        format="md",
        outputfile="/tmp/text.pdf",
    )

    return jsonify(text=f"{read_text.replace("<br>", "")}")


@app.route("/download", methods=["POST"])
def download_pdf():
    return send_from_directory("/tmp", "text.pdf", as_attachment=False)


def cropping(filename):

    # fig, ax = plt.subplots(7, 1, figsize=(30, 30))

    grayscale_img = cv2.imread(filename, 0)
    kernel = np.ones((9, 9), np.uint8)
    img_erosion = cv2.erode(grayscale_img, kernel, iterations=5)
    _, thresh1 = cv2.threshold(img_erosion, 100, 255, cv2.THRESH_BINARY_INV)

    horizontally = np.sum(thresh1 == 255, axis=0)
    vertically = np.sum(thresh1 == 255, axis=1)

    rot_flag = 0
    if len(horizontally) > len(vertically):
        horizontally, vertically, rot_flag = vertically, horizontally, 1

    smoothed_h = savgol_filter(horizontally, 50, 5)
    smoothed_v = savgol_filter(vertically, 50, 5)

    h = [0, len(smoothed_h) - 1]
    thresh_h = 200
    flag = 0

    for i in range(0, int(len(smoothed_h) / 3), 1):
        if smoothed_h[i] < thresh_h and flag == 0:
            flag = 1
        elif smoothed_h[i] > thresh_h and flag == 1:
            h[0] = i
            flag = 0
            break

    for i in range(len(smoothed_h) - 1, int(len(smoothed_h) * 2 / 3), -1):
        if smoothed_h[i] < thresh_h and flag == 0:
            flag = 1
        elif smoothed_h[i] > thresh_h and flag == 1:
            h[1] = i
            break

    # print(h)

    # ax[0].imshow(grayscale_img, cmap='gray')
    # ax[1].imshow(img_erosion, cmap='gray')
    # ax[2].imshow(thresh1, cmap='binary')
    # ax[3].plot(horizontally)
    # ax[4].plot(smoothed_h)
    # ax[5].plot(vertically)
    # ax[6].plot(smoothed_v)
    # plt.show()

    img = cv2.imread(filename)
    if rot_flag:
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

    if h[0] > 10:
        h[0] -= 10

    if h[1] < len(smoothed_h) - 11:
        h[1] += 10

    cropped_image = img[:, h[0] : h[1]]

    cv2.imwrite(filename, cropped_image)
