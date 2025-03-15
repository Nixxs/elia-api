from typing import Dict, Any
from elia_api.utils.database_ops import get_geometry_by_id


async def update_map_data(geometry_id: str, type: str) -> Dict[str, Any]:
    """
    Update the map by displaying spatial data stored in the database.

    This function takes a 'geometry_id', retrieves the corresponding GeoJSON FeatureCollection 
    from the database, and sends it to the frontend for display on the map. The 'type' parameter 
    controls whether to add this data to the existing map or replace all current data.

    Args:
        geometry_id: The ID of the stored geometry to display. You should reference previously 
                     created or processed geometries by their ID.
        type: How to handle the map update. Must be 'add' to add to existing map data, or 'replace'
                    to clear the map before adding new data. Defaults to 'replace'.

    Returns:
        A dictionary containing:
            - geojson: The GeoJSON FeatureCollection to be displayed on the map.
            - type: The operation type ('add' or 'replace') to inform how the frontend should handle the display.

    Notes:
        - You (the AI assistant) should only pass the 'geometry_id' and 'type'.
        - The GeoJSON is handled and displayed by the frontend — it is not returned to you (the AI).
        - Use 'add' to keep existing data and overlay the new geometry, or 'replace' to clear the map first.
    """
    # Retrieve GeoJSON from the database using the provided geometry_id
    geojson = await get_geometry_by_id(geometry_id)

    # Return GeoJSON and type to the frontend for display
    return {
        "geojson": geojson,
        "type": type  # 'add' or 'replace' to control map behavior
    }
