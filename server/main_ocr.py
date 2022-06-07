import easyocr
import os
import json
import time as time_
import numpy as np

from bottle import route, request, run, static_file, FileUpload
from bottle import ServerAdapter

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

class SSLCherootAdapter(ServerAdapter):
    def run(self, handler):
        from cheroot import wsgi
        from cheroot.ssl.builtin import BuiltinSSLAdapter
        import ssl

        server = wsgi.Server((self.host, self.port), handler)
        server.ssl_adapter = BuiltinSSLAdapter("cacert.pem", "privkey.pem")

        # By default, the server will allow negotiations with extremely old protocols
        # that are susceptible to attacks, so we only allow TLSv1.2
        server.ssl_adapter.context.options |= ssl.OP_NO_TLSv1
        server.ssl_adapter.context.options |= ssl.OP_NO_TLSv1_1

        try:
            server.start()
        finally:
            server.stop()

if __name__ == '__main__':
    run(host='0.0.0.0', port=9999, server=SSLCherootAdapter)