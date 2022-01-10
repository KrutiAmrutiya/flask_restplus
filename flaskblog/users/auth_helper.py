from flaskblog.models import User
from typing import Dict, Tuple
from flask import request, jsonify
import jwt
import datetime
from flaskblog.config import Config
from .utils import json

class Auth:

    @staticmethod
    def login_user():
        try:
            # fetch the user data
            user = User.query.filter_by(username=request.json.get('username')).first()
            if user and request.json.get('password'):
                auth_token = jwt.encode({'public_id': user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, Config.SECRET_KEY)
                if auth_token:
                    print(auth_token)
                    response_object = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'Authorization': auth_token.decode('UTF-8')
                    }
                    return jsonify(response_object)
            else:
                response_object = {
                    'status': 'fail',
                    'message': 'email or password does not match.'
                }
                return response_object, 401

        except Exception as e:
            print(e)
            response_object = {
                'status': 'fail',
                'message': 'Try again'
            }
            return response_object, 500

    @staticmethod
    def logout_user():
        return User.decode_auth_token()
