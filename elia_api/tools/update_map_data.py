from typing import Dict, Any


def update_map_data(geojson: str) -> Dict[str, Any]:
    """
    Pass a valid GeoJSON FeatureCollection as a string. Do not wrap it in lists or add extra characters.
    
    Args:
        geojson: A stringified GeoJSON FeatureCollection.

    Returns:
        A dictionary containing the GeoJSON.
    """
    return {
        "geojson": geojson
    }
