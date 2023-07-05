# handles non-tidbyt api devices.  pushes web directly via mqtt based on timing values set in user config file

import sys
import os
import json
import datetime
import time
from itertools import cycle
import paho.mqtt.client as mqtt
from urllib.parse import urlparse

DEBUG=True

def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def load_config(config_path):
    with open(config_path) as f:
        return json.load(f)

def mqtt_setup(connect_string):
    try:
        url = urlparse(connect_string)
        user =  url.username
        passw = url.password
        host = url.hostname
        port = url.port
        topic = url.path
        client = mqtt.Client()
        client.username_pw_set(user,passw)
        client.connect(host,port)
        client.loop_start()
        return client,topic
    except:
        print("Error parsing mqtt url or connecting {}".format(connect_string))
        return None,None

def mqtt_send(client,topic,webp_path):
    if os.path.isfile(webp_path) and os.path.getsize(webp_path) > 0:
        in_file = open(webp_path, "rb")
        webp = in_file.read()
        info = client.publish(
            topic=topic,
            payload=webp,
            qos=0,
            retain=False,
        )
        info.wait_for_publish()
        if info.is_published():
            print("Published webp to topic: " + topic )
            return True
        else:
            return False
    else:
        print("file {} does not exist".format(f))
        return False

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

# now get device and setup mqtt client
device = config['devices'][device]
dprint("processing {}".format(device))
mqtt_client,topic = mqtt_setup(device['api_id']) # api_id is an mqtt url string with username and password
if mqtt_client == None:
    print("Can't connect, quitting")
    exit(1)

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
        if mqtt_send(mqtt_client,topic,webp_path):
            time.sleep(delay)
        else:
            print("Mqtt Error. Ensure you have publish permissions")
            time.sleep(10) # so we don't spam the mqtt server on errors
    else:
        dprint("skipping {}".format(app_basename))
    

