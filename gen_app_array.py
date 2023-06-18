# generate the apps.txt list. should have app name and app descrption pulled from the yaml
import json
# pull in the apps.txt list
apps_array = []
with open("tidbyt-apps/apps.txt",'r') as f:
        apps = f.read().split('\n')
        for app in apps:
            try:
                # read in the file from tidbyt-apps/apps/
                app_dict = dict()
                app_dict['name'] = app
                app = app.replace('.star','')
                #app_path = "tidbyt-apps/apps/{}/{}.star".format(app.replace('_',''),app) 
                yaml_path = "tidbyt-apps/apps/{}/manifest.yaml".format(app.replace('_',''),app)
                with open(yaml_path,'r') as f:
                    yaml_str = f.read()
                    for line in yaml_str.split('\n'):
                            if "summary:" in line:
                                app_dict['summary'] = line.split(': ')[1]
                apps_array.append(app_dict)
            except:
                 print("skipped " + app)
print(apps_array)

# writeout apps_array as a json file
with open("tidbyt-apps/apps.json",'w') as f:
    json.dump(apps_array,f)
