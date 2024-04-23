from datetime import datetime, timedelta
from time import time

from flask import current_app, url_for
import jwt
from sqlalchemy import delete, select
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class Updateable:
    def update(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)


user_lab_table = db.Table('user_lab',
                          db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                          db.Column('user_name', db.String(64)),
                          db.Column('lab_id', db.Integer, db.ForeignKey('labs.id'), primary_key=True),
                          db.Column('lab_name', db.String(64)),
                          db.Column('role', db.String(50))
                          )


class Lab(db.Model):
    __tablename__ = 'labs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True)
    type = db.Column(db.String(255))
    users = db.relationship(
        "User",
        secondary=user_lab_table,
        back_populates="labs"
    )


class User(db.Model, Updateable):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), index=True, unique=True)
    email = db.Column(db.String(255), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    first_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    tokens = db.relationship("Token", back_populates="user", lazy='dynamic')
    role = db.Column(db.String(50), default='guest')
    labs = db.relationship(
        "Lab",
        secondary=user_lab_table,
        back_populates="users"
    )

    def __repr__(self):  # pragma: no cover
        return '<User {}>'.format(self.username)

    @property
    def url(self):
        return url_for('users.get', id=self.id)

    @property
    def has_password(self):
        return self.password_hash is not None

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @property
    def lab_roles(self):
        return {lab.name: role for lab, role in self.labs}

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        if self.password_hash:  # pragma: no branch
            return check_password_hash(self.password_hash, password)

    def ping(self):
        self.last_seen = datetime.utcnow()

    def generate_auth_token(self, expires_in=None):
        token = Token(user=self)
        token.generate(expires_in=expires_in)

        return token

    def generate_user_token(self, expires_in=None, name="Default"):
        token = Token(user=self)
        expires_in = datetime.utcnow() + timedelta(days=expires_in)
        token.generate(expires_in=expires_in, generated_by_user=True, name=name)

        return token

    @staticmethod
    def verify_access_token(access_token_jwt):
        try:
            # payload = jwt.decode(access_token_jwt, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            token = Token.query.filter_by(access_token=access_token_jwt).first()
            if token and token.access_expiration > datetime.utcnow():
                token.user.ping()
                return token.user
        except jwt.ExpiredSignatureError as e:
            current_app.logger.error(f"Token expired: {e}")
            return None  # Token is expired
        except jwt.InvalidTokenError as e:
            current_app.logger.error(f"Invalid token: {e}")
            return None  # Token is invalid

    @staticmethod
    def verify_refresh_token(refresh_token, access_token_jwt):
        token = Token.query.filter_by(access_token=access_token_jwt).first()
        if token and token.refresh_token == refresh_token:
            if token.refresh_expiration > datetime.utcnow():
                return token
            current_app.logger.debug(f"Refresh Token expired date: {token.refresh_expiration}")

            # someone tried to refresh with an expired token
            # revoke all tokens for the front end user
            token.user.revoke_all()
            db.session.commit()

    def revoke_all(self):
        db.session.execute(delete(Token)
                           .where(Token.user == self and not Token.generated_by_user))
        db.session.commit()

    def generate_reset_token(self):
        return jwt.encode(
            {
                'exp': time() + current_app.config['RESET_TOKEN_MINUTES'] * 60,
                'reset_email': self.email,
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_reset_token(reset_token):
        try:
            data = jwt.decode(reset_token, current_app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except jwt.PyJWTError:
            return
        return db.session.scalar(select(User).filter_by(
            email=data['reset_email']))

    @staticmethod
    def check_permissions(user, role="admin"):
        return user.role == role


class Token(db.Model, Updateable):
    __tablename__ = 'tokens'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True)
    access_token = db.Column(db.String(512), index=True)
    access_expiration = db.Column(db.DateTime)
    refresh_token = db.Column(db.String(512), index=True)
    refresh_expiration = db.Column(db.DateTime)
    generated_by_user = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    user = db.relationship("User", back_populates="tokens")

    def generate(self, expires_in=None, generated_by_user=False, name="Default"):
        self.name = name
        self.generated_by_user = generated_by_user
        current_app.logger.debug(f"expires_in: {expires_in}")

        if not expires_in:
            expires_in_min = current_app.config['ACCESS_TOKEN_MINUTES']
            expires_in = datetime.utcnow() + timedelta(minutes=expires_in_min)
            refresh_expires_in_days = current_app.config['REFRESH_TOKEN_DAYS']
            refresh_expires_in = datetime.utcnow() + timedelta(days=refresh_expires_in_days)
        else:
            refresh_expires_in = expires_in + timedelta(days=1)

        current_app.logger.debug(f"expires_in: {expires_in} minutes, refresh_expires_in: {refresh_expires_in} days")

        self.access_token = jwt.encode({
            'uid': self.user_id,
            'exp': expires_in,
            'iat': datetime.utcnow(),
            'role': self.user.role,
            'labs': self.user.lab_roles
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        self.access_expiration = expires_in

        self.refresh_token = jwt.encode({
            'user_id': self.user_id,
            'exp': refresh_expires_in,
            'type': 'refresh'
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        self.refresh_expiration = refresh_expires_in

        current_app.logger.debug(f"Generated token: {self.access_token} and "
                                 f"refresh token: {self.refresh_token} for user: {self.user_id}")

    def expire(self, delay=None):
        if delay is None:  # pragma: no branch
            # 5 second delay to allow simultaneous requests
            delay = 5 if not current_app.testing else 0
        self.access_expiration = datetime.utcnow() + timedelta(seconds=delay)
        self.refresh_expiration = datetime.utcnow() + timedelta(seconds=delay)
        db.session.commit()

    @staticmethod
    def clean():
        """Remove any tokens that have been expired for more than a day."""
        yesterday = datetime.utcnow() - timedelta(days=1)
        db.session.execute(delete(Token).where(Token.refresh_expiration < yesterday))
        db.session.commit()

    @staticmethod
    def from_jwt(access_token_jwt):
        try:
            payload = jwt.decode(access_token_jwt, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return Token.query.filter_by(access_token=access_token_jwt).first()
        except jwt.InvalidTokenError as e:
            current_app.logger.error(f"Invalid token: {e}")
            return None
