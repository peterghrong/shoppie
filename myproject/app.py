from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello():
    return "home page"


@app.route('/about')
def hello():
    return "Shopify summer 2021 internship app"


@app.route('/search/<string:text>')
def search_by_text():
    pass


@app.route('/search/<string:characteristic>')
def search_by_chararcteristics():
    pass


@TODO: this needs to be implemented
@app.route('/search/<string:image>')
def search_by_image():
    pass


@app.route('/post')
def add_image():
    return "posting test"


if __name__ == "__main__":
    app.run()
