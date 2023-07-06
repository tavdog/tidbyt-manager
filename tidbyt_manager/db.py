import os,json,subprocess
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
user_path = "users/{}/{}.json"
def user_exists(username):
    try:
        with open(user_path.format(username,username)) as file:
            # print("username: {} exists.".format(username))
            return True
    except:
        return False
    return False

def file_exists(file_path):
    if os.path.exists(file_path):
        return True
    else:
        return False

def get_user(username):
    # print("username :{}".format(username))
    # print(user_path.format(username,username))
    try:
        with open(user_path.format(username,username)) as file:
            user = json.load(file)
#            print("return user")
            return user
    except:
        print("problem with get_user")
        return False

def auth_user(username,password):
    try:
        with open(user_path.format(username,username)) as file:
            user = json.load(file)
            print(user)
            if check_password_hash(user.get("password"), password):
                return user
            else:
                print("bad password")
                return False
    except:
        print("problem")
        return False

def save_user(user):
     if "username" in user:
        try:
            with open(user_path.format(user["username"],user["username"]),"w") as file:
                json.dump(user,file)
            return True      
        except:
            print("couldn't save {}".format(user))
            return False
def create_user_dir(user):
    dir = sanitize(user)
    dir = secure_filename(dir)
    # test for directory named dir and if not exist creat it
    user_dir = "users/{}".format(user)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
        os.makedirs(user_dir+"/configs")
        return True
    else:
        return False

# def get_apps_list():
    
#     # open json file and convert to dictionary
#     with open("tidbyt-apps/apps.json",'r') as f:
#         return json.load(f)

def get_apps_list(user):
    app_list = list()
    # test for directory named dir and if not exist creat it
    if user == "system" or user == "":
        dir = "tidbyt-apps/"
        # open json file and convert to dictionary
        with open("tidbyt-apps/apps.json",'r') as f:
            return json.load(f)
    else:
        dir = "users/{}/apps".format(user)
    if os.path.exists(dir):
        command = [ "find", dir, "-name", "*.star" ]
        output = subprocess.check_output(command, text=True)
        print("got find output of {}".format(output))
    
        apps_paths = output.split("\n")
        for app in apps_paths:
            if app == "":
                continue
            app_dict = dict()
            app_dict['path'] = app
            app = app.replace(dir+"/","")
            app = app.replace("\n","")
            app = app.replace('.star','')
            app_dict['name'] = app.split('/')[-1]

            # look for a yaml file
            app_base_path = ("/").join(app_dict['path'].split('/')[0:-1])
            yaml_path = "{}/manifest.yaml".format(app_base_path)
            print("checking for yaml in {}".format(yaml_path))
            # check for existeanse of yaml_path
            if os.path.exists(yaml_path):
                with open(yaml_path,'r') as f:
                    yaml_str = f.read()
                    for line in yaml_str.split('\n'):
                            if "summary:" in line:
                                app_dict['summary'] = line.split(': ')[1]
            else:
                app_dict['summary'] = "Custom App"
            app_list.append(app_dict)
        return app_list
    else:
        print("no apps list found for {}".format(user))
        return []
    
def get_app_details(user,name):
    # first look for the app name in the custom apps
    custom_apps = get_apps_list(user)
    print(user,name)
    for app in custom_apps:
        print(app)
        if app['name'] == name:
            # we found it
            return app
    # if we get here then the app is not in custom apps
    # so we need to look in the tidbyt-apps directory
    apps = get_apps_list("system")
    for app in apps:
        if app['name'] == name:
            return app
    return {}

def sanitize(str):
    str = str.replace(" ","")
    str = str.replace("-","")
    str = str.replace(".","")
    str = str.replace("/","")
    str = str.replace("\\","")
    return str

# basically just call gen_apps_array.py script
def generate_apps_list():
    os.system("python3 gen_app_array.py")
    print("generated apps list")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['star']

def save_user_app(file,path):
    filename = sanitize(file.filename)
    filename = secure_filename(filename)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(path, filename))
        return True
    else:
        return False
