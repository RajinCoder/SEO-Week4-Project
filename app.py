from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

stored_data = []

@app.route('/')
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

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0" )