from vsapp.models import User, Post, Comment
from flask import render_template, flash, redirect, url_for, request, abort, jsonify
from vsapp.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from vsapp import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os

# Index
@app.route('/', methods=['POST', 'GET'])
def index():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)

# Registration route
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('feed'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pswd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_pswd)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}. You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('registration.html', title='Register', form=form)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('feed'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            # We use the Ternary Operators for this codnditional
            return redirect(next_page) if next_page else redirect(url_for('feed'))
        else:
            flash('Unsuccessful login, Check credentials.', 'danger')
    return render_template('login.html', title='Login', form=form)
    
# Main feed route
@app.route('/feed', methods=['POST', 'GET'])
def feed():
    if current_user.is_authenticated:
        posts = Post.query.filter(Post.public==True).order_by(Post.date_posted.desc()).all()
    else:
        posts = Post.query.filter_by(public=True).order_by(Post.date_posted.desc()).all()
    for post in posts:
        post.comment = Comment.query.filter_by(post_id=post.id).all()
    image_file = url_for('static', filename='images/' + current_user.image_file)
    return render_template('feed.html', title='Main Feed', image_file=image_file, posts=posts)
    

# Function to change the name of the pictures uploaded and the put them into the images folder
def upload_picture(form_picture):
    hex_rand = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = hex_rand + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

# Profile route
@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = upload_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        db.session.commit()
        flash('Your accout has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    image_file = url_for('static', filename='images/' + current_user.image_file)
    posts = Post.query.filter_by(author=current_user).order_by(Post.date_posted.desc()).all()
    number_posts = len(posts)
    return render_template('profile.html', title='Your Account', image_file=image_file, form=form, posts=posts, number_posts=number_posts)

# Function to upload the post image to the folder and to change it's name to random hex
def upload_picture_post(form_picture):
    hex_rand = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = hex_rand + f_ext
    picture_path = os.path.join(app.root_path, 'static/images/post_images', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

# Creating a new post logic
@app.route('/post_creation', methods=['GET', 'POST'])
@login_required
def new_post():
    image_file = url_for('static', filename='images/' + current_user.image_file)
    form = PostForm()
    if form.validate_on_submit():
        picture_file = upload_picture_post(form.content.data)
        if form.public.data:
            post = Post(title=form.title.data, content=picture_file, author=current_user, public=True)
        else:
            post = Post(title=form.title.data, content=picture_file, author=current_user, public=False)
        db.session.add(post)
        db.session.commit()
        flash('You post has been published', 'success')
        return redirect(url_for('feed'))
    return render_template('post_creation.html', title='Create Post', form=form, legend='New Post', image_file=image_file)

# Creating the page were you can view a single post
@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    image_file = url_for('static', filename='images/' + current_user.image_file)
    return render_template('post.html', title=post.title, post=post, image_file=image_file)

# Editing the post logic
@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    image_file = url_for('static', filename='images/' + current_user.image_file)
    if form.validate_on_submit():
        picture_file = upload_picture_post(form.content.data)
        post.title = form.title.data
        post.content = picture_file
        db.session.commit()
        flash('Changes saved!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
    return render_template('post_creation.html', title='Update Post', form=form, image_file=image_file)

# Deleting the post logic
@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    for comment in post.comments:
        db.session.delete(comment)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted!', 'success')
    return redirect(url_for('feed'))

# Commenting logic
@app.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get(post_id)
    if request.form['comment']:
        comment = Comment(content=request.form['comment'], post=post, author=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added.', 'success')
        return redirect(url_for('feed'))
    else:
        flash('You need to write a comment', 'danger')
        return redirect(url_for('feed'))

# Like logic
@app.route('/like/<int:post_id>', methods=['GET', 'POST'])
def like(post_id):
    if not current_user.is_authenticated:
        return jsonify({'success': False})

    user = User.query.filter_by(id=current_user.id).first()
    post = Post.query.filter_by(id=post_id).first()

    is_liked = post in user.liked_posts
    if is_liked:
        user.liked_posts.remove(post)
        post.like_count -= 1
    else:
        user.liked_posts.append(post)
        post.like_count += 1
    db.session.commit()

    return jsonify({'success': True, 'like_count': post.like_count, 'is_liked': is_liked})




# Logout logic
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))