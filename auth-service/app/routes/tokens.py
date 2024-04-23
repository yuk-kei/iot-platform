from flask import Blueprint, request, abort, current_app, url_for, session
from sqlalchemy import select
from werkzeug.http import dump_cookie
from apifairy import authenticate, body, response, other_responses

from app import db

from app.middleware.auth import basic_auth, token_auth

from app.models.models import User, Token

from app.schemas.schemas import TokenSchema, PasswordResetRequestSchema, \
    PasswordResetSchema, OAuth2Schema, EmptySchema, UserTokenGenSchema, ResetUserPasswordSchema, UserTokenSchema

tokens = Blueprint('tokens', __name__)
token_schema = TokenSchema()
oauth2_schema = OAuth2Schema()
user_token_gen_schema = UserTokenGenSchema()
user_token_schema = UserTokenSchema()


def token_response(token):
    headers = {}
    if current_app.config['REFRESH_TOKEN_IN_COOKIE']:
        samesite = 'strict'
        if current_app.config['USE_CORS']:  # pragma: no branch
            samesite = 'none' if not current_app.debug else 'lax'
        headers['Set-Cookie'] = dump_cookie(
            'refresh_token', token.refresh_token,
            path=url_for('tokens.new'), secure=not current_app.debug,
            httponly=True, samesite=samesite)
    print(f"access_token: {token.access_token}", f"refresh_token: {token.refresh_token}")
    return {
        'access_token': token.access_token,
        'refresh_token': token.refresh_token if current_app.config['REFRESH_TOKEN_IN_BODY'] else None,
    }, 200, headers


@tokens.route('/tokens', methods=['POST'])
@authenticate(basic_auth)
@response(token_schema)
@other_responses({401: 'Invalid username or password'})
def new():
    """Create new login tokens

    The refresh token is returned in the body of the request or as a hardened
    cookie, depending on configuration. A cookie should be used when the
    client is running in an insecure environment such as a web browser, and
    cannot adequately protect the refresh token against unauthorized access.
    """
    user = basic_auth.current_user()
    token = user.generate_auth_token()
    db.session.add(token)
    Token.clean()  # keep token table clean of old tokens
    db.session.commit()
    return token_response(token)


@tokens.route('/user-tokens', methods=['POST'])
@authenticate(token_auth)
@body(user_token_gen_schema)
@response(user_token_schema)
@other_responses({401: 'Invalid username or password'})
def create_user_token(args):
    """Create new api access tokens

    The api access token is returned in the body of the request, it should be created by the user
    with a name and an expiration date in days (e g. 30), the range is between 1 and 365 days.
    """
    user = token_auth.current_user()
    token = user.generate_user_token(expires_in=args.get('expires_in'), name=args.get('name'))
    db.session.add(token)
    Token.clean()  # keep token table clean of old tokens
    db.session.commit()
    return token_response(token)


@tokens.route('/tokens', methods=['PUT'])
@body(token_schema)
@response(token_schema, description='Newly issued access and refresh tokens')
@other_responses({401: 'Invalid access or refresh token'})
def refresh(args):
    """Refresh an access token

    The client can pass the refresh token in the body of the request or in a `refresh_token` cookie.
    The access token must be passed in the body of the request.
    """
    access_token_jwt = args['access_token']
    refresh_token = args.get('refresh_token', request.cookies.get(
        'refresh_token'))
    current_app.logger.debug(f"access_token: {access_token_jwt}, refresh_token: {refresh_token}")
    if not access_token_jwt or not refresh_token:
        abort(401)
    token = User.verify_refresh_token(refresh_token, access_token_jwt)
    if not token:
        abort(401)
    token.expire()
    new_token = token.user.generate_auth_token()
    db.session.add_all([token, new_token])
    db.session.commit()
    return token_response(new_token)


@tokens.route('/tokens', methods=['DELETE'])
@authenticate(token_auth)
@response(EmptySchema, status_code=204, description='Token revoked')
@other_responses({401: 'Invalid access token'})
def revoke():
    """Revoke an access token"""
    access_token_jwt = request.headers['Authorization'].split()[1]
    token = Token.from_jwt(access_token_jwt)
    if not token:  # pragma: no cover
        abort(401)
    token.expire()
    db.session.commit()
    return {}

# @tokens.route('/tokens/reset', methods=['POST'])
# @body(PasswordResetRequestSchema)
# # @response(EmptySchema, status_code=204,
# #           description='Password reset email sent')
# def reset(args):
#     """Request a password reset token"""
#     user = db.session.scalar(select(User).filter_by(email=args['email']))
#     if user is not None:
#         reset_token = user.generate_reset_token()
#         reset_url = current_app.config['PASSWORD_RESET_URL'] + '?token=' + reset_token
#
#         # send_email(args['email'], 'Reset Your Password', 'reset',
#         #            username=user.username, token=reset_token, url=reset_url)
#     return {"reset_url": reset_url}


# @tokens.route('/tokens/reset', methods=['PUT'])
# @body(PasswordResetSchema)
# @response(EmptySchema, status_code=204,
#           description='Password reset successful')
# @other_responses({400: 'Invalid reset token'})
# def password_reset(args):
#     """Reset a user password"""
#     user = User.verify_reset_token(args['token'])
#     if user is None:
#         abort(400)
#     user.password = args['new_password']
#     db.session.commit()
#     return {}
