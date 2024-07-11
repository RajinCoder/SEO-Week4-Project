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
        session['posts'] = posts
        return jsonify({'redirect': url_for("pets_display")}), 200
    else:
        return jsonify({'message': 'Invalid data format.'}), 400

@app.route('/pets')
def pets_display():
    posts = session.get('posts', [])
    return render_template('pets_display.html', posts=posts)

@app.route('/post/<int:pet_id>')
def post_details(pet_id):
    post = chosen_post_data(pet_id)
    if post:
        return render_template('post_details.html', post=post)
    else:
        return "Post not found", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
