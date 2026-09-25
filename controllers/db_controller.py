from flask import Blueprint, jsonify
from models.db_helpers import fetch_records


db_bp = Blueprint("db", __name__)


@db_bp.route("/test-db", methods=["GET"])
def test_db():
    try:
        fetch_records("SELECT 1")

        return jsonify({
            "status": "success",
            "message": "Database Connected"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Database Connection Failed",
            "detail": str(e)
        }), 500