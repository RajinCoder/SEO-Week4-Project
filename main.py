from flask import Flask, render_template, url_for, flash, redirect, request

app = Flask(__name__)
proxied = FlaskBehindProxy(app)

@app.route("/")
def replace_here():
    return render_template('')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")