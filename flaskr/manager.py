from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
import flaskr.db as db


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
            device["name"] = name
            device["api_id"] = api_id
            device["api_key"] = api_key
            device["notes"] = notes
            user = g.user
            if "devices" not in user:
                user["devices"] = {}
            user["devices"][name] = device
            db.save_user(user)

            return redirect(url_for('manager.index'))
    return render_template('manager/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, owner_id, username'
        ' FROM post p JOIN user u ON p.owner_id = u.id'
        ' WHERE p.id = ?',(id,)).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))
    if check_author and post['owner_id'] != g.user['id']:
        abort(403)
    return post

def get_device(id, check_author=True):
    device = get_db().execute(
        'SELECT p.id, name, notes, api_id, api_key, created, owner_id, username'
        ' FROM device p JOIN user u ON p.owner_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()
    if device is None:
        abort(404, "Post id {0} doesn't exist.".format(id))
    if check_author and device['owner_id'] != g.user['id']:
        abort(403)
    return device

@bp.route('/<string:name>/update', methods=('GET', 'POST'))
@login_required
def update(name):
    if request.method == 'POST':
        name = request.form['name']
        notes = request.form['notes']
        api_id = request.form['api_id']
        api_key = request.form['api_key']
        error = None
        if not name:
            error = 'Name is required.'
        if error is not None:
            flash(error)
        else:
            device = dict()
            device["name"] = name
            device["api_id"] = api_id
            device["api_key"] = api_key
            device["notes"] = notes
            
            user = g.user
            user["devices"][name] = device
            db.save_user(user)

            return redirect(url_for('manager.index'))
    device = g.user["devices"][name]
    return render_template('manager/update.html', device=device)

@bp.route('/<string:name>/delete', methods=('POST',))
@login_required
def delete(name):
    g.user["devices"].pop(name)
    db.save_user(g.user)
    return redirect(url_for('manager.index'))