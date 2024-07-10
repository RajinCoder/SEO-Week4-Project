from flask import Flask, render_template, url_for, flash, redirect, request
from petfinder import api_query_response, chosen_post_data

app = Flask(__name__)

@app.route("/")
def replace_here():
    return render_template('')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")