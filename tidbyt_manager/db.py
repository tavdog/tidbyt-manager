import os,json
from werkzeug.security import check_password_hash, generate_password_hash
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
    # test for directory named dir and if not exist creat it
    user_dir = "users/{}".format(user)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
        os.makedirs(user_dir+"/configs")
        return True
    else:
        return False

def get_apps_list():
    
    # open json file and conver to dictionary
    with open("tidbyt-apps/apps.json",'r') as f:
        return json.load(f)
        
def sanitize(str):
    str = str.replace(" ","")
    str = str.replace("-","")
    str = str.replace(".","")
    str = str.replace("/","")
    str = str.replace("\\","")
    return str
