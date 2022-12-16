# pip install pyopenssl
# python main.py --keywords ../sample_data/keywords.txt --pdf_dir ../sample_data --output ../out 

from flask import Flask, send_from_directory, request
import base64
import os
from PIL import Image
from io import BytesIO
import argparse
from pdf_dao import Database
from pdf_utils import PdfUtils
import json

parser = argparse.ArgumentParser(description='PDF search with Hololens')
parser.add_argument('--pdf_dir', type=str, help='Pdf directory')
parser.add_argument('--keywords', type=str, help='Keywords file')
parser.add_argument('--output', type=str, help='Output directory')
parser.add_argument('--upload', type=str, help='Upload directory')

args = parser.parse_args()
print(args)

pdf_dir = args.pdf_dir if args.pdf_dir else "./"
keywords_file = args.keywords if args.keywords else "./keywords.txt"
out_dir = args.output if args.output else "./processed_pdfs"
upload_path = args.upload if args.upload else "./tmp"

with open(keywords_file, encoding = 'utf-8') as f:
    keywords = f.readlines()

# Create outdir if it doesn't exist
if not os.path.exists(out_dir):
    os.mkdir(out_dir)
if not os.path.exists(upload_path):
    os.makedirs(upload_path)

fs_pdfs = PdfUtils.list_pdfs(pdf_dir)

pdfs_out = {}
words_out = {}
for pdf in fs_pdfs.values():
    PdfUtils.extract_pdf_info(pdf, pdfs_out, words_out, keywords, out_dir)


# db_host = "cluster0.zwdtk.mongodb.net"
# db_user = "arvrlab"
# db_pasword = "q7u6OfZz8D50ZZa5"
# db = Database(db_user, db_pasword, db_host)
db = Database()
db.drop_db()

db.insert_many_pdfs(pdfs_out.values())
db.insert_many_keywords(words_out.values())

print(json.dumps(db.get_all_pdfs(), indent=4, sort_keys=True))
# print(json.dumps(db.get_all_keywords(), indent=4, sort_keys=True))


app = Flask(__name__)

from flask import request

@app.route('/pdfs')
def get_pdfs():
    keyword = request.args.get('keyword')
    if keyword is not None:
        try:
            return json.dumps(db.get_keyword(keyword))
        except Exception as e:
            print(e) 
            return "{}", 404
    else:
        try:
            return json.dumps(db.get_all_pdfs())
        except Exception as e:
            print(e) 

@app.route('/pdfs/<string:pdf>')
def get_pdf(pdf):
    try:
        return json.dumps(db.get_pdf(pdf))
    except Exception as e:
        print(e) 
        return "{}", 404

@app.route('/pdfs/<string:pdf>/<string:page>')
def get_page(pdf, page):
    return send_from_directory(f"{out_dir}/{pdf}", f"page-{page}.json")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port="443", ssl_context='adhoc')




# ######################## OCR ########################
# reader = easyocr.Reader(['en'])


# def millis():
#     return int(round(time_.time() * 1000))
    
# def convert(o):
#     if isinstance(o, np.generic): return o.item()
#     else: return o

# def ocr_file(file_path, filename):
#     results = reader.readtext(file_path, width_ths=0.1)
#     index = 0
#     out_obj = []
#     for obj in results:
#         position = obj[0]
#         word = obj[1].lower().translate(str.maketrans('', '', string.punctuation))
#         prob = obj[2]
#         if word not in keywords or prob < 0.6:
#             continue
#         img = cv2.imread(file_path)
#         top_left = tuple(position[0])
#         bottom_right = tuple(position[2])
#         cropped_image = img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
#         out_image = file_path + str(index) + ".jpg"
#         out_filename = "/imgs/" + filename + str(index) + ".jpg"
#         cv2.imwrite(out_image, cropped_image)
#         index += 1

#         out_obj.append({
#             "w" : word,
#             "src": out_filename
#         })
#     return out_obj


# ######################## Web server ########################

# # Test page upload
# @route('/')
# def root():
#     return static_file('./public/test_upload.html', root='.')

# @route('/imgs/<filename>')
# def serve_imgs(filename):
#     try:
#         return static_file(filename, root = upload_path)
#     except: 
#         print("/imgs/" + filename + " not found")

# @route('/upload', method='POST')
# def do_upload():
#     upload :FileUpload = request.files.get('snapshot')
#     name, ext = os.path.splitext(upload.filename)
#     # if ext not in ('.png', '.jpg', '.jpeg'):
#     #     return "File extension not allowed."

#     file = str(millis())
#     file_path = "{path}/{file}".format(path=upload_path, file=file)
#     upload.save(file_path)
#     result = ocr_file(file_path, file)
#     return json.dumps(result)