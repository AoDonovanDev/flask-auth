from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
""" from secret import secret """
from forms import RegisterForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = secret
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

app.app_context().push()
connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home():
    return redirect('/register')

@app.route('/users/<username>')
def secret(username):
    if 'user_id' not in session:
        flash('must log in')
        return redirect('/')
    user = User.query.filter(User.username == username).first()
    return render_template('user_detail.html', user=user)

@app.route('/register', methods=['get', 'post'])
def register():

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data

        user = User.register(username, password, first_name, last_name, email)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id

        return redirect(f'/users/{username}')

    return render_template('register.html', form=form)

@app.route('/login', methods=['get', 'post'])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        session['user_id'] = user.id
        return redirect(f'/users/{username}')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/login')

@app.route('/users/<username>/delete', methods=['post'])
def delete_user(username):
    user = User.query.filter(User.username == username).first()
    if session['user_id'] != user.id:
        flash('you cant do that')
        return redirect('/')
    db.session.delete(user)
    db.session.commit()
    session.pop('user_id')
    return redirect('/')

@app.route('/users/<username>/feedback/add', methods=['get', 'post'])
def add_feedback(username):
    user = User.query.filter(User.username == username).first()
    form = FeedbackForm()
    if session['user_id'] != user.id:
        flash('what are you trying to do')
        return redirect('/')
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        fb = Feedback(title=title, content=content, username=user.username)
        db.session.add(fb)
        db.session.commit()
        return redirect(f'/users/{user.username}')
    return render_template('feedback.html', form=form)

@app.route('/feedback/<int:fb_id>/update', methods=['get', 'post'])
def update_feedback(fb_id):
    feedback = Feedback.query.get(fb_id)
    user = User.query.filter(User.username == feedback.username).first()
    form = FeedbackForm()
    if session['user_id'] != user.id:
        flash('stop that')
        return redirect('/')
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.add(feedback)
        db.session.commit()
        return redirect(f'/users/{user.username}')
    return render_template('update_feedback.html', form=form)

@app.route('/feedback/<int:fb_id>/delete', methods=['post'])
def delete_feedback(fb_id):
    feedback = Feedback.query.get(fb_id)
    user = User.query.filter(User.username == feedback.username).first()
    if session['user_id'] != user.id:
        flash('stop that')
        return redirect('/')
    db.session.delete(feedback)
    db.session.commit()
    return redirect(f'/users/{user.username}')