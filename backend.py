from flask import Flask

# set up flask, add a public folder
app = Flask(__name__, static_folder='static', static_url_path='public')


# On start, read flat-file database/config file

@app.route("/")
def index():
    return ""


@app.route('/post/<str:zone>', methods=['GET'])
def fetchCurrent():
    """
    Get the current temperature reading, and setting
    """
    pass


@app.route('/post/<str:zone>/<float:temp>', methods=['GET'])
def getTemp():
    """
    POSTed value will be new setting
    """
    pass
