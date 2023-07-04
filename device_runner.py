# python
# accept a username as argument then open up that config file for that user
# and print out the contents of that file

import sys
import os
import json
import datetime
import time
from itertools import cycle

DEBUG=True

def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def load_config(config_path):
    with open(config_path) as f:
        return json.load(f)
    
def mqtt_push(config,webp):
    

if len(sys.argv) < 3:
    print("Usage: python3 %s <user> <device_id>" % sys.argv[0])
    exit(1)

user = sys.argv[1]
device = sys.argv[2]

dprint("doing {} - {} ".format(user,device))

config_path = "users/{}/{}.json".format(user, user)

if not os.path.exists(config_path):
    print("Config file ({}) does not exist".format(config_path))
    exit(1)


config = load_config(config_path)
dprint(json.dumps(config, indent=4))

# now get device
device = config['devices'][device]
dprint("processing {}".format(device))
app_array = device['apps'].values()

app_cycler = cycle(app_array)
while True:
    # infinitiely loop through the array
    app = next(app_cycler)
    dprint("apps is {}".format(json.dumps(app)))
    app_basename = "{}-{}".format(app['name'],app["iname"])
    webp_path = "tidbyt_manager/webp/{}.webp".format(app_basename)

    delay = app.get('display_time',5)
    
    if app.get('enabled') == "true":
        dprint("pushing {}".format(app_basename))
        #mqtt_push(config, webp_path)
        time.sleep(delay)
    else:
        dprint("skipping {}".format(app_basename))
    

