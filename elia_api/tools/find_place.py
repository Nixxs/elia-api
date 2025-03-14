import requests
from elia_api.config import config
from elia_api.tools.registry import register_backend_function

@register_backend_function("find_place")
def find_place(query: str, map_data: str, location: str = None, radius: int = 50000):
    """
    Search for a place using Google Places API and return its coordinates.

    This function searches for a place based on the provided query and optionally biases 
    the search around a specific location and radius. The current map state is also provided
    for context, although it is not used directly in this function.

    Args:
        query: The name of the place to search (e.g., "Rottnest Island").
        map_data: [Provided automatically] The current map state, including viewport and data.
        location: Optional. A "lat,lng" string to bias the search near a specific location.
        radius: Optional. Search radius in meters (default is 50,000 meters).

    Returns:
        A dictionary containing:
            - name: The name of the found place.
            - lat: Latitude of the place.
            - lng: Longitude of the place.
            - address: Formatted address of the place (if available).
        
        If no place is found, returns:
            - error: Error message indicating no places were found.

    Example:
        find_place(query="Rottnest Island", map_data=..., location="-31.9505,115.8605", radius=50000)

    Notes:
        - The `map_data` argument is supplied automatically by the system.
        - You (the AI) do not need to ask the user for this value.
    """
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": config.GOOGLE_API_KEY,
    }

    if location:
        params["location"] = location
        params["radius"] = radius

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") == "OK" and data["results"]:
        place = data["results"][0]  # Take first result
        lat = place["geometry"]["location"]["lat"]
        lng = place["geometry"]["location"]["lng"]
        name = place["name"]
        address = place.get("formatted_address", "")
        return {"name": name, "lat": lat, "lng": lng, "address": address}
    else:
        return {"error": "No places found for query."}
