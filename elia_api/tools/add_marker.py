
# this function represents a function that will be called on the front end to add a marker to the map
# as such it must return function arguments that correspond to the arguments of the function call on the front-end
def add_marker(latitude: float, longitude: float, label: str = "") -> dict[str, str | float]:
    """
    Add a marker to the map.

    Args:
        latitude: Latitude of the marker.
        longitude: Longitude of the marker.
        label: Optional label for the marker.

    Returns:
        A dictionary containing marker information.
    """
    return {
        "latitude": latitude,
        "longitude": longitude,
        "label": label
    }
