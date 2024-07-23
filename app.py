from flask import Flask, render_template, request, jsonify, url_for, redirect, session
from flask_cors import CORS, cross_origin
from modules.petfinder import api_query_response, chosen_post_data
import os
import random

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
        return redirect(url_for("index"))
    return render_template('pets_display.html', posts=posts)

@app.route('/post/<string:pet_id>')
def post_details(pet_id):
    post = chosen_post_data(pet_id)
    if post:
        return render_template('post_details.html', post=post)
    else:
        return render_template('error.html', error='pet', error_message=random.choice([ "Oops! This one is playing fetch and hasn't come back yet.", "Purr-haps this one wandered off chasing a mouse.", "This one is still chasing its tail.", "Looks like this one took a nap in the sun.", "Uh-oh! This one has gone for a walk.", "This one is on a squirrel chase."]))


@app.route('/error')
def error():
    return render_template('error.html')

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error_message=random.choice([ "Oops! This page is playing fetch and hasn't come back yet.", "Purr-haps this page wandered off chasing a mouse.", "This page is still chasing its tail.", "The cat's got this page's tongue.", "Looks like this page took a nap in the sun.", "Uh-oh! This page has gone for a walk.", "Our server took this page out for a walk.", "This page is on a squirrel chase.", "The internet ate my homework...and this page." ]))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
