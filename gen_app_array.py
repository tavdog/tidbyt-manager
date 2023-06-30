# generate the apps.txt list. should have app name and app descrption pulled from the yaml
import json,os,sys

# check for an argument
if len(sys.argv) > 1:
    # set path to first argument
    app_path = "users/{}/custom-apps".format(sys.argv[1])
else:
    app_path = "tidbyt-apps"

# change directory to path
os.chdir(app_path)

# check for existence of apps_path dir
if not os.path.exists(app_path):
    print("apps_path directory not found")
    exit()

# run a command to generate a txt file withh all the .star file in the apps_path directory
os.system("ls {}/apps/* | grep star > {}/apps.txt".format(app_path,app_path))

# pull in the apps.txt list
apps_array = []
with open("{}/apps.txt".format(app_path),'r') as f:
        apps = f.read().split('\n')
        for app in apps:
            try:
                # read in the file from apps_path/apps/
                app_dict = dict()
                app_dict['name'] = app
                app = app.replace('.star','')
                app_path = "{}/apps/{}/{}.star".format(app_path, app.replace('_',''), app)

                # skip any files that include secret.star module and 
                with open(app_path,'r') as f:
                    app_str = f.read()
                    if "secret.star" in app_str:
                        print("skipping {} (uses secret.star)".format(app))
                        continue
                
                yaml_path = "{}/apps/{}/manifest.yaml".format(app_path, app.replace('_',''),app)
                # check for existeanse of yaml_path
                if os.path.exists(yaml_path):
                    with open(yaml_path,'r') as f:
                        yaml_str = f.read()
                        for line in yaml_str.split('\n'):
                                if "summary:" in line:
                                    app_dict['summary'] = line.split(': ')[1]
                else:
                     app_dict['summary'] = "App"

                apps_array.append(app_dict)
            except:
                 print("skipped " + app)
print(apps_array)

# delete the apps.txt file
os.system("rm {}/apps.txt".format(app_path))

# writeout apps_array as a json file
with open("{}/apps.json".format(app_path),'w') as f:
    json.dump(apps_array,f)
