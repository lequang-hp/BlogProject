# from mydb import getConnection
from flask import(
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
import pymysql.cursors

bp = Blueprint('blog',__name__)

def getConnection():
    conn = pymysql.connect(host='localhost',
        user='root',
        password='123456',
        db='blog',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)
    return conn

@bp.route("/")
def index():
    conn = getConnection()
    db = conn.cursor()
    
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    )
    posts = db.fetchall()
    for post in posts:
        print(post['username'])
    return render_template('blog/index.html', posts = posts)

@bp.route("/create", methods = ['GET','POST'])
@login_required
def create():
    if(request.method == 'POST'):
        title = request.form['title']
        body = request.form['body']
        error = None
        if not title:
            error = "Title is required"
        
        if error is not None:
            flash(error)
        else:
            connection = getConnection()
            db = connection.cursor()
            db.execute(
                'INSERT INTO post(title, body, author_id)'
                ' VALUES(%s,%s,%s)',
                (title, body, g.user['id'])
            )
            connection.commit()
            return redirect(url_for('index'))
    return render_template('blog/create.html')

def get_post(id,check_author = True):
    db = getConnection().cursor()
    db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = %s', 
        (id,)
    )
    post = db.fetchone()

    if post is None:
        abort(404,"Post id {0} is not exists".format(id))
    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route("/<int:id>/update",methods=['GET','POST'])
@login_required
def update(id):
    post = get_post(id)
    if(request.method == 'POST'):
        title = request.form['title']
        body = request.form['body']
        error = None
        if(error is not None):
            flash(error)
        else:
            conn = getConnection()
            db = conn.cursor()
            db.execute(
                'UPDATE post SET title = %s, body = %s'
                ' WHERE id = %s',
                (title,body,id)
            )
            conn.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/update.html',post = post)

@bp.route("/<int:id>/delete",methods = ['POST'])
@login_required
def delete(id):
    conn = getConnection()
    db = conn.cursor()
    db.execute(
        'DELETE FROM post WHERE id = %s',(id,)
    )
    conn.commit()
    return redirect(url_for('blog.index'))
    