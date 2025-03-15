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
    sqlalchemy.Column("role", sqlalchemy.String, nullable=False),  # "user", "model", "function"
    sqlalchemy.Column("message", sqlalchemy.Text, nullable=False),  # Can be plain text or JSON
    sqlalchemy.Column("timestamp", sqlalchemy.DateTime, server_default=sqlalchemy.func.now(), nullable=False),
)

geometry_table = sqlalchemy.Table(
    "geometries",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),  # UUID or short string IDs
    sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=True),  # Optional for ownership tracking
    sqlalchemy.Column("geometry", sqlalchemy.JSON, nullable=False),  # Full GeoJSON with geometry + attributes
    sqlalchemy.Column("timestamp", sqlalchemy.DateTime, server_default=sqlalchemy.func.now(), nullable=False)  # Consistent naming
)

DATABASE_URL = config.DATABASE_URL
DB_FORCE_ROLL_BACK = config.DB_FORCE_ROLL_BACK

engine = sqlalchemy.create_engine(DATABASE_URL)

metadata.create_all(engine)

database = databases.Database(DATABASE_URL, force_rollback=DB_FORCE_ROLL_BACK, min_size=1, max_size=5)
