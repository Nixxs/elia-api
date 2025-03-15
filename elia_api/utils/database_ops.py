import uuid
from elia_api.database import database, geometry_table

async def store_geometry(geojson_data: dict, user_id: int = None) -> str:
    geometry_id = str(uuid.uuid4())

    query = geometry_table.insert().values(
        id=geometry_id,
        user_id=user_id,
        geometry=geojson_data
    )

    await database.execute(query)
    return geometry_id

async def get_geometry_by_id(geometry_id: str) -> dict:
    query = geometry_table.select().where(geometry_table.c.id == geometry_id)
    row = await database.fetch_one(query)
    if row:
        return row["geometry"]
    else:
        raise ValueError(f"Geometry ID {geometry_id} not found.")
