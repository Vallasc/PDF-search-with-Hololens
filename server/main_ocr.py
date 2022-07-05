import easyocr
import os
import json
import time as time_
import numpy as np

from bottle import route, request, run, static_file, FileUpload

reader = easyocr.Reader(['en'])


def millis():
    return int(round(time_.time() * 1000))
    
def convert(o):
    if isinstance(o, np.generic): return o.item()  
    else: return o

@route('/')
def root():
    return static_file('./public/test_upload.html', root='.')


@route('/upload', method='POST')
def do_upload():
    upload :FileUpload = request.files.get('snapshot')
    name, ext = os.path.splitext(upload.filename)
    # if ext not in ('.png', '.jpg', '.jpeg'):
    #     return "File extension not allowed."

    save_path = "./tmp"
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    file_path = "{path}/{file}".format(path=save_path, file=millis())
    upload.save(file_path)
    result = reader.readtext(file_path)
    return json.dumps(result, default=convert)

if __name__ == '__main__':
    run(host='0.0.0.0', port=9999)