from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_file, abort
)
from tidbyt_manager import config
from werkzeug.exceptions import abort
from tidbyt_manager.auth import login_required
import tidbyt_manager.db as db
import uuid,os


bp = Blueprint('manager', __name__)

@bp.route('/')
@login_required
def index():

    os.system("pkill -f pixlet") # kill any pixlet processes

    devices = dict()
    if "devices" in g.user:
        devices = g.user["devices"].values()
    return render_template('manager/index.html', devices=devices)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        api_id = request.form['api_id']
        api_key = request.form['api_key']
        notes = request.form['notes']
        error = None
        if not name:
            error = 'Name is required.'
        if error is not None:
            flash(error)
        else:
            device = dict()
            device["id"] = str(uuid.uuid4())
            print("id is :" + str(device["id"]))
            device["name"] = name
            device["api_id"] = api_id
            device["api_key"] = api_key
            device["notes"] = notes
            user = g.user
            if "devices" not in user:
                user["devices"] = {}
        
            user["devices"][device["id"]] = device
            db.save_user(user)

            return redirect(url_for('manager.index'))
    return render_template('manager/create.html')

@bp.route('/<string:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    if request.method == 'POST':
        name = request.form['name']
        notes = request.form['notes']
        api_id = request.form['api_id']
        api_key = request.form['api_key']
        error = None
        if not name or not id:
            error = 'Id and Name is required.'
        if error is not None:
            flash(error)
        else:
            device = dict()
            device["id"] = id
            device["name"] = name
            device["api_id"] = api_id
            device["api_key"] = api_key
            device["notes"] = notes
            
            user = g.user
            if "apps" in user["devices"][id]:
                device["apps"] = user["devices"][id]["apps"]
            user["devices"][id] = device
            db.save_user(user)

            return redirect(url_for('manager.index'))
    device = g.user["devices"][id]
    return render_template('manager/update.html', device=device)

@bp.route('/<string:id>/delete', methods=('POST',))
@login_required
def delete(id):
    g.user["devices"].pop(id)
    db.save_user(g.user)
    return redirect(url_for('manager.index'))

@bp.route('/<string:id>/<string:iname>/delete', methods=('POST','GET'))
@login_required
def deleteapp(id,iname):
    # delete the config file
    config_path = "users/{}/configs/{}-{}.json".format(g.user['username'],g.user["devices"][id]["apps"][iname]["name"],g.user["devices"][id]["apps"][iname]["iname"])
    tmp_config_path = "users/{}/configs/{}-{}.tmp".format(g.user['username'],g.user["devices"][id]["apps"][iname]["name"],g.user["devices"][id]["apps"][iname]["iname"])
    if os.path.isfile(config_path):
        os.remove(config_path)
    if os.path.isfile(tmp_config_path):
        os.remove(tmp_config_path)

    # use pixlet to delete installation of app if api_key exists (tidbyt server operation) and enabled flag is set to true
    if 'api_key' in g.user["devices"][id] and g.user["devices"][id]["apps"][iname]["enabled"] == "true":
        command = "/pixlet/pixlet delete {} {} -t {}".format(g.user["devices"][id]['api_id'],iname,g.user["devices"][id]['api_key'])
        print("Deleting installation id {}".format(iname))
        os.system(command)

    # delete the webp file
    webp_path = "tidbyt_manager/webp/{}-{}.webp".format(g.user["devices"][id]["apps"][iname]["name"],g.user["devices"][id]["apps"][iname]["iname"])
    # if file exists remove it
    if os.path.isfile(webp_path):
        os.remove(webp_path)
    # pop the app from the user object
    g.user["devices"][id]["apps"].pop(iname)
    db.save_user(g.user)
    return redirect(url_for('manager.index'))

@bp.route('/<string:id>/addapp', methods=('GET','POST'))
@login_required
def addapp(id):
    if request.method == 'POST':
        name = request.form['name']
        uinterval = request.form['uinterval']
        display_time = request.form['display_time']
        notes = request.form['notes']
        error = None
        # generate an iname from 3 digits. will be used later as the port number on which to run pixlet serve
        import random
        iname = str(random.randint(100,999))

        if not name:
            error = 'App name required.'
        if db.file_exists("configs/{}-{}.json".format(name,iname)):
            error = "That installation id already exists"
        if error is not None:
            flash(error)
        else:
            app = dict()
            app["iname"] = iname
            print("iname is :" + str(app["iname"]))
            app["name"] = name
            app["uinterval"] = uinterval
            app["display_time"] = display_time
            app["notes"] = notes
            app["enabled"] = "true"
            app["last_render"] = 0
            app["last_push"] = 0
            user = g.user
            if "apps" not in user["devices"][id]:
                user["devices"][id]["apps"] = {}
        
            user["devices"][id]["apps"][iname] = app
            db.save_user(user)

            return redirect(url_for('manager.configapp', id=id,iname=iname))
        
    else:
        # build the list of apps. 
        apps_list = db.get_apps_list()
        return render_template('manager/addapp.html', apps_list=apps_list)    

@bp.route('/<string:id>/<string:iname>/updateapp', methods=('GET','POST'))
@login_required
def updateapp(id,iname):
    if request.method == 'POST':
        name = request.form['name']
        uinterval = request.form['uinterval']
        notes = request.form['notes']
        if "enabled" in request.form:
            enabled = "true"
        else:
            enabled = "false"
        print(request.form)
        error = None
        if not name or not iname:
            error = 'Name and installation_id is required.'
        if error is not None:
            flash(error)
        else:
            app = dict()
            app["iname"] = iname
            print("iname is :" + str(app["iname"]))
            app["name"] = name
            app["uinterval"] = uinterval
            app["notes"] = notes
            app["enabled"] = enabled
            user = g.user
            if user["devices"][id]["apps"][iname]['enabled'] == "true" and enabled == "false":
                # set fresh_disable so we can delete from tidbyt once and only once
                # use pixlet to delete installation of app if api_key exists (tidbyt server operation) and enabled flag is set to true
                if 'api_key' in g.user["devices"][id]:
                    command = "/pixlet/pixlet delete {} {} -t {}".format(g.user["devices"][id]['api_id'],iname,g.user["devices"][id]['api_key'])
                    print(command)
                    os.system(command)
            user["devices"][id]["apps"][iname] = app
            db.save_user(user)

            return redirect(url_for('manager.index'))
    app = g.user["devices"][id]['apps'][iname]
    return render_template('manager/updateapp.html', app=app,device_id=id)    

@bp.route('/<string:id>/<string:iname>/configapp', methods=('GET','POST'))
@login_required
def configapp(id,iname):
    import subprocess, time
    app = g.user["devices"][id]['apps'][iname]
    app_basename = "{}-{}".format(app['name'],app["iname"])
    app_path = "tidbyt-apps/apps/{}/{}.star".format(app['name'].replace('_',''),app['name'])
    config_path = "users/{}/configs/{}.json".format(g.user['username'],app_basename)
    tmp_config_path = "users/{}/configs/{}.tmp".format(g.user['username'],app_basename)
    webp_path = "tidbyt_manager/webp/{}.webp".format(app_basename)

    # always kill the pixlet proc based on port number.
    os.system("pkill -f 5{}".format(app['iname'])) # kill pixlet process 

    if request.method == 'POST':

    #   do something to confirm configuration ?
        print("checking for : " + tmp_config_path)
        if db.file_exists(tmp_config_path):
            print("file exists")
            with open(tmp_config_path,'r') as c:
                new_config = c.read()                
            #flash(new_config)
            with open(config_path, 'w') as config_file:
                config_file.write(new_config)

            # delete the tmp file
            os.remove(tmp_config_path)

            # run pixlet render with the new config file
            print("rendering")
            result = os.system("/pixlet/pixlet render -c {} {} -o {}".format(config_path, app_path, webp_path))
            print(result)
            if g.user["devices"][id]['api_key'] != "":
                device = g.user["devices"][id]
                command = "/pixlet/pixlet push {} {} -t {} -i {}".format(device['api_id'], webp_path, device['api_key'], app['iname'])
                print("pushing {}".format(app['iname']))
                result = os.system(command)
            # give pixlet some time to
            return redirect(url_for('manager.index'))
        

    url_params = ""
    if db.file_exists(config_path):
        import urllib.parse,json
        with open(config_path,'r') as c:
            config_dict = json.load(c)
        
        url_params = urllib.parse.urlencode(config_dict)
        print(url_params)
        if len(url_params) > 2:
            flash(url_params)
    # ./pixlet serve --saveconfig "noaa_buoy.config" --host 0.0.0.0 src/apps/noaa_buoy.star 
    # execute the pixlet serve process and show in it an iframe on the config page.
    app_path = "tidbyt-apps/apps/{}/{}.star".format(app['name'].replace('_',''),app['name'])
    print(app_path)
    if db.file_exists(app_path):
        subprocess.Popen(["/pixlet/pixlet", "--saveconfig", tmp_config_path, "serve", app_path , '--host=0.0.0.0', '--port=5{}'.format(app['iname'])], shell=False)

        # give pixlet some time to start up 
        time.sleep(2)
        return render_template('manager/configapp.html', app=app, domain_host=config.domain_host, url_params=url_params)

    else:
        flash("App Not Found")
        return redirect(url_for('manager.index'))

@bp.route('/<string:id>/<string:iname>/appwebp')
@login_required
def appwebp(id,iname):
    app = g.user["devices"][id]['apps'][iname]
    app_basename = "{}-{}".format(app['name'],app["iname"])
    webp_path = "/app/tidbyt_manager/webp/{}.webp".format(app_basename)
     # check if the file exists
    if db.file_exists(webp_path):
        return send_file(webp_path, mimetype='image/webp')
    else:
        print("file no exist")
        abort(404)

@bp.route('/set_repo', methods=('GET','POST'))
@login_required
def set_repo():
    if request.method == 'POST':
        if 'app_repo_url' in request.form:
            repo_url = request.form['app_repo_url']
            print(repo_url)
            user_apps_path = "users/{}/apps".format(g.user['username'])
            old_repo = ""
            if 'app_repo_url' in g.user:
                old_repo = g.user['app_repo_url']
                
            if repo_url != "":
                if old_repo != repo_url:
                    # just get the last two words of the repo
                    repo_url = repo_url.split("/")[-2:]
                    repo_url = "/".join(repo_url)
                    g.user['app_repo_url'] = repo_url
                    db.save_user(g.user)

                    print(user_apps_path)
                    if db.file_exists(user_apps_path):
                        # delete the folder and re-clone.
                        os.system("rm -rf {}".format(user_apps_path))                        
                    # pull the repo and save to local filesystem.
                    result = os.system("git clone https://github.com/{} {}".format(repo_url,user_apps_path))
                    flash("Repo Cloned")
                else:
                    # same as before so just issue a pull to update it.
                    result = os.system("git -C {} pull".format(user_apps_path))
                    if result == 0:
                        flash("Repo Updated")
                # run the generate app list for custom repo
                db.generate_apps_list()
                return redirect(url_for('manager.index'))
            
            else:
                flash("No Changes to Repo")
 
            flash("Error Saving Repo")
        return redirect(url_for('auth.edit'))
    abort(404)
