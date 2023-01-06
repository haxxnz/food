from flask_login import UserMixin
import sqlalchemy as sa

from data import db


class User(db.Model, UserMixin):
    id = sa.Column(sa.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = sa.Column(sa.String(100), unique=True)
    password = sa.Column(sa.String(200))
    display_name = sa.Column(sa.String(100))
    registered_date_utc = sa.Column(sa.DateTime)