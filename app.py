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
        return render_template('post_details.html', post=post)
    else:
        return render_template('error.html')

@app.route('/error')
def error():
    return render_template('error.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
