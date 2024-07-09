from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

stored_data = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():

    question1 = request.form.get('question1')
    question2 = request.form.get('question2')
    question3 = request.form.get('question3')


    stored_data.append({
        'question1': question1,
        'question2': question2,
        'question3': question3

    })

    return redirect(url_for('index')) 

if __name__ == '__main__':
    app.run(debug=True)
