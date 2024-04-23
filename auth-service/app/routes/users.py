from apifairy.decorators import other_responses
from flask import Blueprint, abort
from apifairy import authenticate, body, response
from sqlalchemy import select
from app import db
from app.models.models import User
from app.schemas.schemas import UserSchema, UpdateUserSchema, EmptySchema, ResetUserPasswordSchema
from app.middleware.auth import token_auth
from app.middleware.paginated import paginated_response

users = Blueprint('users', __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
update_user_schema = UpdateUserSchema(partial=True)


@users.route('/users', methods=['POST'])
@body(user_schema)
@response(user_schema, 201)
def new(args):
    """Register a new user"""
    user = User(**args)
    db.session.add(user)
    db.session.commit()
    return user


@users.route('/users', methods=['GET'])
@authenticate(token_auth)
@paginated_response(users_schema)
def all():
    """Retrieve all users"""
    return select(User)


@users.route('/users/<int:id>', methods=['GET'])
@authenticate(token_auth)
@response(user_schema)
@other_responses({404: 'User not found'})
def get(id):
    """Retrieve a user by id"""
    return db.session.get(User, id) or abort(404)


@users.route('/users/<username>', methods=['GET'])
@authenticate(token_auth)
@response(user_schema)
@other_responses({404: 'User not found'})
def get_by_username(username):
    """Retrieve a user by username"""
    return db.session.scalar(select(User).filter_by(username=username)) or abort(404)


@users.route('/me', methods=['GET'])
@authenticate(token_auth)
@response(user_schema)
def me():
    """Retrieve the authenticated user"""
    return token_auth.current_user()


@users.route('/me', methods=['PUT'])
@authenticate(token_auth)
@body(update_user_schema)
@response(user_schema)
def put(data):
    """Edit user information"""
    user = token_auth.current_user()
    if 'password' in data and ('old_password' not in data or
                               not user.verify_password(data['old_password'])):
        abort(400)
    user.update(data)
    db.session.commit()
    return user


@users.route('/users/reset-password', methods=['PUT'])
@authenticate(token_auth)
@body(ResetUserPasswordSchema)
@response(EmptySchema, status_code=204,
          description='Password reset successful')
@other_responses({400: 'You do not have permission to reset the password'})
def password_reset(args):
    """Admin Reset a user's password"""
    current_user = token_auth.current_user()
    user_permission = User.check_permissions(current_user, role="admin")
    if user_permission is None:
        abort(400)
    target_user = db.session.scalar(select(User).filter_by(username=args['username']))
    target_user.password = args['new_password']
    db.session.commit()
    return {}
