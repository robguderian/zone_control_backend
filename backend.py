import json
from threading import Timer

from flask import Flask

# set up flask, add a public folder
app = Flask(__name__, static_folder='public', static_url_path='')


def get_current_temp(devname):
    """
    Get the current temperature at device
    """
    # TODO
    return 22.2

class Controller:
    """
    Config file handling
    - the config file is json
    - config file is [{zone:xxx, setting:yyy, device:/dev/zzz}]
    """
    def __init__(self, filename):
        self.filename = filename
        with open(filename) as f:
            self.config = json.load(f)

    def getConfig(self, zonename):
        for z in self.config:
            if z.zonename == zonename:
                return z.setting

    def setConfig(self, zonename, newSetting):
        for z in self.config:
            if z.zonename == zonename:
                z.setting = newSetting
        # TODO re-write json

    def getAllJSON(self):
        output = []
        for z in self.config:
            output.append({"zone": z["zone"],
                           "setting": z["setting"],
                           "current": get_current_temp(z["device"])})
        return json.dumps(output)

def check_set_valves():
    """
    Check temperature of floors, set valves open or closed
    """
    print("Checking valves")
    scheduler = Timer(TIMER_TIME, check_set_valves)
    scheduler.start()


# On start, read flat-file database/config file
tempController = Controller("config.json")

# start a scheduled task
# this task checks current temperatures, sets valve appropriately
print("setting initial timer")
TIMER_TIME = 2 * 60 # 2 minutes of 60 seconds
scheduler = Timer(TIMER_TIME, check_set_valves)
scheduler.start()


@app.route("/")
def index():
    return ""

@app.route('/zones', methods=['GET'])
def fetchAllCurrent():
    """
    Get the setting and current temperature of all the things
    """
    return tempController.getAllJSON()

@app.route('/zones/<zone>', methods=['GET'])
def fetchCurrent():
    """
    Get the current temperature reading, and setting
    Single zone
    """
    pass


@app.route('/zones/<zone>/<float:temp>', methods=['GET'])
def getTemp():
    """
    POSTed value will be new setting
    """
    pass
