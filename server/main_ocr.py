import easyocr

from bottle import route, request, run, static_file

IMAGE_PATH = 'https://blog.aspose.com/wp-content/uploads/sites/2/2020/05/Perform-OCR-using-C.jpg'
reader = easyocr.Reader(['en'])
result = reader.readtext(IMAGE_PATH)
result