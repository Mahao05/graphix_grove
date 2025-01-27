from flask import Flask
import webbrowser
from flask_ngok import run_with_ngrok

app = Flask(__name__)
run_with_ngrok(app)

@app.route("/")
def hello_world():
    return "Hello, World!"

if __name__ == "__main__":
    webbrowser.open_new('http://127.0.0.1:5000/') 
    app.run()
