from flask import request, jsonify
import functools


def get_user_from_request(req):
    try:
        return req.user
    except:
        return None


def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):

        user = get_user_from_request(request)
        if user is None:
            return jsonify({'error': 'You do not have permission to perform this action'}), 400

        return f(*args, **kwargs)
    return decorated_function
