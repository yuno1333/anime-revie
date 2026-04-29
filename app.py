from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    anime_title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    rating = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(300))


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        room_name = request.form['room']
        return redirect(f'/room/{room_name}')
    return render_template('home.html')

@app.route('/room/<name>', methods=['GET', 'POST'])
def room(name):
    room = Room.query.filter_by(name=name).first()

    if not room:
        room = Room(name=name)
        db.session.add(room)
        db.session.commit()

    if request.method == 'POST':
        username = request.form['username']
        anime_title = request.form['anime']
        content = request.form['content']
        rating = int(request.form['rating'])

        # 🔥 AUTO FETCH IMAGE
        try:
            response = requests.get(
                f"https://api.jikan.moe/v4/anime?q={anime_title}&limit=1"
            )
            data = response.json()
            image_url = data['data'][0]['images']['jpg']['image_url']
        except:
            image_url = None  # fallback if API fails

        new_review = Review(
            username=username,
            anime_title=anime_title,
            content=content,
            rating=rating,
            image_url=image_url,
            room_id=room.id
        )

        db.session.add(new_review)
        db.session.commit()
        return redirect(f'/room/{name}')

    reviews = Review.query.filter_by(room_id=room.id)\
        .order_by(Review.date_created.desc()).all()

    return render_template('room.html', room=name, reviews=reviews)
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)