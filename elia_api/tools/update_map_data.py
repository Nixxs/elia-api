from typing import Dict, Any

def update_map_data(geojson: str) -> Dict[str, Any]:
    """
    Prepare GeoJSON geometry to be sent to the front-end for map updates.

    Args:
        geojson: A valid GeoJSON FeatureCollection as a string.

    Returns:
        A dictionary containing GeoJSON to update the map.
    """
    # You could also validate the geojson here if needed
    return {
        "geojson": geojson
    }