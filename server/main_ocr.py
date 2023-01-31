# pip install pyopenssl
# python main_ocr.py --keywords ../sample_data/keywords.txt --gpu

import easyocr
import argparse
import os
from PIL import Image
from io import BytesIO
import base64
from pdf_utils import PdfUtils
from flask import Flask, send_from_directory, request
import editdistance

parser = argparse.ArgumentParser(description='PDF search with Hololens OCR server')
parser.add_argument('--keywords', default="./keywords.txt", type=str, help='Keywords file')
parser.add_argument('--tmp', default="./tmp", type=str, help='Tmp directory')
parser.add_argument('--gpu', default=False, action=argparse.BooleanOptionalAction, help='Enable GPU acceleration')

args = parser.parse_args()
reader = easyocr.Reader(['en', 'it'], gpu=args.gpu)

with open(args.keywords, encoding = 'utf-8') as f: 
    keywords = PdfUtils.sanitize_word(f.read()).splitlines()

if not os.path.exists(args.tmp):
    os.makedirs(args.tmp)

app = Flask(__name__)

@app.route('/test')
def get_page():
    return send_from_directory('./public', 'test_upload.html')

image_counter = 0
@app.route('/upload', methods = ['POST'])
def do_upload():
    global image_counter
    base64_img = request.form['snapshot']
    img_bytes = BytesIO(base64.b64decode(base64_img))
    # img_bytes = BytesIO()
    with Image.open(img_bytes) as image:
    #     image.thumbnail((800, 800))
        img_path = f"{image_counter}.png"
        image.save(os.path.join(args.tmp, img_path))
        image_counter += 1

    result = reader.readtext(img_bytes.getvalue())
    out_keywords = []
    for word in result:
        sanitized = PdfUtils.sanitize_word(word[1])
        for keyword in keywords:
            dist = editdistance.eval(sanitized, keyword)
            if dist < 3 and word[2] > 0.6 and keyword not in out_keywords:
                out_keywords.append(keyword)
    print(out_keywords)
    return {
        'keywords': out_keywords,
        'request_index': request.form['request_index']
    }, 200

@app.route('/test_upload', methods = ['POST'])
def do_test_upload():
    return {
        'keywords': ['nice', 'try'],
        'request_index': request.form['request_index']
    }, 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8574, ssl_context='adhoc')