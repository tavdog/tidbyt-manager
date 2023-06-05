from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('manager', __name__)

@bp.route('/')
def index():
    db = get_db()
    devices = db.execute(
        'SELECT p.id, name, notes, api_id, api_key , owner_id, username, created'
        ' FROM device p JOIN user u ON p.owner_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
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
            db = get_db()
            db.execute(
                'INSERT INTO device (name, api_id, api_key, notes, owner_id)'
                ' VALUES (?, ?, ?, ?, ?)', (name, api_id, api_key, notes,  g.user['id'])
            )
            db.commit()
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

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    device = get_device(id)
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
            db = get_db()
            db.execute(
                'UPDATE device SET name = ?, api_id = ?, api_key = ?, notes = ? WHERE id = ?', 
                (name, api_id, api_key, notes, id)
            )
            db.commit()
            return redirect(url_for('manager.index'))
    return render_template('manager/update.html', device=device)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_device(id)
    db = get_db()
    db.execute('DELETE FROM device WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('manager.index'))