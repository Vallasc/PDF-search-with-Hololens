import sys
import json
import os

from bottle import route, request, run, static_file
from pdf_dao import Database
from pdf_utils import PdfUtils

pdf_dir = sys.argv[1] if len(sys.argv) > 1 else "./"
keywords_file = sys.argv[1] if len(sys.argv) > 2 else "./keywords.txt"

destination = "pdfs"

if not os.path.exists(destination):
    os.mkdir(destination)

pdfs = PdfUtils.list_pdfs(pdf_dir)

user = "root"
pasword = "arvrlab"
db = Database(user, pasword)
db.drop_db()

# insert pdf into db
for pdf in pdfs.values():
    word_pages = PdfUtils.extract_pages(pdf, destination)
    # print(pdf)
    db.insert_pdf(pdf)
    for word in pdf["words"]:
        db.push_keyword(word, pdf["words"][word])


# Web server
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
        return static_file(filename, root = destination + os.sep + dir)
    except: 
        print(dir + "/" + filename + " not found")


run(host='localhost', port=9090)


# todo pulire hello,