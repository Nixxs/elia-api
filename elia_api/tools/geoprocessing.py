import requests
from elia_api.tools.registry import register_backend_function
from elia_api.config import config

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
        A dictionary containing the buffered GeoJSON FeatureCollection under the key "geojson".
        If no spatial data is provided, or if an error occurs, returns an error message.

    Example:
        buffer_features(distance=100, units="meters", map_state={...})

    Notes:
        - The `map_data` argument is supplied automatically by the system.
        - You (the AI) do not need to ask the user for this value.
        - The output is always returned in GeoJSON format (EPSG:4326).
        - This function is intended to be called by the AI assistant to perform geoprocessing operations.
    """
    # Prepare Geoflip API payload
    geoflip_payload = {
        "input_geojson": map_data,
        "output_format": "geojson",
        "output_crs": "EPSG:4326",  # Assuming output should stay in WGS84
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
            headers={"Authorization": f"Bearer {config.GEOFLIP_API_KEY}"}
        )

        # Handle response
        if response.status_code == 200:
            buffered_geojson = response.json()
            return {"geojson": buffered_geojson}
        else:
            return {
                "error": "Failed to buffer data via Geoflip API.",
                "status_code": response.status_code,
                "details": response.text
            }

    except requests.RequestException as e:
        return {"error": "Request to Geoflip API failed.", "details": str(e)}
