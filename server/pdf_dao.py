# Pdf = {
#   _id: string
#   name: string
#   path: string
#   numPages: number
#   pages: list<Page>
#   isFav: bool
#   numVisit: number
# }
# Page = {
#   number: int
#   pdfId: string
#   path: string        // Local file system path
#   url: string         // Page image url
#   base64Thumbnail: string
# }
# PageImage = {
#   img: string
#   thumbnail: string
#   width: int
#   height: int
# }


# Keyword = {
#   _id: string
#   word: string
#   pdfs: dict<pdfId, PdfKeyword>
# }
# PdfKeyword = {
#   _id: string
#   name: string
#   path: string
#   numOccKeyword: number
#   pages: list<PageKeyword>
# }
# PageKeyword = {
#     number: int
#     pdfId: string
#     path: string
#     url: string
#     keywords: list<Word>
# }
# Word = {
#   x0: flaot
#   y0: flaot
#   x1: flaot
#   y1: flaot
#   word: string
# }


import pymongo
import os
import json

class Database:
    db_path = "./pdf_search.db"
    def __init__(self, username, password, host = "127.0.0.1"):
        if host == "127.0.0.1" or host == "localhost":
            self._mongo_client = pymongo.MongoClient('mongodb://%s:%s@%s:27017' % (username, password, host))
        else:
            self._mongo_client = pymongo.MongoClient('mongodb+srv://%s:%s@%s/?retryWrites=true&w=majority' % (username, password, host))
        self._db = self._mongo_client["ARdatabase"]
        # self._db["pdfs"].create_index('name')
        self._db_type = "mongo"

    def __init__(self):
        self._db_type = "file"
        if os.path.exists(self.db_path):
            with open(self.db_path, 'rb') as fp:
                self._db_file = json.load(fp)
        else:
            self._db_file =  { "pdfs": {},  "keywords": {}}

    def close(self):
        with open(self.db_path, 'w') as fp:
            json.dump(self._db_file, fp)

        
    def drop_db(self):
        if self._db_type == "mongo":
            self._db["pdfs"].drop()
            self._db["keywords"].drop()
        else:
            self._db_file =  { "pdfs": {},  "keywords": {}}
            

    def insert_one_pdf(self, pdf):
        if self._db_type == "mongo":
            pdfs = self._db["pdfs"]
            try:
                pdfs.insert_one(pdf)
            except:
                print("Error inserting pdf " + pdf["name"])
        else:
            self._db_file["pdfs"][pdf["_id"]] = pdf

    def insert_many_pdfs(self, pdfs):
        if self._db_type == "mongo":
            pdfs = self._db["pdfs"]
            try:
                pdfs.insert_many(pdfs)
            except:
                print("Error inserting pdfs")
        else:
            for pdf in pdfs:
                if pdf["_id"] not in self._db_file["pdfs"]:
                    self._db_file["pdfs"][pdf["_id"]] = pdf

    def get_pdf(self, id):
        if self._db_type == "mongo":
            collection = self._db["pdfs"]
            return collection.find_one({'_id': id})
        else:
            return self._db_file["pdfs"][id]
        
    def update_pdf(self, pdf):
        if self._db_type == "mongo":
            newPdfValues = { "$set": { "isFav": pdf["isFav"], "numVisit": pdf["numVisit"]  } }
            query = { "_id": pdf["_id"] }
            collection = self._db["pdfs"]
            return collection.update_one(query, newPdfValues)
        else:
            self._db_file["pdfs"][pdf["_id"]]["isFav"] = pdf["isFav"]
            self._db_file["pdfs"][pdf["_id"]]["numVisit"] = pdf["numVisit"]
            return True

    def get_all_pdfs(self):
        if self._db_type == "mongo":
            collection = self._db["pdfs"]
            return list(collection.find({}))
        else:
            return list(self._db_file["pdfs"].values())


    def insert_many_keywords(self, keywords):
        if self._db_type == "mongo":
            collection = self._db["keywords"]
            try:
                collection.insert_many(keywords)
            except Exception as e:
                print(e)
        else:
            for keyword in keywords:
                if keyword["_id"] not in self._db_file["keywords"]:
                    self._db_file["keywords"][keyword["_id"]] = keyword
                self._db_file["keywords"][keyword["_id"]] = keyword

    def get_keyword(self, keyword_id):
        if self._db_type == "mongo":
            collection = self._db["keywords"]
            return collection.find_one({'_id': keyword_id})
        else:
            return self._db_file["keywords"][keyword_id]

    def get_all_keywords(self):
        if self._db_type == "mongo":
            collection = self._db["keywords"]
            return list(collection.find({}))
        else:
            return list(self._db_file["keywords"].values())
