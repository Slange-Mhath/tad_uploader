from tad_uploader import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    password = db.Column(db.String(80))

    def __repr__(self):
        return '<User %r>' % self.username


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contributor_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(500))
    rights = db.Column(db.String(500))
    path = db.Column(db.String(150))

    def __repr__(self):
        return '<Image %r>' % self.title


