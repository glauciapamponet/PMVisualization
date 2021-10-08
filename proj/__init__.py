from flask import Flask


app = Flask(__name__)

from proj.controllers import default

