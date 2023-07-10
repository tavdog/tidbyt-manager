# handles non-tidbyt api devices.  pushes web directly via mqtt based on timing values set in user config file

import sys, os, json
import datetime, time, pidfile
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


def main_loop(user,device_id):
    while(True):
        print("Pulling config")
        config_path = "users/{}/{}.json".format(user, user)

        if not os.path.exists(config_path):
            print("Config file ({}) does not exist".format(config_path))
            exit(1)


        config = load_config(config_path)
        dprint(json.dumps(config, indent=4))

        # now get device and setup mqtt client
        device = config['devices'][device_id]
        dprint("processing {}".format(device_id))
        mqtt_client,topic = mqtt_setup(device['api_id']) # api_id is an mqtt url string with username and password
        if mqtt_client == None:
            print("Can't connect, quitting")
            exit(1)

        push_loop(device,mqtt_client,topic,config_path)

def push_loop(device,mqtt_client,topic,config_path):
    start_time = time.time()
    all_apps_array = list(device['apps'].values())
    app_array = list()
    # loop through app_array and delete any with disabled flag
    for app in all_apps_array:
        print(f"checking {app['name']}")
        if app.get('enabled',"false") == "true":
            app_array.append(app)
        else:
            print(f"skipping {app['name']}")
            

    if len(app_array) == 0:
        print("No apps enabled for this device")
        exit(1) # sleep and wait until config file is modified before trying again maybe ?

    # now we have an array of apps to cycle through
    # cycle through the array and push the webp via mqtt

    #app_cycler = cycle(app_array)
    for i in cycle(range(len(app_array))):
        # infinitiely loop through the array
        app = app_array[i]
        dprint("apps is {}".format(json.dumps(app)))
        app_basename = "{}-{}".format(app['name'],app["iname"])
        webp_path = "tidbyt_manager/webp/{}.webp".format(app_basename)
        
        delay = app.get('display_time',5)
        
        dprint("pushing {}".format(app_basename))
        if mqtt_send(mqtt_client,topic,webp_path):
            time.sleep(int(delay))
        else:
            print("Mqtt Error. Ensure you have publish permissions")
            time.sleep(10) # so we don't spam the mqtt server on errors

        # check for the last item and check for modified config file if so, restart the loop
        if i == len(app_array) - 1:
            print("checking for config file changes")
            if os.path.getmtime(config_path) > start_time:
                print("config file changed, reloading")
                return
        


#################################################
# Start of main
#################################################

if len(sys.argv) < 3:
    print("Usage: python3 %s <user> <device_id>" % sys.argv[0])
    exit(1)

user = sys.argv[1]
device = sys.argv[2]

dprint("doing {} - {} ".format(user,device))

try:
    with pidfile.PIDFile(f"/var/run/{user}-{device}.pid"):
        main_loop(user,device)
except pidfile.AlreadyRunningError:
    print('Already running.')
    exit(1)

