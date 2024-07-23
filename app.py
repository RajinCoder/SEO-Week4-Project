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
        return jsonify({'redirect': url_for("pets_display")}), 200
    else:
        return jsonify({'message': 'Invalid data format.'}), 400

@app.route('/pets')
def pets_display():
    posts = session.get('posts', [])
    if not posts:  # Check if no posts were found
        return render_template('error.html')
    return render_template('pets_display.html', posts=posts)

@app.route('/post/<int:pet_id>')
def post_details(pet_id):
    post = chosen_post_data(pet_id)
    if post:
        return render_template('post_details.html', post=post)
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

@app.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    # should i be using chosen_pet_data?
    data = request.get_json()
    pet_id = data.get('pet_id')

    # call helper
    if remove_from_favorites(pet_id):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False}), 400

def remove_from_favorites(pet_id):
    # remove pet from favorites logically!! (from database)
    pass

@app.route('/error')
def error():
    return render_template('error.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
