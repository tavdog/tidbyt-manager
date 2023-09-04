from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_file, abort, current_app
)

from werkzeug.exceptions import abort
from tidbyt_manager.auth import login_required
import tidbyt_manager.db as db
import uuid,os,subprocess


bp = Blueprint('manager', __name__)


@bp.route('/')
@login_required
def index():

    #os.system("pkill -f serve") # kill any pixlet serve processes

    devices = dict()
    if "devices" in g.user:
        devices = g.user["devices"].values()
    return render_template('manager/index.html', devices=devices)

# new function to handle uploading a an app
@bp.route('/uploadapp', methods=('GET', 'POST'))
@login_required
def uploadapp():
    user_apps_path = f"{db.get_users_dir()}/{g.user['username']}/apps"
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect('manager.uploadapp')
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file:
            if file.filename == '':
                flash('No file')
                return redirect('manager.uploadapp')

            # save the file to the user's
            if db.save_user_app(file,user_apps_path):
                flash("Upload Successful")
                return redirect(url_for('manager.index'))
            else:
                flash("Save Failed")
                return redirect(url_for('manager.uploadapp'))
    
    # check for existance of apps path
    if not os.path.isdir(user_apps_path):
        os.mkdir(user_apps_path)

    # get the list of star file in the user_apps_path
    star_files = list()
    for file in os.listdir(user_apps_path):
        if file.endswith(".star"):
            star_files.append(file)
   
    return render_template('manager/uploadapp.html', files=star_files)

# function to delete an uploaded star file
@bp.route('/deleteupload/<string:filename>', methods=('POST','GET'))
@login_required
def deleteupload(filename):
    db.delete_user_upload(g.user,filename)
    return redirect(url_for('manager.uploadapp'))

@bp.route('/adminindex')
@login_required
def adminindex():
    if g.user['username'] != 'admin': abort(404)
    userlist = list()
    # go through the users folder and build a list of all users
    users = os.listdir("users")
    # read in the user.config file
    for username in users:
        user = db.get_user(username)
        if user: userlist.append(user)

    return render_template('manager/adminindex.html', users = userlist)

@bp.route('/admin/<string:username>/delete', methods=('POST','GET'))
@login_required
def deleteuser(username):
    
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
    # first ensure this app id exists in the current users config
    if id not in g.user["devices"]:
        abort(404)
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
    users_dir = db.get_users_dir()
    config_path = "{}/{}/configs/{}-{}.json".format(users_dir,g.user['username'],g.user["devices"][id]["apps"][iname]["name"],g.user["devices"][id]["apps"][iname]["iname"])
    tmp_config_path = "{}/{}/configs/{}-{}.tmp".format(users_dir,g.user['username'],g.user["devices"][id]["apps"][iname]["name"],g.user["devices"][id]["apps"][iname]["iname"])
    if os.path.isfile(config_path):
        os.remove(config_path)
    if os.path.isfile(tmp_config_path):
        os.remove(tmp_config_path)

    # use pixlet to delete installation of app if api_key exists (tidbyt server operation) and enabled flag is set to true
    if 'api_key' in g.user["devices"][id] and g.user["devices"][id]["apps"][iname]["enabled"] == "true":
        command = ["/pixlet/pixlet", "delete", g.user["devices"][id]['api_id'], iname, "-t",  g.user["devices"][id]['api_key']]
        print("Deleting installation id {}".format(iname))
        subprocess.run(command)

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
    if request.method == 'GET':
        # build the list of apps.
        custom_apps_list = db.get_apps_list(g.user['username'])
        apps_list = db.get_apps_list("system")
        return render_template('manager/addapp.html', device=g.user["devices"][id], apps_list=apps_list, custom_apps_list=custom_apps_list)

    elif request.method == 'POST':
        name = request.form['name']
        app_details = db.get_app_details(g.user['username'],name)
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
            app["enabled"] = "false" # start out false, only set to true after configure is finshed
            app["last_render"] = 0
            app["last_push"] = 0
            if "path" in app_details:
                app['path'] = app_details['path'] # this indicates a custom app

            user = g.user
            if "apps" not in user["devices"][id]:
                user["devices"][id]["apps"] = {}
        
            user["devices"][id]["apps"][iname] = app
            db.save_user(user)

            return redirect(url_for('manager.configapp', id=id,iname=iname,delete_on_cancel=1))
    else:
        abort(404)
            
