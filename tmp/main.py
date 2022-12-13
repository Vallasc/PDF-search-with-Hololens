# pip install pyopenssl
from flask import Flask
import base64
from PIL import Image
from io import BytesIO

app = Flask(__name__)
filepath = "../sample_data/page.jpg"

@app.route("/pdf")
def pdf():
    out = "{}"
    with Image.open(filepath) as img:
        width, height = img.size
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue())
        out = { "img": img_str.decode("utf-8") , "width": width, "height": height}
    return out

if __name__ == "__main__":
    app.run(host='0.0.0.0', port="443", ssl_context='adhoc')