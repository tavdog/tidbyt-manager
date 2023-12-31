# python
# accept a username as argument then open up that config file for that user
# and print out the contents of that file

import sys,os,pidfile
import json
import datetime
import time
import subprocess

DEBUG=False
def dprint(*args, **kwargs):
    if DEBUG: print(*args, **kwargs)

def print_error(result):
    print("result.returncode: {}".format(result.returncode))
    print("result.stderr: {}".format(result.stderr))
    print("result.stdout: {}".format(result.stdout))
    print("result.args: {}".format(result.args))


def process_app(app,device,user):
    global force,DEBUG
    app_basename = "{}-{}".format(app['name'],app["iname"])
    config_path = "users/{}/configs/{}.json".format(user['username'],app_basename)
    webp_path = "tidbyt_manager/webp/{}.webp".format(app_basename)
    print("\t\tApp: {} - {}".format(app['iname'],app['name']))
    if 'path' in app:
        app_path = app['path']
    else:
        print("\t\t\tNo path for {}, trying default location".format(app['name']))
        app_path = "tidbyt-apps/apps/{}/{}.star".format(app['name'].replace('_',''),app['name'])
    # ensure app exists at app_path
    if not os.path.exists(app_path):
        # this should not happen but it probably will
        print("\t\t\tApp path {} does not exist".format(app_path))
        return
    if not os.path.exists(config_path):
        print("\t\t\tConfig file {} does not exist yet. App is probably still getting configured".format(config_path))
        return
        
    now = int(time.time())
    
    if 'last_render' not in app:
        app['last_render'] = 0
    print("\t\t\tlast render: {}".format(app['last_render']))
    # check for enabled
    if app['enabled'] != 'true':
        print("\t\t\tApp not Enabled")
        if app.get('deleted') == 'true' or len(device['api_key']) < 1: # if already deleted return or not tidbyt device
            return
        else:
            print("\t\t\tRecently disabled, deleting installation id {}".format(app['iname']))
            command = ["/pixlet/pixlet", "delete", device['api_id'], app['iname'], "-t",  device['api_key']]
            result = subprocess.run(command)
            app['deleted'] = 'true'
            return
            
    # check uinterval
    if now - app['last_render'] > int(app['uinterval'])*60 or force or DEBUG:
        print("\t\t\tRendering")
        # build the pixlet render command
        #command = "/pixlet/pixlet render -c {} {} -o {}".format(config_path, app_path, webp_path)
        command = ["/pixlet/pixlet", "render", "-c", config_path, app_path, "-o",webp_path]
        #print(command)
        result = subprocess.run(command)
        if result.returncode != 0:
            print("\t\t\tError running pixlet render")
            print_error(result)
        else:
            # update the config file with the new last render time
            print("\t\t\tupdating last render")
            app['last_render'] = int(time.time())
            result = None
            if len(device['api_key']) > 1:
                # if webp filesize is zero then issue delete command instead of push
                if os.path.getsize(webp_path) == 0:
                    if app.get('deleted') != 'true': # if we haven't already deleted this app installation delete it
                        command = ["/pixlet/pixlet", "delete", device['api_id'], app['iname'], "-t",  device['api_key']]
                        print("\t\t\t\tWebp filesize is zero. Deleting installation id {}".format(app['iname']))
                        result = subprocess.run(command)
                        app['deleted'] = 'true'
                    else:
                        print("\t\t\t\tPreviously deleted, doing nothing")
                else:
                    #command = "/pixlet/pixlet push {} {} -b -t {} -i {}".format(device['api_id'], webp_path, device['api_key'], app['iname'])
                    command = ["/pixlet/pixlet", "push", device['api_id'], webp_path, "-b", "-t", device['api_key'], "-i", app['iname']]
                    #print(command)
                    print("\t\t\t\tpushing {}".format(app['iname']))
                    result = subprocess.run(command)
                    app['deleted'] = 'false'
                    app['last_push'] = int(time.time())
            else:
                # api_key is short meaning we probably need to push via mqtt
                print("\t\t\tmqtt push is handled by device_runner.py")

    else:
        print("\t\t\tNext update in {} seconds.".format(int(app['uinterval'])*60 - (now - app['last_render'])))

def process_device(device,user):
    username = user['username']
    device_id = device['id']
    print("\tDevice: %s" % device['name'])

    if 'apps' in device:

        # do we have at least 1 app ?
        if len(device['apps']) and "true" in [v['enabled'] for (k,v) in device['apps'].items()]:
            # start the mqtt runner if api_id has mqtt in there and no pid file
            if "mqtt://" in device['api_id'] and not os.path.exists(f"/var/run/{username}-{device_id}.pid"):
                import subprocess
                print(f"\t\tStarting mqtt_runner.py for {username} - {device_id}")
                subprocess.Popen(["python3", "device_runner.py", username, device_id])
            else:
                pass
                #print("skipping device runner")
        # process each app
        for app in device['apps'].values(): 
            process_app(app,device,user)
    else:
        print("\t\tno apps here")
   
def save_json(data, filename):
    dprint("saving {}".format(json.dumps(data)))
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def main():
    print("____________________________________-------------------------___________________________________________")
    print(f"____________________________________{datetime.datetime.now()}___________________________________________")
    
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
        #print(config_file)
        if not os.path.exists(config_file):
            print("No config")
            continue
        # decode json from the file load dict object from json file
        with open(config_file, "r") as f:
            try:
                user = json.load(f)
            except:
                print("bad json")
                continue
        if 'devices' in user:
            for device in user['devices'].values():
                process_device(device,user)

            save_json(user,config_file)
        


if __name__ == "__main__":
    try:
        with pidfile.PIDFile(f"/var/run/runner.pid"):
            main()
    except pidfile.AlreadyRunningError:
        print('Already running.')
        exit(1)

    
