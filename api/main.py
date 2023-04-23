from flask import Flask, request, abort
from utils.db import get_db_client
from flask_cors import CORS
from utils.logger import log
from bson.json_util import dumps
from models.users import UsersModel, User
from models.subscriptions import UserSubscriptions, SubsModel
from utils.exceptions import NotAuthorized
from middleware.require_auth import require_auth

app = Flask(__name__)
CORS(app)
db = get_db_client()

log.info("Server running on http://localhost:8080")


@app.get("/")
def healthcheck():
    log.debug("Hit healthcheck endpoint")
    return {"version": "1.0.0"}


@app.post("/users")
def create_user():
    body = request.json or {}
    try:
        users = UsersModel()
        res = users.create(User(**body))
        return res.dict()
    except Exception as e:
        log.error(f"Error during creating a user: {str(e)}")
        return abort(500)


@app.post("/login")
def login():
    body = request.json or {}
    try:
        users = UsersModel()
        email = body.get("email", "")
        password = body.get("password", "")
        if not email and not password:
            raise NotAuthorized("Bad Login")
        res = users.login(email, password)
        return res.dict(include={"access_token": True})
    except NotAuthorized as e:
        log.error(str(e))
        abort(e.status_code)
    except Exception as e:
        log.error(f"Error during login: {str(e)}")
        abort(401)


@app.get("/news")
def find_news():
    try:
        limit = request.args.get("limit", default=10, type=int)
        offset = request.args.get("offset", default=0, type=int)
        start_date = request.args.get("start_date", type=float)
        end_date = request.args.get("end_date", type=float)
        category_id = request.args.get("category_id", type=int)
        institution_id = request.args.get("institution_id", type=int)
        query = {}
        date_config = {}
        if start_date:
            date_config["$gte"] = start_date
        if end_date:
            date_config["$lte"] = end_date
        if start_date and end_date:
            query["date"] = date_config
        if category_id:
            query["category_id"] = category_id
        if institution_id:
            query["institution_id"] = institution_id
        found_news = db.filozofski.find(query, {"_id": 0}).limit(limit).skip(offset)
        return dumps(found_news)
    except Exception as e:
        log.error(f"Error: {str(e)}")
        abort(500)


@app.post("/subscriptions")
@require_auth
def create_subscription(user: User):
    body = request.json or {}
    try:
        subs = SubsModel()
        body["user_id"] = user.id
        res = subs.create(UserSubscriptions(**body))
        return res.dict()
    except Exception as e:
        log.error(f"Error during subscribing to category: {str(e)}")
        return abort(500)


@app.get("/subscriptions")
def find_subscriptions():
    try:
        limit = request.args.get("limit", default=5, type=int)
        offset = request.args.get("offset", default=0, type=int)
        found_subs = (
            db.subs.find({}, {"_id": 0})
            .sort([("updated_at", -1)])
            .limit(limit)
            .skip(offset)
        )
        return dumps(found_subs)
    except Exception as e:
        log.error(f"Error: {str(e)}")
        abort(500)

@app.get("/categories")
def get_categories():
    try:
        limit = request.args.get("limit", default=20, type=int)
        offset = request.args.get("offset", default=0, type=int)
        found_cats = db.categories.find({}, {"_id": 0}).limit(limit).skip(offset)
        return dumps(found_cats)
    except Exception as e:
        log.error(f"Error: {str(e)}")
        abort(500)

if __name__ == "__main__":
    # This server is only for local/debug
    app.run(port=8080, debug=True)