@bp.route('/<string:id>/<string:iname>/toggle_enabled', methods=(['GET']))
@login_required
def toggle_enabled(id,iname):
    user = g.user
    app = user["devices"][id]["apps"][iname]

    if user["devices"][id]["apps"][iname]['enabled'] == "true":
        app['enabled'] = "false"
        # set fresh_disable so we can delete from tidbyt once and only once
        # use pixlet to delete installation of app if api_key exists (tidbyt server operation) and enabled flag is set to true
        if 'api_key' in g.user["devices"][id]:
            command = ["/pixlet/pixlet", "delete", g.user["devices"][id]['api_id'], iname, "-t",  g.user["devices"][id]['api_key']]
            print(command)
            subprocess.run(command)
            app['deleted'] = "true"
    else:
        # we should probably re-render and push but that'a  a pain so not doing it right now.
        app['enabled'] = "true"

    user["devices"][id]["apps"][iname] = app
    db.save_user(user) # this saves all changes
    flash("Change will go into effect next render cycle. For immediate change edit or re-configure the app.")
    return redirect(url_for('manager.index'))


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
            user = g.user
            app = user["devices"][id]["apps"][iname]
            app["iname"] = iname
            print("iname is :" + str(app["iname"]))
            app["name"] = name
            app["uinterval"] = uinterval
            app["display_time"] = request.form['display_time']
            app["notes"] = notes
            
            if user["devices"][id]["apps"][iname]['enabled'] == "true" and enabled == "false":
                # set fresh_disable so we can delete from tidbyt once and only once
                # use pixlet to delete installation of app if api_key exists (tidbyt server operation) and enabled flag is set to true
                if 'api_key' in g.user["devices"][id]:
                    command = ["/pixlet/pixlet", "delete", g.user["devices"][id]['api_id'], iname, "-t",  g.user["devices"][id]['api_key']]
                    print(command)
                    subprocess.run(command)
                    app['deleted'] = "true"
            app["enabled"] = enabled
            user["devices"][id]["apps"][iname] = app
            db.save_user(user) # this saves all changes

            return redirect(url_for('manager.index'))
    app = g.user["devices"][id]['apps'][iname]
    return render_template('manager/updateapp.html', app=app,device_id=id)    

@bp.route('/<string:id>/<string:iname>/<int:delete_on_cancel>/configapp', methods=('GET','POST'))
@login_required
def configapp(id,iname,delete_on_cancel):
    users_dir = db.get_users_dir()
    domain_host = current_app.config['DOMAIN'] # used when rendering configapp
    import subprocess, time
    app = g.user["devices"][id]['apps'][iname]
    app_basename = "{}-{}".format(app['name'],app["iname"])
    app_details = db.get_app_details(g.user['username'],app['name'])
    if 'path' in app_details:
        app_path = app_details['path']
    else:
        app_path = "tidbyt-apps/apps/{}/{}.star".format(app['name'].replace('_',''),app['name'])
    config_path = "{}/{}/configs/{}.json".format(users_dir, g.user['username'],app_basename)
    tmp_config_path = "{}/{}/configs/{}.tmp".format(users_dir, g.user['username'],app_basename)
    webp_path = "tidbyt_manager/webp/{}.webp".format(app_basename)

    user_render_port = str(db.get_user_render_port(g.user['username']))
    # always kill the pixlet proc based on port number.
    os.system("pkill -f {}".format(user_render_port)) # kill pixlet process based on port

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
            # render_result = os.system("/pixlet/pixlet render -c {} {} -o {}".format(config_path, app_path, webp_path))
            render_result = subprocess.run(["/pixlet/pixlet", "render", "-c", config_path, app_path, "-o",webp_path])
            if render_result.returncode == 0: # success
                # set the enabled key in app to true now that it has been configured.
                g.user["devices"][id]["apps"][iname]['enabled'] = "true"
                # set last_rendered to seconds
                g.user["devices"][id]["apps"][iname]['last_render'] = int(time.time())
           
                if g.user["devices"][id]['api_key'] != "":
                    device = g.user["devices"][id]
                    # check for zero filesize
                    if os.path.getsize(webp_path) > 0:
                        command = ["/pixlet/pixlet", "push", device['api_id'], webp_path, "-b", "-t", device['api_key'], "-i", app['iname']]
                        print("pushing {}".format(app['iname']))
                        result = subprocess.run(command)
                        if 'deleted' in app: del app['deleted']
                    else:
                        # delete installation may error if the instlalation doesn't exist but that's ok.
                        command = ["/pixlet/pixlet", "delete", device['api_id'], app['iname'], "-t",  device['api_key']]
                        print("blank output, deleting {}".format(app['iname']))
                        result = subprocess.run(command)
                        app['deleted'] = 'true'
                    if result == 0:
                        # set last_pushed to seconds
                        g.user["devices"][id]["apps"][iname]['last_pushed'] = int(time.time())
                    else:
                        flash("Error Pushing App")

                # always save       
                db.save_user(g.user)
            else:
                flash("Error Rendering App")
            
        return redirect(url_for('manager.index'))
        
    #################### run the in browser configure interface via pixlet serve
    elif request.method == 'GET':
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
        print(app_path)
        if db.file_exists(app_path):
            subprocess.Popen(["timeout", "-k", "300", "300", "/pixlet/pixlet", "--saveconfig", tmp_config_path, "serve", app_path , '--host=0.0.0.0', '--port={}'.format(user_render_port)], shell=False)

            # give pixlet some time to start up 
            time.sleep(2)
            return render_template('manager/configapp.html', app=app, domain_host=domain_host, url_params=url_params, device_id=id,delete_on_cancel=delete_on_cancel,user_render_port=user_render_port)

        else:
            flash("App Not Found")
            return redirect(url_for('manager.index'))

