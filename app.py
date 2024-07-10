from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from petfinder import api_query_response, chosen_post_data
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={r"/submit": {"origins": "*"}})

stored_data = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])  
def submit():
    if request.is_json:
        data = request.get_json()
        # Process your data here
        stored_data.append(data)  

        return jsonify({'message': 'Data submitted successfully!'}), 200
    else:
        return jsonify({'message': 'Invalid data format.'}), 400

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
