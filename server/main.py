import pymongo
import pdfminer

print("Ciao")
print(pdfminer.__version__)  
username = "root"
password = "arvrlab"
mongo_client = pymongo.MongoClient('mongodb://%s:%s@127.0.0.1:27017' % (username, password))
db = mongo_client["ARdatabase"]
collection = db["pdfs"]

mydict = { "name": "John" }

x = collection.insert_one(mydict)