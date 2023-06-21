# python
# accept a username as argument then open up that config file for that user
# and print out the contents of that file

import sys
import os
import json
import datetime
import time


def process_app(app,device,user):
    global force
    app_basename = "{}-{}".format(app['name'],app["iname"])
    config_path = "users/{}/configs/{}.json".format(user['username'],app_basename)
    webp_path = "tidbyt_manager/webp/{}.webp".format(app_basename)
    app_path = "tidbyt-apps/apps/{}/{}.star".format(app['name'].replace('_',''),app['name'])

    now = int(time.time())
    print("\tApp: {} - {}".format(app['iname'],app['name']))
    print("\tLast run: {}".format(app['last_run']))
    # check uinterval
    if now - app['last_run'] > int(app['uinterval']) or force:
        print("\tRun")
        # build the pixlet render command
        command = "/pixlet/pixlet render -c {} {} -o {}".format(config_path, app_path, webp_path)
        result = os.system(command)
        if result!= 0:
            print("\tError running pixlet render")
        else:
            # push to pixlet with quiet option, maybe use a separate shell script for this i dont'
            # ./pixlet push $(cat tidbyt_marc.id) solar_manager_ch.webp -t $(cat tidbyt_marc.key) -i solarautarky
            command = "/pixlet/pixlet push {} {} -t {} -i {}".format(device['api_id'], webp_path, device['api_key'], app['iname'])
            print(command)
            result = os.system(command)
            if result!= 0:
               print("\tError pushing to device")
        # update the config file with the new last run time
            print("update last run")
            app['last_run'] = int(time.time())
    else:
        print("\tNext update in {} seconds.".format(int(app['uinterval']) - (now - app['last_run'])))

def process_device(device,user):
    print("Device: %s" % device['name'])
    for app in device['apps'].values(): 
        process_app(app,device,user)
   
def save_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def main():

    # set the current time variable
    now = time.time()
    global force
    force = False
    # check for correct number of arguments
    if len(sys.argv) < 2:
        print("Usage: {} <username>".format(sys.argv[0]))
        sys.exit(1)
    if len(sys.argv) > 2:
        force = True

    # open json config file is located in users/user/user.json
    user = sys.argv[1]
    config_file = os.path.join("users", user, "%s.json" % user)
    if not os.path.exists(config_file):
        print("No config")
        sys.exit(1)
    # decode json from the file load dict object from json file
    with open(config_file, "r") as f:
        try:
            user = json.load(f)
        except:
            print("bad json")
            sys.exit(1)
    for device in user['devices'].values():
        process_device(device,user)

    # if "last_run" in user:
    #     print("Last run: %s" % user["last_run"])
    # else:
    #     print("No last run")

    save_json(user,config_file)
    


if __name__ == "__main__":
    main()
