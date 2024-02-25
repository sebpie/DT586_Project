from flask import Flask
from flask import render_template

#initialize a flask object
app = Flask(__name__)


# API for serving webpages

#api for serving the index page
@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)