from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.db_helpers import (
    execute_query,
    insert_record,
    update_record,
    delete_record,
    fetch_records
)