from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from forms import RegistrationForm, LoginForm
from models import db, User, login_manager
from flask_bcrypt import Bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from flask_cors import CORS, cross_origin
from modules.petfinder import api_query_response, chosen_post_data
import os
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config.from_object('config.Config')

db.init_app(app)
login_manager.init_app(app)
bcrypt = Bcrypt(app)

app.secret_key = os.urandom(24)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

@app.route('/submit', methods=['POST'])
@cross_origin()
def submit():
    if request.is_json:
        data = request.get_json()
        print(data)
        posts = api_query_response(data['species'], data['location'], data['geo_range'], data['sex'], data['age'], data['special_ability'], data['size'], data['allergies'])
        if not posts:  # Check if no posts were found
            return jsonify({'redirect': url_for("error")}), 200
        session['posts'] = posts
        session['species'] = data['species']
        session['age'] = data['age']
        session['size'] = data['size']
        return jsonify({'redirect': url_for("load_info")}), 200
    else:
        return jsonify({'message': 'Invalid data format.'}), 400

@app.route('/search-info')
def load_info():
    posts = session.get('posts', [])
    species = session.get('species', '').capitalize()
    age = session.get('age', '').capitalize()
    size = session.get('size', '')
    if size == 1:
        size = "Small 25 lbs (11 kg) or less"
    elif size == 2:
        size = "Med. 26-60 lbs (12-27 kg)"
    elif size == 3:
        size = "Large 61-100 lbs (28-45 kg)"
    elif size == 4:
        size = "X-Large 101 lbs (46 kg) or more"
    else:
        size = "Any"
    if not posts:
        return render_template('error.html')
    return render_template('search_info.html', species=species, age=age, size=size)

@app.route('/pets')
def pets_display():
    posts = session.get('posts', [])
    if not posts:  # Check if no posts were found
        return redirect(url_for("index"))
        # ^ would this be error.html?
    return render_template('pets_display.html', posts=posts)

@app.route('/post/<string:pet_id>')
def post_details(pet_id):
    post = chosen_post_data(pet_id)
    if post:
        favorites = session.get('favorites', {})
        is_favorited = str(pet_id) in favorites
        return render_template('post_details.html', post=post, is_favorited=is_favorited)
    else:
        return render_template('error.html', error='pet', error_message=random.choice([ "Oops! This one is playing fetch and hasn't come back yet.", "Purr-haps this one wandered off chasing a mouse.", "This one is still chasing its tail.", "Looks like this one took a nap in the sun.", "Uh-oh! This one has gone for a walk.", "This one is on a squirrel chase."]))

@app.before_request
def ensure_favorites_in_session():
    if 'favorites' not in session:
        session['favorites'] = {}

@app.route('/favorites')
def favorites_page():
    favorites = session.get('favorites', {})
    return render_template('favorites_page.html', favorites=favorites)

@app.route('/favorite/<int:pet_id>', methods=['POST'])
def add_favorite(pet_id):
    pet_data = request.json

    print("Received JSON data:", pet_data)

    petID = pet_data['pet_id']
    pet_details = pet_data['pet_details']

    print("Pet ID from JSON:", petID)
    print("Pet Details from JSON:", pet_details)

    if 'favorites' not in session:
        session['favorites'] = {}

    print("Current favorites in session:", session['favorites'])

    if petID in session['favorites']:
        return jsonify(status='Already in favorites')

    session['favorites'][petID] = pet_details
    session.modified = True

    print("Updated favorites in session:", session['favorites'])

    return jsonify(status='success')

@app.route('/favorite/<int:pet_id>', methods=['DELETE'])
def remove_favorite(pet_id):
    data = request.get_json()
    petID = data.get('pet_id')

    if 'favorites' not in session:
        session['favorites'] = {}
        print("no favorites yet")
        return jsonify(status='No favorites yet.')

    elif petID not in session['favorites']:
        print("current favorites:", session['favorites'])
        return jsonify(status='Post not in favorites.')

    del session['favorites'][petID]
    session.modified = True

    print("Updated favorites in session:", session['favorites'])
    return jsonify(status='success')


@app.route('/error')
def error():
    return render_template('error.html')

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
            session['id'] = user.id
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
    app.run(debug=True, host='0.0.0.0', port=5000)