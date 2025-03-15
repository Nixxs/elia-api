from typing import Dict, Any
from elia_api.utils.database_ops import get_geometry_by_id


async def update_map_data(geometry_id: str) -> Dict[str, Any]:
    """
    Update the map by displaying spatial data stored in the database.

    This function takes a 'geometry_id', retrieves the corresponding GeoJSON FeatureCollection 
    from the database, and sends it to the frontend for display on the map.

    Args:
        geometry_id: The ID of the stored geometry to display. You should reference previously 
                     created or processed geometries by their ID.

    Returns:
        A dictionary containing:
            - geojson: The GeoJSON FeatureCollection to be displayed on the map.

    Notes:
        - You (the AI assistant) should only pass the 'geometry_id', not raw GeoJSON.
        - The retrieved GeoJSON is sent directly to the frontend to update the map and is not 
          returned to you (the AI).
        - Use this function to display any stored geometry (e.g., points, buffers, union results).
    """
    # Retrieve GeoJSON from the database using the provided geometry_id
    geojson = await get_geometry_by_id(geometry_id)

    # Return GeoJSON to the frontend for display
    return {
        "geojson": geojson
    }
