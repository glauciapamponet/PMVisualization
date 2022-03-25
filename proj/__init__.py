from flask import Flask
import webview

app = Flask(__name__, template_folder='templates')
window = webview.create_window('IC', app)

from proj.controllers import default

