from flask import Flask, request, abort
from utils.db import get_db_client
from flask_cors import CORS
from utils.logger import log
from bson.json_util import dumps

app = Flask(__name__)
CORS(app)
db = get_db_client()

log.info("Server running on http://localhost:8080")


@app.get("/")
def healthcheck():
    log.debug("Hit healthcheck endpoint")
    return {"version": "1.0.0"}


@app.get("/news")
def get_news():
    try:
        limit = request.args.get("limit", default=5, type=int)
        offset = request.args.get("offset", default=0, type=int)
        news_find = db.filozofski.find().limit(limit).skip(offset)
        return dumps(news_find)
    except Exception as e:
        log.error(f"Error: {str(e)}")
        abort(500)


if __name__ == "__main__":
    # This server is only for local/debug
    app.run(port=8080, debug=True)
