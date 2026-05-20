from flask import Flask, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/user')
def user():
    data = {
        "name": "Anbu",
        "age": 20,
        "skill": "Python"
    }
    return jsonify(data)

@app.route('/users')
def users():
    data = [
        {
            "name": "Anbu",
            "age": 20,
            "skill": "Python"
        },
        {
            "name": "John",
            "age": 25,
            "skill": "JavaScript"
        },
        {
            "name": "Alice",
            "age": 30,
            "skill": "Java"
        }
    ]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)