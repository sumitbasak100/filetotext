from flask import Flask, request, jsonify
import os
import requests
from PyPDF2 import PdfReader
from docx import Document

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert():
    if 'url' not in request.form:
        return jsonify(error="No URL provided"), 400

    url = request.form['url']

    text, error = extract_text_from_url(url)

    if error:
        return jsonify(error=error), 500
    else:
        return jsonify(text=text), 200

def extract_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        _, extension = os.path.splitext(url)
        extension = extension[1:].lower()  # Removes the dot and makes it lowercase

        if extension == 'pdf':
            reader = PdfReader(io.BytesIO(response.content))
            text = " ".join(page.extract_text() for page in reader.pages)
        elif extension == 'docx':
            doc = Document(io.BytesIO(response.content))
            text = " ".join(paragraph.text for paragraph in doc.paragraphs)
        elif extension == 'txt':
            text = response.text
        else:
            return None, "Unsupported filetype"

        return text, None
    except Exception as e:
        return None, str(e)