@bp.route('/<string:id>/<string:iname>/appwebp')
@login_required
def appwebp(id,iname):
    try:
        app = g.user["devices"][id]['apps'][iname]
        app_basename = "{}-{}".format(app['name'],app["iname"])
        webp_path = "/app/tidbyt_manager/webp/{}.webp".format(app_basename)
        # check if the file exists
        if db.file_exists(webp_path) and os.path.getsize(webp_path) > 0:
            # if filesize is greater than zero
            return send_file(webp_path, mimetype='image/webp')
        else:
            print("file no exist or 0 size")
            abort(404)
    except:
        abort(404)

@bp.route('/set_user_repo', methods=('GET','POST'))
@login_required
def set_user_repo():
    if request.method == 'POST':
        if 'app_repo_url' in request.form:
            repo_url = request.form['app_repo_url']
            print(repo_url)
            user_apps_path = "{}/{}/apps".format(db.get_users_dir(), g.user['username'])
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
                        subprocess.run(["rm", "-rf", user_apps_path])                        
                    # pull the repo and save to local filesystem. use blah:blah as username password so requests for unknown or private repos fail imeediately
                    result = subprocess.run(["git", "clone", f"https://blah:blah@github.com/{repo_url}", user_apps_path])
                    if result.returncode == 0:
                        flash("Repo Cloned")
                else:
                    # same as before so just issue a pull to update it.
                    result = subprocess.run(["git", "-C", "pull", user_apps_path])
                    if result.returncode == 0:
                        flash("Repo Updated")
                # run the generate app list for custom repo
                return redirect(url_for('manager.index'))
            
            else:
                flash("No Changes to Repo")
 
            flash("Error Saving Repo")
        return redirect(url_for('auth.edit'))
    abort(404)

@bp.route('/set_system_repo', methods=('GET','POST'))
@login_required
def set_system_repo():
    if request.method == 'POST':
        if g.user['username'] != "admin":
            abort(404)
        if 'app_repo_url' in request.form:
            repo_url = request.form['app_repo_url']
            print(repo_url)
            system_apps_path = "tidbyt-apps"
            old_repo = ""
            if 'system_repo_url' in g.user:
                old_repo = g.user['system_repo_url']
                
            if repo_url != "":
                if old_repo != repo_url:
                    # just get the last two words of the repo
                    repo_url = repo_url.split("/")[-2:]
                    repo_url = "/".join(repo_url)
                    g.user['system_repo_url'] = repo_url
                    db.save_user(g.user)

                    print(system_apps_path)
                    if db.file_exists(system_apps_path):
                        # delete the folder and re-clone.
                        print("deleting tidbyt-apps")
                        subprocess.run(["rm", "-rf", system_apps_path])                        
                    # pull the repo and save to local filesystem.
                    #result = os.system("git clone https://blah:blah@github.com/{} {}".format(repo_url,system_apps_path))
                    result = subprocess.run(["git", "clone", f"https://blah:blah@github.com/{repo_url}", system_apps_path])
                    if result.returncode != 0:
                        flash("Error Cloning Repo")
                    else:
                        flash("Repo Cloned")
                else:
                    # same as before so just issue a pull to update it.
                    result = subprocess.run(["git", "-C", "pull", system_apps_path])
                    if result.returncode == 0:
                        flash("Repo Updated")
                # run the generate app list for custom repo
                os.system("python3 gen_app_array.py") # safe
                return redirect(url_for('manager.index'))
            
            else:
                flash("No Changes to Repo")
 
            flash("Error Saving Repo")
        return redirect(url_for('auth.edit'))
    abort(404)
