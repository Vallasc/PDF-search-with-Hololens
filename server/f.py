from flask import Flask

app = Flask(__name__)

@app.route("/upload",  methods = ['GET', 'POST'])
def hello_world():
    print("Ciao")
    return "<p>Hello, World!</p>"


if __name__ == '__main__':
      app.run(host='0.0.0.0', port=9999, ssl_context='adhoc')