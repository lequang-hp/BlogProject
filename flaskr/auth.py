import functools
# from mydb import getConnection
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for 
)
from werkzeug.security import check_password_hash, generate_password_hash
import pymysql.cursors

bp = Blueprint('auth',__name__, url_prefix="/auth")

def getConnection():
    conn = pymysql.connect(host='localhost',
        user='root',
        password='123456',
        db='blog',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)
    return conn

# Require Authentication in other views
def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        db = getConnection().cursor()
        db.execute("SELECT * FROM user WHERE id = %s", (user_id,))
        g.user = db.fetchone()
        

@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        
        conn = getConnection()
        db = conn.cursor()

        if not username:
            error = "Username is required"
        elif not password:
            error = "Password is required"
        elif(db.execute("SELECT id FROM user WHERE username = %s",(username,)) != 0):
            error = "User {0} is already exists".format(username)

        if error is None:
            try:
                db.execute(
                            "INSERT INTO user(username,password) VALUES(%s,%s)",
                            (username,generate_password_hash(password)),
                        )
                conn.commit()
            except Exception as e:
                print("Exception occured:{}".format(e))
                conn.rollback()
            finally:
                conn.close()
            return redirect(url_for("auth.login"))
        
        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    conn = getConnection()
    db = conn.cursor()

    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = getConnection().cursor()
        error = None
        db.execute(
            "SELECT * FROM user WHERE username = %s", (username,)
        )
        user = db.fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user['password'], password):
            print(user['password'])
            error = "Incorrect password."

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user['id']
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))