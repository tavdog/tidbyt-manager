from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
import flaskr.db as db
import uuid


bp = Blueprint('manager', __name__)

@bp.route('/')
@login_required
def index():
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
#            db = get_db()
            # db.execute(
            #     'INSERT INTO device (name, api_id, api_key, notes, owner_id)'
            #     ' VALUES (?, ?, ?, ?, ?)', (name, api_id, api_key, notes,  g.user['id'])
            # )
            # db.commit()
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

# def get_post(id, check_author=True):
#     post = get_db().execute(
#         'SELECT p.id, title, body, created, owner_id, username'
#         ' FROM post p JOIN user u ON p.owner_id = u.id'
#         ' WHERE p.id = ?',(id,)).fetchone()

#     if post is None:
#         abort(404, "Post id {0} doesn't exist.".format(id))
#     if check_author and post['owner_id'] != g.user['id']:
#         abort(403)
#     return post

# def get_device(id, check_author=True):
#     device = get_db().execute(
#         'SELECT p.id, name, notes, api_id, api_key, created, owner_id, username'
#         ' FROM device p JOIN user u ON p.owner_id = u.id'
#         ' WHERE p.id = ?',
#         (id,)
#     ).fetchone()
#     if device is None:
#         abort(404, "Post id {0} doesn't exist.".format(id))
#     if check_author and device['owner_id'] != g.user['id']:
#         abort(403)
#     return device

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

@bp.route('/<string:id>/addapp', methods=('GET','POST'))
@login_required
def addapp(id):
    if request.method == 'POST':
        name = request.form['name']
        iname = request.form['iname']
        uinterval = request.form['uinterval']
        notes = request.form['notes']
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
            user = g.user
            if "apps" not in user["devices"][id]:
                user["devices"][id]["apps"] = {}
        
            user["devices"][id]["apps"][iname] = app
            db.save_user(user)

            return redirect(url_for('manager.index'))
    return render_template('manager/addapp.html')    

@bp.route('/<string:id>/<string:iname>/updateapp', methods=('GET','POST'))
@login_required
def updateapp(id,iname):
    if request.method == 'POST':
        name = request.form['name']
        #iname = request.form['iname']
        uinterval = request.form['uinterval']
        notes = request.form['notes']
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
            user = g.user
        
            user["devices"][id]["apps"][iname] = app
            db.save_user(user)

            return redirect(url_for('manager.index'))
    app = g.user["devices"][id]['apps'][iname]
    return render_template('manager/updateapp.html', app=app)    

@bp.route('/<string:id>/<string:iname>/configapp', methods=('GET','POST'))
@login_required
def configapp(id,iname):
    import subprocess
    app = g.user["devices"][id]['apps'][iname]

    if request.method == 'POST':
        pass
    #   do something to confirm configuration ?

    
    # execute the pixlet serve process and then redirect to it
    subprocess.Popen(["bash", "pixlet_serve.sh {} {}".format(app['name'], app['iname'])], shell=True)
    return render_template('manager/configapp.html', app=app)


