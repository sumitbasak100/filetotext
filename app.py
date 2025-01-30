from flask import Flask, request, jsonify
import os
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from docx import Document
from pptx import Presentation
from PIL import Image
import pytesseract
import io

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert():
    if 'url' not in request.form:
        return jsonify(error="No URL provided"), 400

    url = request.form['url']

    if url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        text, error = extract_text_from_image(url)
    else:
        text, error = extract_text_from_url(url)

    if error:
        return jsonify(error=error), 500
    else:
        return jsonify(text=text), 200

@app.route('/url-text-extract', methods=['POST'])
def url_text_extract():
    if 'url' not in request.form:
        return jsonify(error="No URL provided"), 400

    url = request.form['url']

    text, error = extract_text_from_webpage(url)

    if error:
        return jsonify(error=error), 500
    else:
        return jsonify(text=text), 200

# New route to search for sober living homes using Google Places API
@app.route('/search-sober-living', methods=['GET'])
def search_sober_living():
    # Get pincode from the query parameters
    pincode = request.args.get('pincode')
    if not pincode:
        return jsonify(error="No pincode provided"), 400

    # Google Places API URL
    url = f'https://maps.googleapis.com/maps/api/place/textsearch/json?query=sober+living+homes+in+{pincode}&key=AIzaSyAyKWwY9UbPrt4v-7DOQ9jqvC8V2512CTM'

    try:
        # Make the API request to Google Places
        response = requests.get(url)
        data = response.json()

        if data['status'] == 'OK':
            # Return the results from the Google Places API
            return jsonify(results=data['results']), 200
        else:
            return jsonify(error="Failed to fetch data from Google Places API"), 500
    except Exception as e:
        return jsonify(error=str(e)), 500

def extract_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        _, extension = os.path.splitext(url)
        extension = extension[1:].lower()  # Removes the dot and makes it lowercase

        if extension in ['pdf', 'docx', 'txt']:
            if extension == 'pdf':
                reader = PdfReader(io.BytesIO(response.content))
                text = " ".join(page.extract_text() for page in reader.pages)
            elif extension == 'docx':
                doc = Document(io.BytesIO(response.content))
                text = " ".join(paragraph.text for paragraph in doc.paragraphs)
            elif extension == 'txt':
                text = response.text
        elif extension == 'pptx':
            prs = Presentation(io.BytesIO(response.content))
            text = ''
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text += shape.text + '\n'
        else:
            return None, "Unsupported filetype"

        return text, None
    except Exception as e:
        return None, str(e)

def extract_text_from_webpage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract text from all <p> tags
        text = '\n'.join(p.get_text() for p in soup.find_all('p'))

        return text, None
    except Exception as e:
        return None, str(e)

def extract_text_from_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        image = Image.open(io.BytesIO(response.content))
        text = pytesseract.image_to_string(image)

        return text, None
    except Exception as e:
        return None, str(e)

if __name__ == "__main__":
    app.run(debug=True)
