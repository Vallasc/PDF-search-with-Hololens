# Pdf = {
#   _id: string
#   name: string
#   pages: list<Page>
#   words: dict<string, list<WordPage>>
# }

# Page = {
#   number: int
#   pdfId: string
#   path: string
#   url: string
# }

# Word = {
#   x0: flaot
#   y0: flaot
#   x1: flaot
#   y1: flaot
#   word: string
# }

# WordPage = {
#   word: Word
#   page: Page
# }

# TODO
# Keyword = {
#   _id: string
#   word: string
#   pages: set<Page>
# }

# Favorites = {
#   _id: string
#   pdf_id: string
# }

# LastSeen = {
#   _id: string
#   pdf_id: string
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
        self._db["pdfs"].create_index('name')
        self._db_type = "mongo"

    def __init__(self):
        self._db_type = "file"
        if os.path.exists(db_path):
            with open(db_path, 'rb') as fp:
                self._db_file = json.load(fp)
        else:
            self._db_file =  []

    def close(self):
        f = open(db_path)
            self._db_file = json.load(f)
        with open(db_path, 'w') as fp:
            json.dump(self._db_file, fp)

        
    def drop_db(self):
        if self._db_type == "mongo":
            self._db["pdfs"].drop()
            self._db["keywords"].drop()
        else:


    def insert_pdf(self, pdf):
        pdf["_id"] = pdf["name"]
        collection = self._db["pdfs"]
        try:
            collection.insert_one(pdf)
        except:
            print("Error inserting pdf " + pdf["name"])

    def get_pdf(self, name):
        collection = self._db["pdfs"]
        return collection.find_one({'_id': name})

    def get_all_pdfs(self):
        collection = self._db["pdfs"]
        return collection.find({})

    def push_keyword(self, word, pages):
        collection = self._db["keywords"]
        _id = word
        try:
            collection.update_one({'_id': _id}, {'$push': {'pages': {'$each': pages}}, 
                                                '$set': {'word': word, '_id': _id}}, upsert = True)
        except Exception as e:
            print(e)

    def get_keyword_page(self, word):
        collection = self._db["keywords"]
        _id = word
        try:
            return collection.find({'_id': _id})
        except Exception as e:
            print(e)