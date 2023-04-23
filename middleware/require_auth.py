from functools import wraps
import jwt
from flask import request
from config import Config
from models.users import UsersModel


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return {
                "message": "access_token missing in Authorization header",
                "error": "Unauthorized",
            }, 401
        try:
            decoded = jwt.decode(token, Config.jwt_secret_key, algorithms=["HS256"])
            users = UsersModel()
            current_user = users.get(decoded["id"])
            if current_user is None:
                return {
                    "message": "Invalid Authentication token!",
                    "data": None,
                    "error": "Unauthorized",
                }, 401
            # if not current_user["active"]:
            #     abort(403)
        except Exception as e:
            return {
                "message": "Something went wrong",
                "error": str(e),
            }, 500
        return f(current_user, *args, **kwargs)

    return decorated
