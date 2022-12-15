# pip install pyopenssl
# 
from flask import Flask
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

db_host = "cluster0.zwdtk.mongodb.net"
db_user = "arvrlab"
db_pasword = "q7u6OfZz8D50ZZa5"


# Create outdir if it doesn't exist
if not os.path.exists(out_dir):
    os.mkdir(out_dir)
if not os.path.exists(upload_path):
    os.makedirs(upload_path)

pdfs = PdfUtils.list_pdfs(pdf_dir)
print(pdfs)
print()

pdfs_out = {}
words_out = {}
for pdf in pdfs.values():
    PdfUtils.extract_pdf_info(pdf, pdfs_out, words_out, keywords, out_dir)

print(json.dumps(pdfs_out, indent=4, sort_keys=True))
print(json.dumps(words_out, indent=4, sort_keys=True))

# db = Database(db_user, db_pasword, db_host)
# db.drop_db()


# @app.route("/pdf")
# def pdf():
#     out = "{}"
#     with Image.open(filepath) as img:
#         width, height = img.size
#         buffered = BytesIO()
#         img.save(buffered, format="JPEG")
#         img_str = base64.b64encode(buffered.getvalue())
#         out = { "img": img_str.decode("utf-8") , "width": width, "height": height}
#     return out

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port="443", ssl_context='adhoc')