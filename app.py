from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leaderboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model
class Score(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    diff = db.Column(
        db.Integer,
        nullable=False
    )

    attempts = db.Column(
        db.Integer,
        default=0
    )
# Create database
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template("index.html")
@app.route('/check-user/<name>')
def check_user(name):

    existing = Score.query.filter_by(name=name).first()

    if existing:

        remaining = 2 - existing.attempts

        return jsonify({
            "exists": True,
            "attempts_left": remaining
        })

    return jsonify({
        "exists": False,
        "attempts_left": 2
    })

# Save score
@app.route('/submit-score', methods=['POST'])
def submit_score():

    data = request.get_json()

    name = data['name']
    diff = data['diff']

    existing = Score.query.filter_by(name=name).first()

    # Existing player
    if existing:

        # Limit attempts
        if existing.attempts >= 2:

            return jsonify({
                "message": "No attempts remaining"
            }), 403

        # Increase attempts
        existing.attempts += 1

        # Save only best score
        if diff < existing.diff:
            existing.diff = diff

        db.session.commit()

        return jsonify({
            "message": "Score updated",
            "best_diff": existing.diff,
            "attempts": existing.attempts
        })

    # New player
    new_score = Score(
        name=name,
        diff=diff,
        attempts=1
    )

    db.session.add(new_score)

    db.session.commit()

    return jsonify({
        "message": "New player added"
    })
# Get leaderboard
@app.route('/leaderboard')
def leaderboard():

    scores = Score.query \
        .order_by(Score.diff.asc()) \
        .limit(10) \
        .all()

    result = []

    for score in scores:

        result.append({
            "name": score.name,
            "diff": score.diff
        })

    return jsonify(result)
if __name__ == '__main__':
    app.run(debug=True)