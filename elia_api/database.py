import databases
import sqlalchemy

from elia_api.config import config

metadata = sqlalchemy.MetaData()

user_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True),
    sqlalchemy.Column("password", sqlalchemy.String),
)

chat_history_table = sqlalchemy.Table(
    "chat_history",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False),
    sqlalchemy.Column("message", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("is_user", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column("timestamp", sqlalchemy.DateTime, server_default=sqlalchemy.func.now(), nullable=False),
)

DATABASE_URL = config.DATABASE_URL
DB_FORCE_ROLL_BACK = config.DB_FORCE_ROLL_BACK

engine = sqlalchemy.create_engine(DATABASE_URL)

metadata.create_all(engine)

database = databases.Database(DATABASE_URL, force_rollback=DB_FORCE_ROLL_BACK, min_size=1, max_size=5)
