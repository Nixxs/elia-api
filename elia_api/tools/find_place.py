import requests
from elia_api.config import config
from elia_api.tools.registry import register_backend_function

@register_backend_function("find_place")
def find_place(query: str, location: str = None, radius: int = 50000):
    """
    Search for a place using Google Places API and return lat/lng.

    :param query: The name of the place to search.
    :param location: Optional lat,lng to bias search nearby.
    :param radius: Optional radius in meters for nearby search.
    :return: Dict with name, lat, lng or error message.
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
