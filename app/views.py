"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""
import os
import jwt
from functools import wraps
from app import app, db, login_manager
from flask import render_template, request, jsonify, g,send_from_directory, session
from datetime import datetime, timedelta
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf.csrf import generate_csrf
from werkzeug.security import check_password_hash
from app.forms import RegistrationForm, LoginForm, NewPostForm
from werkzeug.utils import secure_filename
from . import db
from app.models import Post,Like,Follow,User
from .config import Config



def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    auth = request.headers.get('Authorization', None) 

    if not auth:
      return jsonify({'code': 'authorization_header_missing', 'description': 'Authorization header is expected'}), 401

    parts = auth.split()

    if parts[0].lower() != 'bearer':
      return jsonify({'code': 'invalid_header', 'description': 'Authorization header must start with Bearer'}), 401
    elif len(parts) == 1:
      return jsonify({'code': 'invalid_header', 'description': 'Token not found'}), 401
    elif len(parts) > 2:
      return jsonify({'code': 'invalid_header', 'description': 'Authorization header must be Bearer + \s + token'}), 401

    token = parts[1]
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])

    except jwt.ExpiredSignatureError:
        return jsonify({'code': 'token_expired', 'description': 'Token is expired'}), 401
    except jwt.DecodeError:
        return jsonify({'code': 'token_invalid_signature', 'description': 'Token signature is invalid'}), 401

    g.current_user = user = payload
    return f(*args, **kwargs)

  return decorated


@app.route('/')
def index():
    return jsonify(message="This is the beginning of our API")
 
@app.route('/api/v1/register', methods=['POST'])
def register():
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        username = registration_form.username.data
        password = registration_form.password.data
        first_name = registration_form.first_name.data
        last_name = registration_form.last_name.data
        email = registration_form.email.data
        location = registration_form.location.data
        bio = registration_form.bio.data
        photo_file = registration_form.photo.data
        joined_on = datetime.utcnow()
        photo_filename = secure_filename(photo_file.filename)
        photo_file.save(os.path.join(Config.UPLOAD_FOLDER, photo_filename))

        user = User(username,password,first_name,last_name,email,location,bio,photo_filename,joined_on)
        db.session.add(user)
        db.session.commit()
        return jsonify({
            "message": "Registration was successful",
            "username": username,
            "password": password,
            "firstname": first_name,
            "lastname": last_name,
            "email": email,
            "location": location,
            "biography": bio,
            "profile_photo": photo_filename,
            "joined_on": joined_on
        }), 201
    errors = form_errors(registration_form)
    return jsonify(errors=errors), 400
 
@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        user = db.session.execute(db.select(User).filter_by(username=username)).scalar()
        if user is not None and check_password_hash(user.password, password):
            login_user(user)
            jwt_token = generate_token(user.id)
            session['jwt_token'] = jwt_token
            return jsonify({
                "message": "Login successful",
                "token": jwt_token,
            }), 200
        return jsonify(errors=["Incorrect credentials"])
    errors = form_errors(login_form)
    return jsonify(errors=errors), 400



@app.route('/api/v1/users/<user_id>', methods=['GET'])
@login_required
@requires_auth
def get_user_info(user_id):
    posts = []
    followers = []
    user_posts = db.session.execute(db.select(Post).filter_by(user_id=int(user_id))).scalars()
    for post in user_posts:
        posts.append({
            "id": post.id,
            "user_id": post.user_id,
            "photo": f"/api/v1/uploads/{post.photo}",
            "description": post.caption,
            "created_on": post.created_on,
        })
    user_followers = db.session.execute(db.select(Follow).filter_by(user_id=int(user_id))).scalars()
    for follower in user_followers:
        followers.append({
            "id": follower.id,
            "follower_id": follower.follower_id,
            "user_id": follower.user_id,
        })

    user_info = db.session.execute(db.select(User).filter_by(id=int(user_id))).scalar()
    return jsonify({
        "id": user_info.id,
        "username": user_info.username,
        "firstname": user_info.firstname,
        "lastname": user_info.lastname,
        "email": user_info.email,
        "location": user_info.location,
        "biography": user_info.biography,
        "profile_photo": f"/api/v1/uploads/{user_info.profile_photo}",
        "joined_on": user_info.joined_on.strftime("%B, %Y"),
        "posts": posts,
        "followers": followers
    }), 200

