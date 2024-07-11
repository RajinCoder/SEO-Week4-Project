from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
from models import db, User, login_manager
from flask_bcrypt import Bcrypt
from flask_login import login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
login_manager.init_app(app)
bcrypt = Bcrypt(app)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Email address already registered. Please use a different email.', 'danger')
            return redirect(url_for('register'))

        # If username and email are unique, proceed with registration
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created successfully!', 'success')
        return redirect(url_for('login'))

    # If form validation fails, render the registration form with error messages
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Check if user exists
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')

    # If form validation fails or login is unsuccessful, render the login form with error messages
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/home")
@login_required
def home():
    return "Welcome to your home page!"

if __name__ == '__main__':
    app.run(debug=True)
