from typing import Dict, Any

def update_map_data(geojson: str) -> Dict[str, Any]:
    """
    Prepare GeoJSON geometry to be sent to the front-end for map updates, you should almost alway run this anytime the user
    has asked you to do a spatial operation (ie buffer, union etc..) or even just if they asked you to draw points or something.

    Args:
        geojson: A valid GeoJSON FeatureCollection as a string.

    Returns:
        A dictionary containing GeoJSON to update the map.
    """
    # You could also validate the geojson here if needed
    return {
        "geojson": geojson
    }