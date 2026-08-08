from flask import Flask, render_template, request, send_file
import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter

app = Flask(__name__)

@app.route('/')
def index():
    return "PDF Pro+ is Live and Running Successfully!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