@app.route('/api/v1/users/<user_id>/posts', methods=['GET'])
@login_required
@requires_auth
def get_posts(user_id):
    user_posts = db.session.execute(db.select(Post).filter_by(user_id=user_id)).scalars()
    posts = []
    for post in user_posts:
        posts.append({
            "id": post.id,
            "user_id": post.user_id,
            "photo": f"/api/v1/posters/{post.photo}",
            "description": post.caption,
            "created_on": post.created_on,
        })
    return jsonify(posts=posts), 200


@app.route('/api/v1/users/<user_id>/posts', methods=['POST'])
@login_required
@requires_auth
def add_post(user_id):
    post_form = NewPostForm()
    if post_form.validate_on_submit():
        photo = post_form.photo.data
        caption = post_form.caption.data
        photo_filename = secure_filename(photo.filename)
        photo.save(os.path.join(Config.UPLOAD_FOLDER, photo_filename))
        created_on = datetime.utcnow()
        post = Post(caption,photo_filename,user_id,created_on)
        db.session.add(post)
        db.session.commit()
        return jsonify({
            "message": "New post was created"
        }), 201
    errors = form_errors(post_form)
    return jsonify(errors=errors), 400


@app.route('/api/v1/posts', methods=['GET'])
@login_required
@requires_auth
def get_all_posts():
    posts = db.session.execute(db.select(Post)).scalars()
    all_posts = []
    for post in posts:
        likes = db.session.execute(db.select(Like).filter_by(post_id=post.id)).scalars()
        likes_lst = []
        for like in likes:
            likes_lst.append({
                "id": like.id,
                "post_id": like.post_id,
                "user_id": like.user_id,
            })
        user = User.query.get(post.user_id)
        all_posts.append({
            "id": post.id,
            "user_id": post.user_id,
            "photo": f"/api/v1/uploads/{post.photo}",
            "caption": post.caption,
            "created_on": post.created_on.strftime("%d %b %Y"),
            "likes": likes_lst,
            "username": user.username
        })
    return jsonify(all_posts), 200


@app.route('/api/v1/posts/<post_id>/like', methods=['POST'])
@login_required
@requires_auth
def like(post_id):
    post = db.session.execute(db.select(Post).filter_by(id=post_id)).scalar()
    if post is not None:
        likes = db.session.execute(db.select(Like).filter_by(post_id=post.id)).scalars()
        if post is not None:
            uid = int(current_user.get_id())
            like = Like(post_id, uid)
            db.session.add(like)
            db.session.commit()
            return jsonify({
                "message": "Post liked",
                "likes": len([like for like in likes]) + 1
            }), 201
         
@app.route('/api/v1/users/<user_id>/follow', methods=['POST'])
@login_required
@requires_auth
def follow(user_id):
    follower_id = int(current_user.get_id())
    user_id = int(user_id)
    if user_id != follower_id:
        follow = Follow(user_id=user_id, follower_id=follower_id)
        db.session.add(follow)
        db.session.commit()
        return jsonify({
            "message": "Followed user.",
            "follwer": follower_id,
            "followed": user_id
        }), 201
    return jsonify({
        "message": "lol you cannot follow yourself"
    }), 400

@app.route('/api/v1/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    session.pop('jwt_token', None)
    return jsonify({
        "message": "Logged out."
    }), 200

def form_errors(form):
    error_messages = []
    """Collects form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            message = u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                )
            error_messages.append(message)

    return error_messages

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


def generate_token(uid):
    timestamp = datetime.utcnow()
    payload = {
        "subject": uid,
        "iat": timestamp,
        "exp": timestamp + timedelta(minutes=20)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

@login_manager.user_loader
def load_user(user_id):
    return db.session.execute(db.select(User).filter_by(id=user_id)).scalar()

@app.route('/api/v1/uploads/<filename>', methods=['GET'])
def get_image(filename):
    return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)


@app.route('/api/v1/csrf-token', methods=['GET'])
def get_csrf():
    return jsonify({'csrf_token': generate_csrf()})

@app.route('/api/v1/jwt-token', methods=['GET'])
def get_jwt_token():
    return jsonify(jwt_token=session.get('jwt_token'))

@app.route('/api/v1/loggedin', methods=['GET'])
def logged_in():
    if current_user.is_authenticated:
        return jsonify(logged_in=True, id=current_user.id)
    else:
        return jsonify(logged_in=False)
    

@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404