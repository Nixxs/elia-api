from elia_api.tools.registry import register_backend_function

@register_backend_function("get_weather")
def get_weather(latitude: float, longitude: float) -> dict[str, str | float]:
    """
    Get the weather for a given location.

    Args:
        latitude: Latitude of the location.
        longitude: Longitude of the location.

    Returns:
        String containing the weather information.
    """
    # Simulated API call (you can replace this with real API call)
    return "Sunny with a chance of rain 25 degrees Celsius"
