import json
import os
import string
import time as time_
from turtle import position
import numpy as np
import argparse
import easyocr
import cv2
from bottle import route, request, run, static_file, FileUpload
from pdf_dao import Database
from pdf_utils import PdfUtils

parser = argparse.ArgumentParser(description='PDF search with Hololens')
parser.add_argument('--pdf_dir', type=str, help='Pdf directory')
parser.add_argument('--keywords', type=str, help='Keywords file')

args = parser.parse_args()
print(args)

pdf_dir = args.pdf_dir if args.pdf_dir else "./"
keywords_file = args.keywords if args.keywords else "./keywords.txt"

with open(keywords_file, encoding = 'utf-8') as f:
    keywords = f.readlines()

out_dir = "./processed_pdfs"
upload_path = "./tmp"

db_host = "cluster0.zwdtk.mongodb.net"
db_user = "arvrlab"
db_pasword = "q7u6OfZz8D50ZZa5"


# Create outdir if it doesn't exist
if not os.path.exists(out_dir):
    os.mkdir(out_dir)
if not os.path.exists(upload_path):
    os.makedirs(upload_path)

pdfs = PdfUtils.list_pdfs(pdf_dir)

db = Database(db_user, db_pasword, db_host)
db.drop_db()

######################## Init DB ########################
# insert pdf into db
for pdf in pdfs.values():
    word_pages = PdfUtils.extract_pages(pdf, keywords, out_dir)
    # print(pdf)
    db.insert_pdf(pdf)
    for word in pdf["words"]:
        db.push_keyword(word, pdf["words"][word])

######################## OCR ########################
reader = easyocr.Reader(['en'])


def millis():
    return int(round(time_.time() * 1000))
    
def convert(o):
    if isinstance(o, np.generic): return o.item()
    else: return o

def ocr_file(file_path):
    results = reader.readtext(file_path, width_ths=0.1)
    index = 0
    out_obj = []
    for obj in results:
        position = obj[0]
        word = obj[1].lower().translate(str.maketrans('', '', string.punctuation))
        prob = obj[2]
        if word not in keywords or prob < 0.6:
            continue
        img = cv2.imread(file_path)
        top_left = tuple(position[0])
        bottom_right = tuple(position[2])
        print(top_left)
        print(bottom_right)
        cropped_image = img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        out_image = file_path + str(index) + ".jpg"
        cv2.imwrite(out_image, cropped_image)
        index += 1

        out_obj.append({
            "w" : word,
            "src": out_image
        })
    return out_obj


######################## Web server ########################

# Test page upload
@route('/')
def root():
    return static_file('./public/test_upload.html', root='.')

@route('/upload', method='POST')
def do_upload():
    upload :FileUpload = request.files.get('snapshot')
    name, ext = os.path.splitext(upload.filename)
    # if ext not in ('.png', '.jpg', '.jpeg'):
    #     return "File extension not allowed."

    file = millis()
    file_path = "{path}/{file}".format(path=upload_path, file=file)
    upload.save(file_path)
    result = ocr_file(file_path)
    return json.dumps(result)


@route('/pdfs')
def get_pdfs():
    if "keyword" in request.query:
        keyword = request.query['keyword']
        return json.dumps(list(db.get_keyword_page(keyword.lower())))
    else:
        return json.dumps(list(db.get_all_pdfs()))
    
@route('/pdfs/<dir>')
def get_pdf_pages(dir):
    try:
        pdf = db.get_pdf(dir)
        return json.dumps(list(pdf["pages"]))
    except Exception as e:
        print(e) 
        print(dir + " not found")

@route('/pdfs/<dir>/<filename>')
def serve_pdfs(dir, filename):
    print("serving " + dir + "/" + filename )
    try:
        return static_file(filename, root = out_dir + os.sep + dir)
    except: 
        print(dir + "/" + filename + " not found")


run(host='localhost', port=9090)