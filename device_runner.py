# handles non-tidbyt api devices.  pushes web directly via mqtt based on timing values set in user config file

import sys, os, json, shutil
import datetime, time, pidfile
from itertools import cycle
import paho.mqtt.client as mqtt
from urllib.parse import urlparse

import logging

DEBUG=True

def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)
    else:
        logging.info(*args, **kwargs)

def load_config(config_path):
    with open(config_path) as f:
        return json.load(f)

def mqtt_setup(connect_string):
    try:
        url = urlparse(connect_string)
        user =  url.username
        passw = url.password
        host = url.hostname or 'mqtt'
        port = url.port or 1883
        topic = url.path
        topic = topic[1:]
        client = mqtt.Client()
        if user and passw : client.username_pw_set(user,passw)
        dprint(f"Connecting to {host}:{port}")
        client.connect(host,port)
        client.loop_start()
        return client,topic
    except Exception as e:
        dprint("Error parsing mqtt url or connecting {}".format(connect_string))
        dprint(repr(e))
        return None,None

def mqtt_send_img(client,topic,webp_path):
    topic = topic + "/img"
    dprint(f"in mqtt send with topic {topic}")
    if os.path.isfile(webp_path) and os.path.getsize(webp_path) > 0:
        file_size = os.stat(webp_path)
        dprint(f"Size of file : {file_size.st_size} bytes")
        in_file = open(webp_path, "rb")

        info = client.publish(
            topic=topic,
            payload="START",
            qos=0,
            retain=False,
        )
        info.wait_for_publish()
        if info.is_published():
            dprint("Published START")

        time.sleep(1)
        info = client.publish(
            topic=topic,
            payload=file_size.st_size,
            qos=0,
            retain=False,
        )
        info.wait_for_publish()
        if info.is_published():
            dprint("Published " + str(file_size.st_size))

        time.sleep(1)
        info = client.publish(
            topic=topic,
            payload=in_file.read(),
            qos=0,
            retain=False,
        )
        info.wait_for_publish()
        if info.is_published():
            dprint("Published binary file")

        time.sleep(1)
        info = client.publish(
            topic=topic,
            payload="FINISH",
            qos=0,
            retain=False,
        )
        info.wait_for_publish()
        if info.is_published():
            dprint("Published topic: END")
            return True

        else:
            dprint("Topic {topic} not published")
            return False
    else:
        dprint("file {} does not exist".format(webp_path))
        return False


def main_loop(user,device_id):
    while(True):
        dprint("Pulling config")
        config_path = "users/{}/{}.json".format(user, user)

        if not os.path.exists(config_path):
            dprint("Config file ({}) does not exist".format(config_path))
            exit(1)


        config = load_config(config_path)
        #dprint(json.dumps(config, indent=4))

        # now get device and setup mqtt client
        device = config['devices'][device_id]
        dprint("processing {}".format(device_id))
        mqtt_client,topic = mqtt_setup(device['api_id']) # api_id is an mqtt url string with username and password
        if mqtt_client == None:
            dprint("Can't connect, quitting")
            exit(1)

        push_loop(device,mqtt_client,topic,config_path)

def push_loop(device,mqtt_client,topic,config_path):
    start_time = time.time()
    all_apps_array = list(device['apps'].values())
    app_array = list()
    # loop through app_array and delete any with disabled flag
    for app in all_apps_array:
        if app.get('enabled',"false") == "true":
            app_array.append(app)
        else:
            dprint(f"skipping {app['name']}")
            

    if len(app_array) == 0:
        dprint("No apps enabled for this device, quitting")
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
        webp_curr_path = "tidbyt_manager/webp/{}.webp".format(device['name'])
        # copy webp_path file to current/device_name.webp
        dprint("copying webp to current")
        # current_directory = os.getcwd()  # Get the current working directory
        destination_path = "tidbyt_manager/webp/skidbyt_1.webp"  # Create the destination path

        # Copy the file
        shutil.copy(webp_path, destination_path)
        delay = app.get('display_time',5)
        
        if "mqtt" in device['api_id']:
            dprint("publishing {}".format(app_basename))
            if mqtt_send_img(mqtt_client,topic,webp_path):
                time.sleep(int(delay))
            else:
                dprint("Mqtt Error. Ensure you have publish permissions")
                time.sleep(10) # so we don't spam the mqtt server on errors
        else:
            time.sleep(int(delay))

        # check for the last item and check for modified config file if so, restart the loop
        if i == len(app_array) - 1:
            dprint("checking for config file changes")
            if os.path.getmtime(config_path) > start_time:
                dprint("config file changed, reloading")
                return
        


#################################################
# Start of main
#################################################

if len(sys.argv) < 3:
    dprint("Usage: python3 %s <user> <device_id>" % sys.argv[0])
    exit(1)

user = sys.argv[1]
device = sys.argv[2]
logging.basicConfig(filename=f"/var/log/{user}-{device}.log", encoding='utf-8', level=logging.INFO)
dprint("doing {} - {} ".format(user,device))

try:
    with pidfile.PIDFile(f"/var/run/{user}-{device}.pid"):
        main_loop(user,device)
except pidfile.AlreadyRunningError:
    dprint('Already running.')
    exit(1)

