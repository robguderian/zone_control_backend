import json
from threading import Timer
import re

from flask import Flask, Response

# set up flask, add a public folder
app = Flask(__name__, static_folder='public', static_url_path='', host='0.0.0.0')
TIMER_TIME = 2 * 60 # 2 minutes of 60 seconds
TOLERANCE = 0.5 # degrees Celsius

def get_current_temp(devname):
    """
    Get the current temperature at device
    """
    # TODO
    # needs to match
    #51 01 4b 46 7f ff 0c 10 ab : crc=ab YES\n51 01 4b 46 7f ff 0c 10 ab t=21062\n
    m = re.search("\st=(\d+)\n", open(devname).read())

    return int(m.group(1))

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

    def getZone(self, zonename):
        for z in self.config:
            if z['zone'].lower() == zonename.lower():
                return z

    def getConfig(self, zonename):
        print(self.config)
        z = self.getZone(zonename)
        if z is not None:
            return z['setting']
        return -1

    def getCurrentTemp(self, zonename):
        z = self.getZone(zonename)
        if z is not None:
            return get_current_temp(z["device"])
        return -1

    def getCurrentAndSetting(self, zonename):
        z = self.getZone(zonename)
        if z is not None:
            return (get_current_temp(z["device"]), z['setting'])
        return (-1, -1)


    def setConfig(self, zonename, newSetting):
        z = self.getZone(zonename)
        if z is not None:
            z['setting'] = newSetting

        with open(self.filename, 'w') as f:
            json.dump(self.config, f)

    def getAllJSON(self):
        output = []
        for z in self.config:
            output.append({"zone": z["zone"],
                           "setting": z["setting"],
                           "current": get_current_temp(z["device"])})
        return json.dumps(output)

    def check_all(self):
        for z in self.config:
            actual = get_current_temp(z['device'])
            
            if actual - z['setting'] >= TOLERANCE: # Check high-limit. Turn off if > high limit
                pass
            elif z['setting'] - actual <= TOLERANCE: # check low-limit, turn on if too cold
                pass

def check_set_valves():
    """
    Check temperature of floors, set valves open or closed
    """
    print("Checking valves")
    tempController.check_all()
    scheduler = Timer(TIMER_TIME, check_set_valves)
    scheduler.start()


# On start, read flat-file database/config file
tempController = Controller("config.json")

# start a scheduled task
# this task checks current temperatures, sets valve appropriately
print("setting initial timer")
check_set_valves()

@app.route('/zones', methods=['GET'])
def fetchAllCurrent():
    """
    Get the setting and current temperature of all the things
    """
    return tempController.getAllJSON()

@app.route('/zones/<zone>', methods=['GET'])
def fetchCurrent(zone):
    """
    Get the current temperature reading, and setting
    Single zone
    """
    currentTemp = (tempController.getCurrentAndSetting(zone))
    data = json.dumps( {"current":currentTemp[0], "setting":currentTemp[1]})
    return Response(data, status=200, mimetype='application/json')



@app.route('/zones/<zone>/<temp>', methods=['POST'])
def setTemp(zone, temp):
    """
    POSTed value will be new setting
    """
    try:
        floatTemp = float(temp)
        tempController.setConfig(zone,floatTemp)
    except:
        print("Bad float, ignoring")
    
    currentTemp = (tempController.getCurrentAndSetting(zone))
    data = json.dumps( {"current":currentTemp[0], "setting":currentTemp[1]})
    return Response(data, status=200, mimetype='application/json')

@app.route('/')
def index():
    return app.send_static_file('index.html')