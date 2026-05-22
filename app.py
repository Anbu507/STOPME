from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leaderboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database models
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

    attempt1_diff = db.Column(
        db.Integer,
        nullable=True
    )

    attempt2_diff = db.Column(
        db.Integer,
        nullable=True
    )

    attempts = db.Column(
        db.Integer,
        default=0
    )


class FlappyScore(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    score = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    attempt1_score = db.Column(
        db.Integer,
        nullable=True
    )

    attempt2_score = db.Column(
        db.Integer,
        nullable=True
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
    name_clean = name.strip().lower()
    existing = Score.query.filter_by(name=name_clean).first()

    if existing:

        remaining = 2 - existing.attempts

        return jsonify({
            "exists": True,
            "attempts_left": remaining,
            "attempt1_diff": existing.attempt1_diff,
            "attempt2_diff": existing.attempt2_diff,
            "best_diff": existing.diff
        })

    return jsonify({
        "exists": False,
        "attempts_left": 2,
        "attempt1_diff": None,
        "attempt2_diff": None,
        "best_diff": None
    })


# Get player rank
def get_player_rank(player_diff):

    scores = Score.query \
        .order_by(Score.diff.asc()) \
        .all()

    for index, score in enumerate(scores):

        if score.diff == player_diff:
            return index + 1

    return -1


# Save score
@app.route('/submit-score', methods=['POST'])
def submit_score():

    data = request.get_json()

    name = data['name'].strip().lower()
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

        if existing.attempts == 2:
            existing.attempt2_diff = diff
        else:
            if existing.attempt1_diff is None:
                existing.attempt1_diff = diff
            else:
                existing.attempt2_diff = diff

        # Save only best score
        if diff < existing.diff:
            existing.diff = diff

        db.session.commit()

        rank = get_player_rank(existing.diff)

        return jsonify({
            "message": "Score updated",
            "best_diff": existing.diff,
            "attempt1_diff": existing.attempt1_diff,
            "attempt2_diff": existing.attempt2_diff,
            "attempts": existing.attempts,
            "rank": rank,
            "total_players": Score.query.count()
        })

    # New player
    new_score = Score(
        name=name,
        diff=diff,
        attempt1_diff=diff,
        attempts=1
    )

    db.session.add(new_score)

    db.session.commit()

    rank = get_player_rank(diff)

    return jsonify({
        "message": "New player added",
        "best_diff": diff,
        "attempt1_diff": diff,
        "attempt2_diff": None,
        "attempts": 1,
        "rank": rank,
        "total_players": Score.query.count()
    })


# Get leaderboard
@app.route('/leaderboard')
def leaderboard():

    scores = Score.query \
        .order_by(Score.diff.asc()) \
        .all()

    result = []

    for index, score in enumerate(scores):

        result.append({
            "rank": index + 1,
            "name": score.name,
            "diff": score.diff
        })

    return jsonify(result)


# Flappy Bird endpoints

@app.route('/check-flappy-user/<name>')
def check_flappy_user(name):
    name_clean = name.strip().lower()
    existing = FlappyScore.query.filter_by(name=name_clean).first()

    if existing:
        remaining = 2 - existing.attempts
        return jsonify({
            "exists": True,
            "attempts_left": remaining,
            "attempt1_score": existing.attempt1_score,
            "attempt2_score": existing.attempt2_score,
            "best_score": existing.score
        })

    return jsonify({
        "exists": False,
        "attempts_left": 2,
        "attempt1_score": None,
        "attempt2_score": None,
        "best_score": None
    })


def get_flappy_player_rank(player_score):
    scores = FlappyScore.query \
        .order_by(FlappyScore.score.desc()) \
        .all()

    for index, s in enumerate(scores):
        if s.score == player_score:
            return index + 1
    return -1


@app.route('/submit-flappy-score', methods=['POST'])
def submit_flappy_score():
    data = request.get_json()
    name = data['name'].strip().lower()
    score_val = data['score']

    existing = FlappyScore.query.filter_by(name=name).first()

    if existing:
        if existing.attempts >= 2:
            return jsonify({
                "message": "No attempts remaining"
            }), 403

        existing.attempts += 1

        if existing.attempts == 2:
            existing.attempt2_score = score_val
        else:
            if existing.attempt1_score is None:
                existing.attempt1_score = score_val
            else:
                existing.attempt2_score = score_val

        # Save best score (higher score is better)
        if score_val > existing.score:
            existing.score = score_val

        db.session.commit()
        rank = get_flappy_player_rank(existing.score)

        return jsonify({
            "message": "Score updated",
            "best_score": existing.score,
            "attempt1_score": existing.attempt1_score,
            "attempt2_score": existing.attempt2_score,
            "attempts": existing.attempts,
            "rank": rank,
            "total_players": FlappyScore.query.count()
        })

    new_score = FlappyScore(
        name=name,
        score=score_val,
        attempt1_score=score_val,
        attempts=1
      )

    db.session.add(new_score)
    db.session.commit()
    rank = get_flappy_player_rank(score_val)

    return jsonify({
        "message": "New player added",
        "best_score": score_val,
        "attempt1_score": score_val,
        "attempt2_score": None,
        "attempts": 1,
        "rank": rank,
        "total_players": FlappyScore.query.count()
    })


@app.route('/flappy-leaderboard')
def flappy_leaderboard():
    scores = FlappyScore.query \
        .order_by(FlappyScore.score.desc()) \
        .all()

    result = []
    for index, s in enumerate(scores):
        result.append({
            "rank": index + 1,
            "name": s.name,
            "score": s.score
        })

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)