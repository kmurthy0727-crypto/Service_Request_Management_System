import os
from urllib.parse import quote_plus

from flask import Flask
from dotenv import load_dotenv

from models import db
from controllers.main_controller import main_bp
from controllers.db_controller import db_bp

load_dotenv(override=True)


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    mysql_user = os.getenv("MYSQL_USER")
    mysql_password = os.getenv("MYSQL_PASSWORD")
    mysql_host = os.getenv("MYSQL_HOST")
    mysql_port = os.getenv("MYSQL_PORT")
    mysql_db = os.getenv("MYSQL_DB")

    encoded_password = quote_plus(mysql_password)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{mysql_user}:{encoded_password}"
        f"@{mysql_host}:{mysql_port}/{mysql_db}"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(db_bp)
    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)