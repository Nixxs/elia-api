import requests
from elia_api.tools.registry import register_backend_function
from elia_api.config import config
from geojson import Feature, FeatureCollection
import json
from typing import Dict, Any
from shapely import wkt
from shapely.geometry import mapping

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
    Convert latitude and longitude into a GeoJSON FeatureCollection as a string for map updates.

    Args:
        latitude: Latitude of the point.
        longitude: Longitude of the point.
        label: A label to add as a property to the feature.
        map_data: Current map data (provided automatically).

    Returns:
        A dictionary containing a GeoJSON FeatureCollection as a string.
    """

    # GeoJSON dict (manually)
    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]  # Note: [lon, lat] order for GeoJSON
                },
                "properties": {
                    "label": label
                }
            }
        ]
    }

    # Proper JSON string (compact, no line breaks)
    geojson_str = json.dumps(feature_collection, separators=(",", ":"))

    return {
        "geojson": geojson_str
    }



@register_backend_function("wkt_to_geojson")
def wkt_to_geojson(rows: str, map_data: str = "") -> Dict[str, Any]:
    """
    Convert a list of WKT geometries and their properties (passed as a JSON string) into a GeoJSON FeatureCollection.

    Args:
        rows: A JSON string of a list of dictionaries, each containing 'wkt' and optional properties.
              Example: '[{"wkt": "POINT(115.8575 -31.9505)", "name": "Location A"}, {"wkt": "POINT(115.8605 -31.9525)", "name": "Location B"}]'
        map_data: Current map data (provided automatically, not needed here).

    Returns:
        A dictionary with 'geojson' key containing the GeoJSON FeatureCollection as a string, this can be used later
        with update_map_data() to draw the data to the map for the user.

    Notes:
        - AI should pass a simple JSON string list of objects with 'wkt' and any other properties.
        - This output is ready to be used in update_map_data().
    """

    try:
        rows_list = json.loads(rows)  # Parse JSON string

        features = []
        for idx, row in enumerate(rows_list):
            if "wkt" not in row:
                return {"error": f"Row at index {idx} is missing 'wkt' key."}

            try:
                geom = wkt.loads(row["wkt"])  # Convert WKT to Shapely geometry
                geojson_geom = mapping(geom)  # Convert to GeoJSON format

                # Remove 'wkt' from properties
                properties = {k: v for k, v in row.items() if k != "wkt"}

                feature = Feature(geometry=geojson_geom, properties=properties)
                features.append(feature)

            except Exception as e:
                return {"error": f"Failed to parse WKT at row {idx}: {str(e)}"}

        feature_collection = FeatureCollection(features)
        geojson_str = json.dumps(feature_collection)  # Return as string for frontend

        return {"geojson": geojson_str}

    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in 'rows'. Must be a valid JSON string list of objects."}