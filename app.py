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
        print(f'Size1: {data['size']}')
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

# method is get, post, both, or none?
@app.route('/favorites')
def favorites_page():
    # conflicted b/t doing list of nested dicts or dict of dict
    # favorites = session.get('favorites', [])
    favorites = session.get('favorites', {})
    return render_template('favorites_page.html', favorites=favorites)


@app.route('/favorite/<int:pet_id>', methods=['POST'])
def add_favorite(pet_id):
    #  have all pets automatically be in this large dictionary? --> waste of space
    # would i need a database in this case?
    pet_data = request.json

    print("Received JSON data:", pet_data)

    # maybe get instead?
    petID = pet_data['pet_id']
    pet_details = pet_data['pet_details']

    print("Pet ID from JSON:", petID)
    print("Pet Details from JSON:", pet_details)
    
    # favorites = session.get('favorites', [])


    if 'favorites' not in session:
        session['favorites'] = {}

    print("Current favorites in session:", session['favorites'])

    if petID in session['favorites']:
        return jsonify(status='Already in favorites')
    
    session['favorites'][petID] = pet_details
    session.modified = True

    # for favorite in session['favorites']:
    #     if favorite['pet_id'] == pet_data['pet_id']:
    #         return jsonify(status='already_exists')
    
    # session['favorites'].append(pet_data)

    # session['favorites'][pet_id] = pet_details
    
    # Add the pet_id to the favorites list if it's not already there
    # if pet_id not in favorites:
    #     favorites.append(pet_id)
    #     session['favorites'] = favorites  # Update the session with the updated favorites list
    # print(f"Updated favorites list: {session['favorites']}")
    print("Updated favorites in session:", session['favorites'])

    return jsonify(status='success')
    # return redirect(url_for('pets_display'))

@app.route('/favorite/<int:pet_id>', methods=['DELETE'])
def remove_favorite(pet_id):
    # should i be using chosen_pet_data?
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
    # # call helper
    # if remove_from_favorites(pet_id):
    #     return jsonify({'success': True})
    # else:
    #     return jsonify({'success': False}), 400

# def remove_from_favorites(pet_id):
#     # remove pet from favorites logically!! (from database)
#     pass

@app.route('/error')
def error():
    return render_template('error.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
