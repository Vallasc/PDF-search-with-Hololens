# pip install pyopenssl
# pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116
# python main.py --keywords ../sample_data/keywords.txt --pdf_dir ../sample_data --output ../out 

import traceback
from flask import Flask, send_from_directory, request
import os
import argparse
from pdf_dao import Database
from pdf_utils import PdfUtils
import json
from copy import deepcopy

parser = argparse.ArgumentParser(description='PDF search with Hololens file server')
parser.add_argument('--pdf_dir', default="./", type=str, help='Pdf directory')
parser.add_argument('--keywords', default="./keywords.txt", type=str, help='Keywords file')
parser.add_argument('--output', default="./processed", type=str, help='Output directory')
parser.add_argument('--tmp', default="./tmp", type=str, help='Tmp directory')
args = parser.parse_args()


with open(args.keywords, encoding = 'utf-8') as f: 
    keywords = PdfUtils.sanitize_word(f.read()).splitlines()

# Create outdir if it doesn't exist
if not os.path.exists(args.output):
    os.mkdir(args.output)
if not os.path.exists(args.tmp):
    os.makedirs(args.tmp)

fs_pdfs = PdfUtils.list_pdfs(args.pdf_dir)

pdfs_out = {}
words_out = {}

for pdf in fs_pdfs.values():
    PdfUtils.extract_pdf_info(pdf, pdfs_out, words_out, keywords, args.output)

db = Database()
db.drop_db()

db.insert_many_pdfs(pdfs_out.values())
db.insert_many_keywords(words_out.values())

print(json.dumps(db.get_all_pdfs(), indent=4, sort_keys=True))
print(json.dumps(db.get_all_keywords(), indent=4, sort_keys=True))


app = Flask(__name__)

@app.route('/pdfs')
def get_pdfs():
    keyword = request.args.get('keyword')
    fav = request.args.get('favFilter') is not None 
    moreOcc = request.args.get('moreOcc') is not None
    mostView = request.args.get('mostViewed') is not None
    limit = 30 if request.args.get('limit') is None else request.args.get('limit')
    if keyword is not None:
        keyword = PdfUtils.sanitize_word(keyword)
        result_pdfs = db.get_keyword(keyword)["pdfs"].values()
    else:
        result_pdfs = db.get_all_pdfs()
    try:
        out_pdfs = PdfUtils.hydratate_pdfs(result_pdfs, db)
        if moreOcc:
            out_pdfs.sort( lambda e : e["numOccKeyword"])
        elif mostView:
            out_pdfs.sort( lambda e : e["numVisit"])
        if fav:
            out_pdfs = filter(out_pdfs, lambda e : e["isFav"] == True)
        out_pdfs = out_pdfs[0:limit]
        print(out_pdfs)
        return {
            'pdfs': out_pdfs
        }, 200
    except Exception as e:
        traceback.print_exc()
        return "{}", 404
        

@app.route('/pdfs/<string:pdf>')
def get_pdf(pdf):
    visit = request.args.get('visit')
    if visit is not None:
        _pdf = db.get_pdf(pdf)
        _pdf["numVisit"] += 1
        db.update_pdf(_pdf)
    try:
        return json.dumps(db.get_pdf(pdf))
    except Exception as e:
        print(e) 
        return "{}", 404

@app.route('/pdfs/<string:pdf>/<string:page>')
def get_page(pdf, page):
    keyword = request.args.get('keyword')
    if keyword is not None:
        keyword = PdfUtils.sanitize_word(keyword)
        k_db = db.get_keyword(keyword)
        filtered = [p for p in k_db['pdfs'][pdf]['pages'] if p["number"] == int(page)]
        if len(filtered) == 1: 
            return PdfUtils.select_keyword_on_image(filtered[0])
        else:
            return "{}", 404 
    else:
        return send_from_directory(f"{args.output}/{pdf}", f"page-{page}.json")


@app.route('/favs/<string:pdf>', methods = ['POST'])
def post_favourites(pdf):
    value = request.form['value']
    if value is not None:
        try:
            _pdf = db.get_pdf(pdf)
            _pdf["isFav"] = bool(value)
            db.update_pdf(_pdf)
            return "{}", 200
        except Exception as e:
            print(e) 
            return "{}", 404
    return "{}", 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8573, ssl_context='adhoc')