import requests
from elia_api.tools.registry import register_backend_function
from elia_api.config import config
from geojson import Feature, Point, FeatureCollection
import json
from typing import Dict, Any

# NOTE: when you are making functions, just remember the LLM doesn't seem to like complex data structures as params

@register_backend_function("buffer_features")
def buffer_features(distance: float, units: str, map_data: str ):
    """
    Buffer spatial features by a specified distance.

    This function takes spatial data currently displayed on the map (as GeoJSON) and buffers
    the geometries by the specified distance and units. It uses the Geoflip API to perform
    the buffering and returns the resulting GeoJSON FeatureCollection.

    Args:
        distance: The buffer distance to apply (e.g., 100 for 100 meters).
        units: The units for the buffer distance can be one of "meters", "kilometers", "miles", or "feet"
        map_data: Current map data this is provided automatically

    Returns:
        A he buffered GeoJSON FeatureCollection under the key "geojson" as a string so you can call update_map_data to update the map for the user.
        If no spatial data is provided, or if an error occurs, returns an error message.

    Example:
        buffer_features(distance=100, units="meters", map_state={...})

    Notes:
        - The `map_data` argument is supplied automatically by the system.
        - You (the AI) do not need to ask the user for this value.
        - The output is always returned in GeoJSON format (EPSG:4326).
        - This function is intended to be called by the AI assistant to perform geoprocessing operations.
    """

    try:
        # Parse map_data from string to dict
        input_geojson = json.loads(map_data)
    except json.JSONDecodeError:
        return {
            "error": "Invalid map_data format. Expected valid GeoJSON FeatureCollection as JSON string."
        }

    # Prepare Geoflip API payload
    geoflip_payload = {
        "input_geojson": input_geojson,
        "output_format": "geojson",
        "output_crs": "EPSG:4326",
        "transformations": [
            {
                "type": "buffer",
                "distance": distance,
                "units": units
            }
        ]
    }

    try:
        # Make request to Geoflip API
        response = requests.post(
            f"{config.GEOFLIP_API_URL}/v1/transform/geojson",
            json=geoflip_payload,
            headers={"apiKey": config.GEOFLIP_API_KEY}
        )

        # Handle response
        if response.status_code == 200:
            buffered_geojson = response.json()
            return {"geojson": json.dumps(buffered_geojson)}
        else:
            return {
                "error": "Failed to buffer data via Geoflip API.",
                "status_code": response.status_code,
                "details": response.text
            }

    except requests.RequestException as e:
        return {"error": "Request to Geoflip API failed.", "details": str(e)}

@register_backend_function("union_features")
def union_features(map_data: str):
    """
    Union spatial features into a single combined geometry.

    This function takes spatial data currently displayed on the map (as GeoJSON) and performs
    a union operation to merge overlapping or touching geometries into a single geometry.
    It uses the Geoflip API to perform the union and returns the resulting GeoJSON FeatureCollection.
    you will probably need to call the update_map_data after doing this to the user's map reflects the change
    unless you need to follow up with something else

    Args:
        map_data: Current map data provided automatically (GeoJSON FeatureCollection as a JSON string).

    Returns:
        A GeoJSON FeatureCollection under the key "geojson" as a string so you can call update_map_data to update the map for the user.
        If no spatial data is provided, or if an error occurs, returns an error message.

    Example:
        union_features(map_state={...})

    Notes:
        - The `map_data` argument is supplied automatically by the system.
        - You (the AI) do not need to ask the user for this value.
        - The output is always returned in GeoJSON format (EPSG:4326).
        - This function is intended to be called by the AI assistant to perform geoprocessing operations.
    """

    try:
        # Parse map_data from string to dict
        input_geojson = json.loads(map_data)
    except json.JSONDecodeError:
        return {
            "error": "Invalid map_data format. Expected valid GeoJSON FeatureCollection as JSON string."
        }

    # Prepare Geoflip API payload
    geoflip_payload = {
        "input_geojson": input_geojson,
        "output_format": "geojson",
        "output_crs": "EPSG:4326",
        "transformations": [
            {
                "type": "union"
            }
        ]
    }

    try:
        # Make request to Geoflip API
        response = requests.post(
            f"{config.GEOFLIP_API_URL}/v1/transform/geojson",
            json=geoflip_payload,
            headers={"apiKey": config.GEOFLIP_API_KEY}
        )

        # Handle response
        if response.status_code == 200:
            unioned_geojson = response.json()
            return {"geojson": json.dumps(unioned_geojson)}
        else:
            return {
                "error": "Failed to union data via Geoflip API.",
                "status_code": response.status_code,
                "details": response.text
            }

    except requests.RequestException as e:
        return {"error": "Request to Geoflip API failed.", "details": str(e)}


@register_backend_function("lat_long_to_geojson")
def lat_long_to_geojson(latitude: float, longitude: float, label: str, map_data: str) -> Dict[str, Any]:
    """
    Convert latitude and longitude into a GeoJSON FeatureCollection, 
    wrapping a Point geometry in a FeatureCollection to maintain 
    consistent structure expected by the frontend. Use this when you have only a point
    and want to call the update_map_data

    Args:
        latitude: Latitude of the point.
        longitude: Longitude of the point.
        map_data: Current map data this is provided automatically

    Returns:
        A dictionary containing a GeoJSON FeatureCollection as a string.
    """
    # Create a GeoJSON Point Feature
    point_feature = Feature(
        geometry=Point((longitude, latitude)),
        properties={
            "label": label
        }  # Add properties if needed
    )

    # Wrap the feature in a FeatureCollection
    feature_collection = FeatureCollection([point_feature])

    # Convert FeatureCollection to JSON string for frontend compatibility
    geojson_str = json.dumps(feature_collection)

    return {
        "geojson": geojson_str
    }
