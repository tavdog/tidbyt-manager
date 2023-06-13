import os,json
user_path = "users/{}.json"
def user_exists(username):
    try:
        with open(user_path.format(username)) as file:
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
    print("username :{}".format(username))
    try:
        with open(user_path.format(username)) as file:
            user = json.load(file)
            #print("return user")
            return user
    except():
        print("problem with get_user")
        return False

def auth_user(username,password):
    try:
        with open(user_path.format(username)) as file:
            user = json.load(file)
            print(user)
            if user.get("password") == password:
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
            with open(user_path.format(user["username"]),"w") as file:
                json.dump(user,file)
            return True      
        except:
            print("couldn't save {}".format(user))
            return False
        
def get_apps_list():
    with open("tidbyt-apps/apps.txt",'r') as f:
        apps = f.read().split('\n')
        print(apps)
        return apps


# import sqlite3
# import click
# from flask import current_app, g
# from flask.cli import with_appcontext
# def get_db():
#     if 'db' not in g:
#         g.db = sqlite3.connect(
#             current_app.config['DATABASE'],
#             detect_types=sqlite3.PARSE_DECLTYPES
#         )
#         g.db.row_factory = sqlite3.Row
#     return g.db

# def close_db(e=None):
#     db = g.pop('db', None)
#     if db is not None:
#         db.close()

# def init_db():
#     db = get_db()
#     with current_app.open_resource('schema.sql') as f:
#         db.executescript(f.read().decode('utf8'))

# @click.command('init-db')
# @with_appcontext
# def init_db_command():
#     """Clear the existing data and create new tables."""
#     init_db()
#     click.echo('Initialized the database.')

# def init_app(app):
#     app.teardown_appcontext(close_db)
#     app.cli.add_command(init_db_command)