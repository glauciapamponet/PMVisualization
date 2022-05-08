from flask import Flask
import webview
from tkinter import *

root = Tk()

screen_h = root.winfo_screenheight()
screen_w = root.winfo_screenwidth()

app = Flask(__name__, template_folder='templates')
window = webview.create_window('IC', app, width=screen_w, height=screen_h, min_size=(1200, 100))

from proj.controllers import default

