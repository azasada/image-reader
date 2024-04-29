from flask import json, render_template, send_from_directory, url_for, request, jsonify
from image_reader import app
import io

from PIL import Image
import pytesseract
import datetime
import pypandoc
import os


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    images = request.files.getlist("file")
    lang = request.form["lang"]
    read_text = ""
    for image in images:
        image_data = image.read()
        read_text += pytesseract.image_to_string(
            Image.open(io.BytesIO(image_data)), lang=lang
        )
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
    print("hello")
    return send_from_directory("/tmp", "text.pdf", as_attachment=False)
