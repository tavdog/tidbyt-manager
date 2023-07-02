# generate the apps.txt list. will pullapp descrption pulled from the yaml if available
import json,os,sys,subprocess


apps_path = "tidbyt-apps"

# check for existence of apps_path dir
if not os.path.exists(apps_path):
    print("{} directory not found".format(apps_path))
    exit()

# run a command to generate a txt file withh all the .star file in the apps_path directory
command = [ "find", apps_path, "-name", "*.star" ]
output = subprocess.check_output(command, text=True)
print("got find output of {}".format(output))

# pull in the apps.txt list
apps_array = []
apps = output.split('\n')
apps.sort()
for app in apps:
    print(app)
    try:
        # read in the file from apps_path/apps/
        app_dict = dict()
        app_dict['name'] = os.path.basename(app).replace('.star','')
        app_dict['path'] = app
        app_path = app #"{}/apps/{}/{}.star".format(apps_path, app.replace('_',''), app)

        # skip any files that include secret.star module and 
        with open(app_path,'r') as f:
            app_str = f.read()
            if "secret.star" in app_str:
                print("skipping {} (uses secret.star)".format(app))
                continue
        
        app_base_path = ("/").join(app_path.split('/')[0:-1])
        yaml_path = "{}/manifest.yaml".format(app_base_path)

        # check for existeanse of yaml_path
        if os.path.exists(yaml_path):
            with open(yaml_path,'r') as f:
                yaml_str = f.read()
                for line in yaml_str.split('\n'):
                        if "summary:" in line:
                            app_dict['summary'] = line.split(': ')[1]
        else:
                app_dict['summary'] = " -- "

        apps_array.append(app_dict)
    except Exception as e:
            print("skipped " + app + " due to error: " + repr(e))
#print(apps_array)

# writeout apps_array as a json file
with open("{}/apps.json".format(apps_path),'w') as f:
    json.dump(apps_array,f)
