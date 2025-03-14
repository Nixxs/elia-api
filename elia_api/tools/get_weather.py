from elia_api.tools.registry import register_backend_function

@register_backend_function("get_weather")
def get_weather(latitude: float, longitude: float, map_data: str) -> dict[str, str | float]:
    """
    Get the weather for a given location.

    Args:
        latitude: Latitude of the location.
        longitude: Longitude of the location.
        map_data: Current map data this is provided automatically by the system

    Notes:
        - The `map_state` argument is supplied automatically by the system.
        - You (the AI) do not need to ask the user for this value.
        - The output is always returned in GeoJSON format (EPSG:4326).
        - This function is intended to be called by the AI assistant to perform geoprocessing operations.
    """
    # Simulated API call (you can replace this with real API call)
    return "Sunny with a chance of rain 25 degrees Celsius"
