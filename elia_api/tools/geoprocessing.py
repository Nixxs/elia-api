import requests
from elia_api.tools.registry import register_backend_function
from elia_api.config import config
import json
from typing import Dict, Any
from elia_api.utils.database_ops import store_geometry

# NOTE: when you are making functions, just remember the LLM doesn't seem to like complex data structures as params
# also any function can ask for a map_data: str param this is inject automatically from chat.py and is always sent as part 
# of the prompt.

@register_backend_function("buffer_features")
async def buffer_features(distance: float, units: str, map_data: str, user_id: int = None) -> Dict[str, Any]:
    """
    Buffer spatial features currently displayed on the map by a specified distance.

    This function takes spatial data from the current map (provided automatically as GeoJSON), 
    applies a buffer operation using the Geoflip API, stores the buffered result, and returns 
    a 'geometry_id' for future reference.

    Args:
        distance: The buffer distance to apply (e.g., 100 for 100 meters).
        units: The units for the buffer distance (e.g., "meters", "kilometers", "miles", "feet").
        map_data: [Provided automatically] Current map data (GeoJSON FeatureCollection as a JSON string).
        user_id: [Provided automatically] The ID of the user performing this action.

    Returns:
        A dictionary containing:
            - geometry_id: A new ID representing the buffered geometry.

    Example:
        buffer_features(distance=100, units="meters", map_state={...})

    Notes:
        - The 'map_data' argument is injected automatically; you do not need to ask for it.
        - The output is stored and returned as a 'geometry_id' for use in future operations.
        - To display the result on the map, use 'update_map_data' with the new 'geometry_id'.
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

            # Store buffered geometry and return geometry_id
            new_geometry_id = await store_geometry(buffered_geojson, user_id=user_id)
            return {"geometry_id": new_geometry_id}

        else:
            return {
                "error": "Failed to buffer data via Geoflip API.",
                "status_code": response.status_code,
                "details": response.text
            }

    except requests.RequestException as e:
        return {"error": "Request to Geoflip API failed.", "details": str(e)}

@register_backend_function("union_features")
async def union_features(map_data: str, user_id: int = None) -> Dict[str, Any]:
    """
    Union spatial features currently displayed on the map into a single combined geometry.

    This function takes spatial data from the current map (provided automatically as GeoJSON),
    performs a union operation to merge overlapping or touching geometries using the Geoflip API,
    stores the unioned result, and returns a 'geometry_id' for future reference.

    Args:
        map_data: [Provided automatically] Current map data (GeoJSON FeatureCollection as a JSON string).
        user_id: [Provided automatically] The ID of the user performing this action (optional, for ownership tracking).

    Returns:
        A dictionary containing:
            - geometry_id: A new ID representing the unioned geometry.

    Example:
        union_features(map_state={...})

    Notes:
        - 'map_data' is injected automatically; you do not need to ask for it.
        - The output is stored and returned as a 'geometry_id' for use in future operations.
        - To display the result on the map, use 'update_map_data' with the 'geometry_id' and specify whether to 'add' or 'replace'.
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

            # Store unioned geometry and return geometry_id
            new_geometry_id = await store_geometry(unioned_geojson, user_id=user_id)
            return {"geometry_id": new_geometry_id}

        else:
            return {
                "error": "Failed to union data via Geoflip API.",
                "status_code": response.status_code,
                "details": response.text
            }

    except requests.RequestException as e:
        return {"error": "Request to Geoflip API failed.", "details": str(e)}
    
@register_backend_function("lat_long_to_geojson")
async def lat_long_to_geojson(latitude: float, longitude: float, label: str, user_id: int = None) -> Dict[str, Any]:
    """
    Create a point feature from latitude and longitude, and store it as a geometry for later use.

    This function generates a GeoJSON point using the provided latitude, longitude, and label, stores it in the geometry database, and returns a 'geometry_id' for future reference.

    The 'geometry_id' is used to reference spatial data in other operations (e.g., buffer, union) without handling raw GeoJSON.

    Args:
        latitude: Latitude of the point.
        longitude: Longitude of the point.
        label: A label to store as a property.
        user_id: [Provided automatically] Used to link geometry to the user.

    Returns:
        A dictionary with:
            - geometry_id: ID of the stored geometry.

    Example:
        lat_long_to_geojson(latitude=-31.9505, longitude=115.8605, label="Perth City")

    Notes:
        - Always use the returned 'geometry_id' to reference this geometry in future operations.
        - This does not update the map — use 'update_map_data' if needed.
    """

    # GeoJSON FeatureCollection structure
    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]  # [lon, lat] as per GeoJSON standard
                },
                "properties": {
                    "label": label
                }
            }
        ]
    }

    # Store in geometries table and return the geometry ID
    geometry_id = await store_geometry(feature_collection, user_id=user_id)

    return {
        "geometry_id": geometry_id
    }
