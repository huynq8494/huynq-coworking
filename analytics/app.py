import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from flask import jsonify, request
from sqlalchemy import and_, text
from random import randint

from config import app, db


port_number = int(os.environ.get("APP_PORT", 5153))

class Token(db.Model):
    __tablename__ = "tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True, unique=False, nullable=False)
    token = db.Column(db.String(6), index=True, unique=False, nullable=False)
    created_at = db.Column(db.DateTime, index=False, unique=False, nullable=False, default=datetime.now())
    used_at = db.Column(db.DateTime, index=True, unique=False, nullable=True)


@app.route("/health_check")
def health_check():
    return "ok"


@app.route("/readiness_check")
def readiness_check():
    try:
        count = db.session.query(Token).count()
    except Exception as e:
        app.logger.error(e)
        return "failed", 500
    else:
        return "ok"


def get_daily_visits():
    with app.app_context():
        result = db.session.execute(text("""
        SELECT Date(created_at) AS date,
            Count(*)         AS visits
        FROM   tokens
        WHERE  used_at IS NOT NULL
        GROUP  BY Date(created_at)
        """))

        response = {}
        for row in result:
            response[str(row[0])] = row[1]

        app.logger.info(response)

    return response


@app.route("/api/reports/daily_usage", methods=["GET"])
def daily_visits():
    return jsonify(get_daily_visits)


@app.route("/api/reports/user_visits", methods=["GET"])
def all_user_visits():
    result = db.session.execute(text("""
    SELECT t.user_id,
        t.visits,
        users.joined_at
    FROM   (SELECT tokens.user_id,
                Count(*) AS visits
            FROM   tokens
            GROUP  BY user_id) AS t
        LEFT JOIN users
                ON t.user_id = users.id;
    """))

    response = {}
    for row in result:
        response[row[0]] = {
            "visits": row[1],
            "joined_at": str(row[2])
        }

    return jsonify(response)


scheduler = BackgroundScheduler()
job = scheduler.add_job(get_daily_visits, 'interval', seconds=30)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port_number)
