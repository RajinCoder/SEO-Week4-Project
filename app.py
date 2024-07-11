from flask import Flask, render_template, request, redirect, url_for, flash
from forms import RegistrationForm, LoginForm
from models import db, User, login_manager
from flask_bcrypt import Bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from petfinder import api_query_response, chosen_post_data

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
login_manager.init_app(app)
bcrypt = Bcrypt(app)

stored_data = []


with app.app_context():
    db.create_all()

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.is_json:
        data = request.get_json()
        question1 = data.get('question1')
        question2 = data.get('question2')
        question3 = data.get('question3')

        stored_data.append({
            'question1': question1,
            'question2': question2,
            'question3': question3
        })

        return jsonify({'message': 'Data submitted successfully!'}), 200
    else:
        return jsonify({'message': 'Invalid data format.'}), 400

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Email address already registered. Please use a different email.', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created successfully!', 'success')
        return redirect(url_for('login'))

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
            return redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')

    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0" )