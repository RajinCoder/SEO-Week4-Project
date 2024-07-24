from flask import Flask, render_template, request, jsonify, url_for, redirect, session
from flask_cors import CORS, cross_origin
from modules.petfinder import api_query_response, chosen_post_data
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')

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
    if not posts:
        return render_template('error.html')
    return render_template('pets_display.html', posts=posts)

@app.route('/post/<int:pet_id>')
def post_details(pet_id):
    post = chosen_post_data(pet_id)
    if post:
        favorites = session.get('favorites', {})
        is_favorited = str(pet_id) in favorites
        return render_template('post_details.html', post=post, is_favorited=is_favorited)
    else:
        return render_template('error.html')
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

@app.route('/logout')
def logout():
    # logout_user()
    # logic for logging out here
    return redirect(url_for('index'))

@app.route('/error')
def error():
    return render_template('error.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
