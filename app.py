from flask import Flask, render_template, request, jsonify, url_for, redirect, session
from flask_cors import CORS, cross_origin
from petfinder import api_query_response, chosen_post_data
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
        posts = api_query_response(data['location'], data['geo_range'], data['sex'], data['age'], data['special_ability'])
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
        session['favorites'] = []

# method is get, post, both, or none?
@app.route('/favorites')
def favorites_page():
    favorites = session.get('favorites', [])

    return render_template('favorites_page.html', favorites=favorites)


@app.route('/favorite/<int:pet_id>', methods=['POST'])
def add_favorite(pet_id):
    # Retrieve the list of favorites from session, or initialize it if it doesn't exist
    favorites = session.get('favorites', [])
    
    # Add the pet_id to the favorites list if it's not already there
    if pet_id not in favorites:
        favorites.append(pet_id)
        session['favorites'] = favorites  # Update the session with the updated favorites list
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
