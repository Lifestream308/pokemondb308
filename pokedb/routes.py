from lib2to3.pgen2 import token
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from pokedb import app, db, bcrypt
from pokedb.forms import RegistrationForm, LoginForm, PostForm
from pokedb.models import User, Post, users_schema, posts_schema, post_schema
from flask_login import login_user, current_user, logout_user, login_required
from helpers import token_required

# Token API PROTECTED ROUTES
# Create
@app.route('/create_post', methods = ['POST'])
@token_required
def create_post(current_user_token):
    title = request.json['title']
    content = request.json['content']
    author = User.query.filter_by(token=current_user_token.token).first()
    user_token = current_user_token.token

    print(f'BIG TESTER: {current_user_token.token}')

    post = Post(title, content, author, user_token)

    db.session.add(post)
    db.session.commit()

    response = post_schema.dump(post)
    return jsonify(response)

# Retrieve all
@app.route("/getcars", methods=['GET'])
@token_required
def getcars(current_user_token): 
    getposts = Post.query.all()

    print(f'BIG TESTER: {current_user_token.token}')

    result = posts_schema.dump(getposts)
    return jsonify(result)

# Retrieve one
@app.route("/getcars/<id>", methods=['GET'])
@token_required
def getcar(current_user_token, id): 
    getpost = Post.query.get(id)
    return post_schema.jsonify(getpost)

# Update
@app.route('/updatepost/<id>', methods = ['PUT'])
@token_required
def updatepost(current_user_token, id):

    post = Post.query.get(id)

    title = request.json['title']
    content = request.json['content']

    post.title = title
    post.content = content

    print(f'BIG TESTER: {current_user_token.token}')

    db.session.commit()

    return post_schema.jsonify(post)

# Delete
@app.route("/delete/<id>", methods=['Delete'])
@token_required
def delete(current_user_token, id): 
    getpost = Post.query.get(id)

    db.session.delete(getpost)
    db.session.commit()

    return post_schema.jsonify(getpost)

# Start of UNPROTECTED API Routes
@app.route("/getusers", methods=['GET'])
def getusers(): 
    getusers = User.query.all()
    result = users_schema.dump(getusers)
    return jsonify(result)

@app.route("/getposts", methods=['GET'])
def getposts(): 
    getposts = Post.query.all()
    result = posts_schema.dump(getposts)
    return jsonify(result)

@app.route("/getposts/<id>", methods=['GET'])
def getpost(id): 
    getpost = Post.query.get(id)
    return post_schema.jsonify(getpost)

# End API Routes

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=Post.query.all())

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')

# Create, Read, Update, Delete
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, number=form.number.data, content=form.content.data, type=form.type.data, weakness=form.weakness.data, author=current_user, user_token=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Pokemon', form=form, legend='New Pokemon')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Pokemon')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))