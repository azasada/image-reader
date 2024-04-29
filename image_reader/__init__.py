from flask import Flask

app = Flask(__name__)

from image_reader import routes
