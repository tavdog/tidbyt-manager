# python
# accept a username as argument then open up that config file for that user
# and print out the contents of that file

import sys
import os
import json
import datetime
import time

DEBUG=False
def process_app(app,device,user):
    global force,DEBUG
    app_basename = "{}-{}".format(app['name'],app["iname"])
    config_path = "users/{}/configs/{}.json".format(user['username'],app_basename)
    webp_path = "tidbyt_manager/webp/{}.webp".format(app_basename)
    print("\t\tApp: {} - {}".format(app['iname'],app['name']))
    if 'path' in app:
        app_path = app['path']
    else:
        print("\t\t\tNo path for {}".format(app['name']))
        return
    # ensure app exists at app_path
    if not os.path.exists(app_path):
        # this should not happen but it probably will
        print("\t\t\tApp path {} does not exist".format(app_path))
        return
        
    now = int(time.time())
    
    if 'last_render' not in app:
        app['last_render'] = 0
    print("\t\t\tlast render: {}".format(app['last_render']))
    # check for enabled
    if app['enabled'] != 'true':
        print("\t\t\tApp not Enabled")
        return
    # check uinterval
    if now - app['last_render'] > int(app['uinterval'])*60 or force or DEBUG:
        print("\t\t\tRun")
        # build the pixlet render command
        command = "/pixlet/pixlet render -c {} {} -o {}".format(config_path, app_path, webp_path)
        print(command)
        result = os.system(command)
        if result!= 0:
            print("\t\t\tError running pixlet render")
        else:
            # update the config file with the new last render time
            print("\t\t\tupdate last render")
            app['last_render'] = int(time.time())
            result = 0
            if len(device['api_key']) > 1:
                # if webp filesize is zero then issue delete command instead of push
                if os.path.getsize(webp_path) == 0:
                    if not app.get('deleted'): # if we haven't already deleted this app installation delete it
                        command = "/pixlet/pixlet delete {} {} -t {}".format(device['api_id'],app['iname'],device['api_key'])
                        print("\t\t\t\tWebp filesize is zero. Deleting installation id {}".format(app['iname']))
                        result = os.system(command)
                        app['deleted'] = True
                    else:
                        print("\t\t\t\tPreviously deleted, doing nothing")
                else:
                    command = "/pixlet/pixlet push {} {} -b -t {} -i {}".format(device['api_id'], webp_path, device['api_key'], app['iname'])
                    print("pushing {}".format(app['iname']))
                    result = os.system(command)
                    app['deleted'] = False
                if result != 0:
                    print("\t\t\tError pushing to device")
                else:
                    # update the config file with the new last push time
                    print("\t\t\tupdate last push")
                    app['last_push'] = int(time.time())
            else:
                # api_key is short meaning we probably need to push via mqtt
                print("\t\t\tmqtt push is handled by device_runner.py")

    else:
        print("\t\t\tNext update in {} seconds.".format(int(app['uinterval'])*60 - (now - app['last_render'])))

def process_device(device,user):
    print("\tDevice: %s" % device['name'])
    if 'apps' in device:
        for app in device['apps'].values(): 
            process_app(app,device,user)
    else:
        print("\t\tno apps here")
   
def save_json(data, filename):
    print("saving {}".format(json.dumps(data)))
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def main():

    # set the current time variable
    now = time.time()
    global force
    force = False
    user = None
    # check for correct number of arguments
    if len(sys.argv) < 2:
        print("Processing all users")

    else:
        user = sys.argv[1]

    if len(sys.argv) > 2:
        force = True

    user_list = list()
    # open json config file is located in users/user/user.json
    if not user:
        # get list of directories in user
        for user in os.listdir("users"):
            if os.path.isdir(os.path.join("users", user)):
                user_list.append(user)
    else:
        user_list.append(user)


    for user in user_list:    
        print("User : {}".format(user))
        config_file = os.path.join("users", user, "%s.json" % user)
        if not os.path.exists(config_file):
            print("No config")
            next
        # decode json from the file load dict object from json file
        with open(config_file, "r") as f:
            try:
                user = json.load(f)
            except:
                print("bad json")
                next
        if 'devices' in user:
            for device in user['devices'].values():
                process_device(device,user)

            save_json(user,config_file)
        


if __name__ == "__main__":
    main()
